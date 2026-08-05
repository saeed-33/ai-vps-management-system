# Admin Panel

Next.js admin panel for the AI VPS Management System.

## Current Scope

This is the phase 10 foundation. It provides:

- App Router setup.
- TypeScript.
- Admin shell layout.
- Sidebar navigation.
- Dashboard foundation.
- API status page.
- Bootstrap login page.
- Users foundation page.
- Servers foundation page.
- Monitoring profiles foundation page.
- Specialist agents foundation page.
- Shared API client.

It does not yet provide full session persistence, CRUD, or agent chat.

## Install

```bash
npm install --no-audit --no-fund --ignore-scripts
```

## Run

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Environment

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Login

Open:

```text
http://127.0.0.1:3000/login
```

Use the Backend bootstrap admin credentials:

```text
Email: BOOTSTRAP_ADMIN_EMAIL
Password: original password used to generate BOOTSTRAP_ADMIN_PASSWORD_HASH
```

The access token is stored locally in the browser for the foundation pages.
