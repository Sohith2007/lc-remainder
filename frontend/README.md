# LeetReminder Frontend

React + TypeScript + Vite app for the LeetCode daily reminder project.

## Setup

1. Install dependencies with `npm install`.
2. Copy `.env.example` to `.env` and set `VITE_API_URL` to your backend URL.
3. Start the app with `npm run dev`.

## Scripts

- `npm run dev` starts the Vite dev server.
- `npm run build` creates a production build.
- `npm run lint` runs ESLint across the frontend source.

## Deployment Notes

- Keep `VITE_API_URL` pointed at the deployed backend.
- The local development default is `http://localhost:8000`.
- The production build output is generated in `dist/` and should not be committed.
