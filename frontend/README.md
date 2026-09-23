# HireSense frontend

Next.js (App Router, TypeScript) app implementing the Phase 1 core loop UI:
login/register, JD list/create, resume upload, the ranked candidate list,
and the manual status-change action.

## Node version

This project needs **Node ≥20** (Tailwind v4's native binary and Next.js 16
both require it). Check with `node -v`. If you're on an older Node and
don't want to change your global version, install it alongside via
Homebrew without touching your existing `node`:

```bash
brew install node@20   # installed keg-only, does not relink your default node
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"   # for this shell/session
```

(`.nvmrc` in this directory documents the pinned version for tools that read it.)

## Setup

```bash
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE_URL, defaults to http://localhost:8000
```

Requires the backend running and reachable at that URL, with CORS enabled
for this app's origin (`FRONTEND_ORIGIN` in `backend/.env`, defaults to
`http://localhost:3000`) — see `backend/README.md`.

## Run

```bash
npm run dev
```

## Build / lint

```bash
npm run build
npm run lint
```

## Architecture notes

- **Auth is SPA-style, client-side.** The browser calls the FastAPI backend
  directly with `fetch` (`lib/api.ts`); the access token is attached as an
  `Authorization: Bearer` header, both tokens are persisted in
  `localStorage` (`lib/auth-storage.ts`) so a reload survives. A single
  `apiFetch` wrapper retries once through a silent refresh on a `401`, then
  hard-redirects to `/login` if that also fails.
- **`AuthGuard`** (`components/auth/auth-guard.tsx`), applied in
  `app/(app)/layout.tsx`, is the only route-protection mechanism -- there's
  no server-side session check, consistent with the SPA-style choice.
- **Polling, not websockets**, picks up the async evaluation result: the
  ranked-candidates and candidate-detail queries (`app/(app)/job-descriptions/
  [jdId]/page.tsx`, `app/(app)/candidates/[candidateId]/page.tsx`) set
  `refetchInterval` to 3s *only* while a candidate's `processing_status` is
  still `pending`/`parsing`/`evaluating`, and stop once the worker finishes.
- **shadcn/ui here is `@base-ui/react`-based**, not Radix -- components that
  render another element as themselves use the `render` prop
  (`<Button render={<Link href="..." />}>`), not `asChild`.
- **TanStack Table v9** (`components/candidates/candidate-ranking-table.tsx`)
  uses the v9 `useTable`/`tableFeatures` API, not v8's `useReactTable`. The
  ranking table itself doesn't register a sorting feature -- the backend
  already returns candidates sorted by score, and Phase 1 doesn't need
  client-side re-sorting.
