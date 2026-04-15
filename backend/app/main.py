from __future__ import annotations

import asyncio
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .config import load_settings, validate_email_settings
from .emailing import build_email, send_email
from .leetcode import fetch_daily_problem
from .scheduler import refresh_and_send
from .storage import Storage


settings = load_settings()
storage = Storage(settings.supabase_url, settings.supabase_key)
templates = Jinja2Templates(directory="app/templates")
app = FastAPI(title=settings.app_name)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def collect_recipients() -> list[str]:
    try:
        stored = storage.list_recipients()
    except RuntimeError:
        stored = []
    recipients = [value.strip().lower() for value in stored if value.strip()]
    if settings.reminder_recipient:
        recipients.append(settings.reminder_recipient.strip().lower())
    return sorted(set(recipients))


async def execute_refresh() -> str:
    missing = validate_email_settings(settings)
    if missing:
        return f"missing config: {', '.join(missing)}"
    return await refresh_and_send(
        storage=storage,
        source_url=settings.leetcode_daily_url,
        sender=settings.smtp_sender,
        recipients=collect_recipients(),
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
    )


async def send_immediate_to_recipient(recipient: str) -> str:
    problem = storage.load_daily_problem()
    if problem is None:
        problem = await fetch_daily_problem(settings.leetcode_daily_url)
        storage.save_daily_problem(problem)

    message = build_email(problem, settings.smtp_sender, recipient)
    send_email(
        message,
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_username,
        settings.smtp_password,
    )
    return "sent-immediate"


async def get_live_problem() -> object | None:
    """Fetch latest daily problem on every request; fall back to cached data if needed."""
    try:
        problem = await fetch_daily_problem(settings.leetcode_daily_url)
        try:
            storage.save_daily_problem(problem)
        except Exception:
            # Live fetch is source of truth; persistence failure should not block response.
            pass
        return problem
    except Exception:
        try:
            return storage.load_daily_problem()
        except RuntimeError:
            return None


@app.get("/api/home")
async def api_home():
    """
    Returns daily problem data for the landing page.
    Fetches problem from storage; if missing, returns empty problem.
    """
    problem = await get_live_problem()
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "daily_problem": {
                "title": problem.title,
                "slug": problem.slug,
                "url": problem.url,
                "difficulty": problem.difficulty,
                "description": problem.description,
                "fetched_at": problem.fetched_at.isoformat(),
                "acceptance_rate": problem.acceptance_rate,
                "topic_tags": problem.topic_tags or [],
            } if problem else None
        }
    )


@app.get("/api/problem")
async def api_problem():
    """
    Returns problem details page data with completion status and timer info.
    """
    problem = await get_live_problem()

    if problem is None:
        return JSONResponse(
            status_code=200,
            content={"status": "success", "daily_problem": None, "timer": None}
        )
    
    # Calculate timer: next occurrence of reminder time
    now = datetime.now(ZoneInfo(settings.timezone))
    next_reminder = now.replace(
        hour=settings.reminder_hour,
        minute=settings.reminder_minute,
        second=0,
        microsecond=0
    )
    
    # If we've already passed the reminder time today, set for tomorrow
    if next_reminder <= now:
        next_reminder += timedelta(days=1)
    
    time_until_expires = next_reminder - now
    hours, remainder = divmod(int(time_until_expires.total_seconds()), 3600)
    minutes = remainder // 60
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "daily_problem": {
                "title": problem.title,
                "slug": problem.slug,
                "url": problem.url,
                "difficulty": problem.difficulty,
                "description": problem.description,
                "fetched_at": problem.fetched_at.isoformat(),
                "acceptance_rate": problem.acceptance_rate,
                "topic_tags": problem.topic_tags or [],
            } if problem else None,
            "timer": {
                "expires_at": next_reminder.isoformat(),
                "hours_remaining": hours,
                "minutes_remaining": minutes,
                "display_text": f"Expires in {hours}h {minutes}m",
            } if problem else None
        }
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        problem = storage.load_daily_problem()
    except RuntimeError:
        problem = None
    try:
        recipients = storage.list_recipients()
    except RuntimeError:
        recipients = []
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "problem": problem,
            "settings": settings,
            "recipients": recipients,
            "status": request.query_params.get("status", ""),
            "error": request.query_params.get("error", ""),
        },
    )


