# LeetCode Daily Reminder

Small FastAPI app that shows the current daily LeetCode problem and sends a daily reminder email.
Recipient emails are collected from a frontend form and persisted in Supabase.

The backend live-fetches LeetCode data on every request and falls back to the last cached problem only if the fetch fails.

## Setup

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Create a Supabase project and copy:
	 - `SUPABASE_URL`
	 - `SUPABASE_KEY` (service role key for backend server use)
4. In Supabase SQL editor, create tables:

```sql
create table if not exists daily_problem (
	id bigint primary key,
	title text not null,
	slug text not null,
	url text not null,
	difficulty text not null,
	description text not null,
	fetched_at timestamptz not null,
	acceptance_rate double precision,
	topic_tags jsonb not null default '[]'::jsonb
);

create table if not exists delivery_log (
	sent_date date primary key,
	sent_at timestamptz not null
);

create table if not exists recipients (
	email text primary key,
	created_at timestamptz not null default now()
);
```

5. Fill in `.env` with the required runtime values. The app loads `.env` automatically at startup.

## Environment Variables

Required:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_SENDER`

Optional:

- `SMTP_HOST` defaults to `smtp.gmail.com`
- `SMTP_PORT` defaults to `587`
- `REMINDER_HOUR` defaults to `8`
- `REMINDER_MINUTE` defaults to `0`
- `TIMEZONE` defaults to `UTC`
- `LEETCODE_DAILY_URL` defaults to the LeetCode daily problem page
- `CORS_ORIGINS` defaults to `http://localhost:5173` and `http://localhost:3000`

If you deploy for India, set `TIMEZONE=Asia/Kolkata` and adjust the reminder hour/minute to your preferred local send time.

## Run

```bash
uvicorn app.main:app --reload
```

The frontend should point at the backend API on `http://localhost:8000` during local development.

## Refresh manually

Send a POST request to `/refresh` after SMTP is configured.

## Add recipients

Use the form on `/` to add recipient emails. The scheduler sends to all saved recipients daily.

## Deployment Notes

- Set all production environment variables in your hosting provider before starting the app.
- Keep `SUPABASE_KEY` private; use the service-role key only on the backend.
- Ensure CORS allows the deployed frontend origin.