# Migration Plan: Django Monolith → React + Django REST

The phased plan used to migrate ExhibitGuide from a single server-rendered Django
application into a decoupled architecture: a Django REST API serving a separate React
single-page application.

Work was staged across ten phases so that each one delivered something verifiable before
the next began, and so the original application stayed deployable throughout. The two
versions live on separate branches and are deployed independently:

| | Version 1 — Original | Version 2 — Migrated |
|---|---|---|
| Branch | `main` | `react-and-rest-version` |
| Architecture | Django monolith, server-rendered templates | Django REST API + React SPA |
| Hosted | `https://exhibitguide.onrender.com` | `https://exhibitguide-react-frontend.onrender.com` |

**Status: migration complete.** All ten phases delivered and deployed. Verified in the
browser: ten exhibits render from the live API, deep links resolve, and `/qr/1001` opens
The Starry Night for an anonymous visitor with no sign-in.

This document is retained as a record of the migration approach and its sequencing.
`[x]` marks work completed; `[–]` marks work consciously descoped, with the reasoning given.

---

## Phase 0 — Safety & setup ✅
- [x] Working on the `react-and-rest-version` branch
- [x] Committed a clean starting point
- [x] Folder layout decided: `backend/` (Django) + `frontend/` (React)
- [x] Renamed Django project folder `exhibit_guide_pwa/` → `backend/`
- [x] README on `main` documents both versions for assessors

## Phase 1 — Add Django REST Framework ✅
- [x] `pip install djangorestframework` (installed 3.16.1)
- [x] Added `'rest_framework'` to `INSTALLED_APPS`
- [x] Pinned `djangorestframework==3.16.1` in `backend/requirements.txt`
- [x] `manage.py check` passes
- [x] Commit Phase 1 change (`563b11b`)

## Phase 2 — First API endpoint (Exhibit, end to end) ✅
> Start with **just `Exhibit`** to see the whole pattern work before repeating it.
- [x] Create `backend/exhibits/serializers.py` with an `ExhibitSerializer`
- [x] Add a DRF view (ViewSet) for exhibits in `backend/exhibits/views.py`
- [x] Wire up the URL `/api/exhibits/`
- [x] Visit `/api/exhibits/` and confirm real data comes out as JSON 🎉

## Phase 3 — Add the rest of the data to the API ✅
- [x] Serializer + view + URL for `Artist` → `/api/artists/`
- [x] Same for `Artwork` → `/api/artworks/`
- [x] Same for `Show` → `/api/shows/`
- [x] Decide how nested data appears (artist name vs. ID) — include both id + readable name
- [x] Handle image URLs (`exhibit_images/`) in the JSON — absolute URLs via request context