@app.post("/api/recipients", status_code=201)
async def add_recipient(request: Request):
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON body"}
        )
    
    if not email:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Email is required"}
        )
    
    if not EMAIL_PATTERN.match(email):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid email format"}
        )

    try:
        inserted = storage.add_recipient(email)
    except RuntimeError as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Database configuration error"}
        )
    
    if not inserted:
        return JSONResponse(
            status_code=409,
            content={"status": "error", "message": "Email already subscribed"}
        )
    
    # Try to send immediate email
    missing = validate_email_settings(settings)
    if missing:
        return JSONResponse(
            status_code=201,
            content={"status": "success", "message": "Subscribed but email not sent", "email": email}
        )
    
    try:
        await send_immediate_to_recipient(email)
        return JSONResponse(
            status_code=201,
            content={"status": "success", "message": "Subscribed and email sent", "email": email}
        )
    except Exception as e:
        return JSONResponse(
            status_code=201,
            content={"status": "success", "message": "Subscribed but email send failed", "email": email}
        )


@app.post("/recipients")
async def add_recipient_form(email: str = Form(...)):
    """Legacy endpoint for form-based submission (Jinja templates)"""
    value = email.strip().lower()
    if not EMAIL_PATTERN.match(value):
        return RedirectResponse(url="/?error=invalid-email", status_code=303)

    try:
        inserted = storage.add_recipient(value)
    except RuntimeError:
        return RedirectResponse(url="/?error=supabase-not-configured", status_code=303)
    if inserted:
        missing = validate_email_settings(settings)
        if missing:
            return RedirectResponse(url="/?status=recipient-added&error=missing-email-config", status_code=303)
        try:
            await send_immediate_to_recipient(value)
            return RedirectResponse(url="/?status=recipient-added-and-sent", status_code=303)
        except Exception:
            return RedirectResponse(url="/?status=recipient-added&error=immediate-send-failed", status_code=303)
    return RedirectResponse(url="/?status=recipient-exists", status_code=303)


@app.post("/api/refresh")
async def api_refresh():
    result = await execute_refresh()
    if result.startswith("missing config"):
        missing = validate_email_settings(settings)
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Email configuration missing", "missing": missing}
        )
    
    # Parse result to extract sent count
    sent_count = 0
    if result.startswith("sent:"):
        try:
            sent_count = int(result.split(":")[1])
            return JSONResponse(
                status_code=200,
                content={"status": "success", "message": f"Sent to {sent_count} recipients", "sent_count": sent_count}
            )
        except (IndexError, ValueError):
            pass
    
    if result == "already-sent":
        return JSONResponse(
            status_code=200,
            content={"status": "already_sent", "message": "Problem already sent today", "sent_count": 0}
        )
    
    if result == "no-recipients":
        return JSONResponse(
            status_code=200,
            content={"status": "no_recipients", "message": "No recipients configured", "sent_count": 0}
        )
    
    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": result, "sent_count": 0}
    )


@app.post("/refresh", response_class=JSONResponse)
async def refresh():
    """Legacy endpoint that returns JSON response (for backward compatibility)"""
    result = await execute_refresh()
    if result.startswith("missing config"):
        missing = validate_email_settings(settings)
        raise HTTPException(status_code=400, detail={"missing": missing})
    return {"status": result}


def run_refresh() -> str:
    return asyncio.run(execute_refresh())


@app.on_event("startup")
async def start_scheduler() -> None:
    scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.timezone))
    scheduler.add_job(
        execute_refresh,
        CronTrigger(hour=settings.reminder_hour, minute=settings.reminder_minute, timezone=ZoneInfo(settings.timezone)),
        id="daily-leetcode-reminder",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()
    app.state.scheduler = scheduler


@app.on_event("shutdown")
async def stop_scheduler() -> None:
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler is not None:
        scheduler.shutdown(wait=False)