## Phase 4 — React frontend (separate app) ✅
- [x] Create the React app with Vite (`frontend/`)
- [x] Install React dependencies (`npm install`)
- [x] Confirm the blank app runs (`npm run dev` → http://localhost:5173)
- [x] Add an API-calling tool (`axios` or built-in `fetch`) — using built-in `fetch`

## Phase 5 — Connect React → Django ✅
- [x] `pip install django-cors-headers` and configure CORS
- [x] Fetch `/api/exhibits/` from React and log the result
- [x] Build the first real React screen: a list of exhibits from the API 🎉

## Phase 6 — Rebuild pages in React ✅
- [x] Exhibit list page (`ExhibitList.jsx`) — grid of cards linking to detail
- [x] Exhibit detail page (`ExhibitDetail.jsx`) — single exhibit, all fields, image fallback
- [–] Artists / Shows pages — **descoped.** Both are exposed through the API
      (`/api/artists/`, `/api/shows/`) and surfaced within exhibit pages and the dashboard's
      show filter, so dedicated browse pages added no user journey the assessment required.
      Artists and Shows remain fully manageable through the Django admin.
- [x] Add routing (React Router) — `/` list ↔ `/exhibits/:id` detail
- [x] Recreate styling (replaces the Bootstrap/crispy templates) — Figma design system applied; all 5 designs built: scan screen (1), detail page (2), interest modal (3), success banner (4), saved-exhibits dashboard (5, demo data). Interest capture is functional (POST /api/interest/ → Prospect). Dashboard uses demo data pending auth.

## Phase 7 — Login & security ✅
- [x] Choose auth method — JWT via `djangorestframework-simplejwt`
- [x] Build API login endpoints — register/login/refresh/me + per-user collection/saved/inquiries
- [x] Build a React login form that stores + sends the token — AuthContext (localStorage + authFetch), Login/Register pages
- [x] Protect endpoints that require login — IsAuthenticated on per-user endpoints; RequireAuth guards /dashboard
- [x] Real dashboard: per-user watchlist (SavedExhibit) + enquiries (GalleryInquiry); Save-to-watchlist on detail; logout

## Phase 8 — Interactive features (create / edit / delete) ✅
- [x] React form to add an exhibit (POST) — staff-only `/manage/new` (ExhibitForm)
- [x] Edit an exhibit (PUT/PATCH) — `/manage/:id/edit`
- [x] Delete an exhibit — from the `/manage` table (confirm dialog)
- [x] Handle image uploads from React to Django — multipart FormData → DRF; verified
- [x] Staff-only writes (IsStaffOrReadOnly); reads stay public; non-staff blocked from /manage

## Phase 9 — Cleanup & deploy ✅
- [x] Retire the old Django templates + crispy-forms that React replaced — full decouple: removed all server-rendered templates/views/urls/forms + crispy; Django is now a pure REST API + admin. (profile + password-reset also removed; both preserved on `main`.)
- [x] Prepare the repo for deployment — env-driven CORS, deployment runbook in README, `seed_data` guarded against setting a default password outside DEBUG
- [x] Push everything to GitHub (Render builds from there)
- [x] Create the Postgres database
- [x] **Create the backend Web Service** (Root Directory `backend`) — live at
      `https://exhibitguide-1.onrender.com`; `/api/` and `/admin/` both responding,
      correct branch confirmed (the `/api/exhibits/qr/` route exists only here)
- [x] Seed content — all 10 exhibits loaded
- [x] **Create the frontend Static Site** — live at
      `https://exhibitguide-react-frontend.onrender.com`; `VITE_API_URL` correctly compiled
      into the bundle, rewrite `/*` → `/index.html` confirmed working on deep links
- [x] **Connect the two** — `DJANGO_CORS_ALLOWED_ORIGINS` + `FRONTEND_URL` set on the
      backend; verified the API returns `access-control-allow-origin` for the frontend
- [x] Verify the deployed stack — exhibit list renders 10 works from the live API;
      `/qr/1001` opens The Starry Night for an anonymous visitor with Express Interest
- [x] Add the two hosted URLs to this branch's README
- [x] Generate QR codes against the production frontend URL — 10 codes produced as PNGs
      plus a print-ready PDF; all decoded and verified to resolve live (still to print)
- [x] Add the Version 2 hosted URL to `main`'s README — commit `fbb30e1`, pushed; the
      comparison table and the Version 2 section both carry the frontend and backend URLs,
      and the status now reads "Complete and deployed"
- [x] Production hardening: SMTP configured on the Render backend service; settings are
      env-driven (console backend locally, SMTP in production, TLS on, guard against
      setting both TLS and SSL). Password-reset send failures are now caught and logged
      rather than returning 500 — which previously leaked which addresses had accounts
      (commit `f4dd569`, covered by 3 regression tests).
- [x] Decide on merging `react-and-rest-version` — **decision: do not merge.** The two
      versions are deliberately parallel, not a feature branch awaiting integration. They
      are deployed separately and assessed independently, and the migration removed the
      templates, `exhibit_guide_pwa/` layout and crispy-forms that `main` still serves.
      Merging would break the live original application and collapse the two-version
      structure the assessor documentation describes. Both branches remain the deliverable.

---

### Local development reminder (two terminals)
```bash
# Terminal 1 — Django REST API (on SQLite locally)
cd backend
python manage.py runserver        # http://localhost:8000

# Terminal 2 — React frontend
cd frontend
npm run dev                       # http://localhost:5173
```
