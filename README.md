# ExhibitGuide

ExhibitGuide is a decoupled web app:
- Frontend: React + Vite (`frontend/`)
- Backend: Django REST API + Django admin (`backend/`)

This README is optimized for assessment:
1. quick access to hosted and local environments,
2. clear test paths for core functionality,
3. concise evidence that maps to assessment requirements.

## 1) Assessor Start Here (Production)

Frontend (start here):
- https://exhibitguide-react-frontend.onrender.com/

Backend (API + admin only):
- https://exhibitguide-1.onrender.com/
- Admin: https://exhibitguide-1.onrender.com/admin/

Notes:
- Start from the frontend root URL.
- The backend URL does not provide end-user pages; it serves API routes and admin only.
- On Render free tier, first request after idle can take 30-60 seconds.

### Two versions, two branches — and why they are not merged

This repository holds **two complete, independently deployed versions** of ExhibitGuide.
This branch is Version 2.

| | Version 1 — Original | Version 2 — this branch |
|---|---|---|
| Branch | `main` | `react-and-rest-version` |
| Tag | `v1.0` | `v2.0` |
| Architecture | Django monolith, server-rendered templates | Django REST API + React SPA |
| Django folder | `exhibit_guide_pwa/` | `backend/` |
| Hosted | https://exhibitguide.onrender.com | https://exhibitguide-react-frontend.onrender.com |

**Why two versions exist.** Version 1 delivered the product as a conventional Django
application and validated the core journey. Version 2 migrated that same product to a
decoupled architecture. The migration itself is part of what is being submitted, so the
starting point had to remain intact and inspectable rather than being overwritten — an
assessor can compare the two directly, and the ten-phase route between them is recorded in
`DJANGO_TO_REACT_MIGRATION_PLAN.md`.

**Why they are deliberately not merged.** These are parallel deliverables, not a feature
branch awaiting integration:

1. **A merge would break the live Version 1 site.** `main` auto-deploys to Render. Version 2
   deleted the templates, template views, forms and `crispy_forms` dependency that Version 1
   serves, and renamed `exhibit_guide_pwa/` to `backend/`. Merging would delete the running
   application's code.
2. **The two are assessed independently.** Both are documented as separately gradable.
   Collapsing them into one branch would destroy that structure and leave only the later
   architecture as evidence.
3. **Neither supersedes the other.** A merge asserts that one version replaces another.
   Here both are finished products that happen to share an origin, and branches are the
   correct tool for maintaining parallel lines of work.
4. **The submitted state is pinned.** `v1.0` and `v2.0` tag each branch, so the assessed
   version of each remains retrievable regardless of later development.

The decision is also recorded in `DJANGO_TO_REACT_MIGRATION_PLAN.md` alongside the work it
concerns.

## 2) Fast Production Verification Flow

### Visitor flow (public to authenticated)
1. Start at the frontend root route (`/`) and confirm the exhibit list renders.
2. On that same page, use the baked-in QR option and scan a code (or open `/qr/1001`) and confirm it resolves to exhibit detail.
3. From the scanned exhibit detail page, submit **Express Interest in Purchasing**.
4. Register at `/register` and confirm redirect to `/dashboard`.
5. Confirm the interested work appears in dashboard scans/collections.
6. Submit **Enquire** from dashboard and confirm success + status update.
7. Open `/profile` and confirm profile data can be updated.
8. (Optional) Return to the root route (`/`), click an exhibit card, and confirm it opens the exhibit detail page (`/exhibits/<id>`).
9. Logout and confirm `/dashboard` redirects to `/login`.

### Staff/admin flow
1. Open backend admin and sign in as staff.
2. Create/edit `Artist`, `Artwork`, `Show`, `Exhibit`.
3. Confirm `Exhibit` gets an auto `qr_identifier` on save.
4. Re-open the frontend QR route for that exhibit and confirm resolution.
5. Confirm inquiry/prospect records are visible in admin.

## 3) Local Setup (Quick Repro)

### Prerequisites
- Python 3.12+
- Node.js 20+
- npm

### Backend setup
```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
```

Run with SQLite (default/easiest):
```bash
export DJANGO_DEBUG=true
unset DATABASE_URL
python manage.py migrate
python manage.py runserver 8000
```

### Frontend setup
```bash
cd frontend
npm ci
VITE_API_URL=http://127.0.0.1:8000 npm run dev
```

Open:
- frontend: http://127.0.0.1:5173/
- backend admin/API: http://127.0.0.1:8000/

## 4) Database Modes

Backend DB selection is environment-driven in `backend/exhibit_guide_pwa/settings.py`.

- Debug/local (`DJANGO_DEBUG=true`):
  - uses SQLite (`backend/db.sqlite3`) for local development.
- Production (`DJANGO_DEBUG=false`):
  - uses `DATABASE_URL` (preferred),
  - or `DJANGO_PRODUCTION_DATABASE_URL`.

## 5) Core Routes For Assessment

### Frontend routes (React)
Core:
- `/`
- `/exhibits/<id>`
- `/qr/<qr_identifier>`
- `/register`
- `/login`
- `/dashboard`
- `/profile`

Secondary/support:
- `/password-reset`
- `/reset-password`
- `/scan`
- `/scan/<id>`
- `/manage`
- `/manage/new`
- `/manage/<id>/edit`

### Backend routes (Django API + admin)
Core:
- `/api/exhibits/`
- `/api/exhibits/qr/<qr_identifier>/`
- `/api/interest/`
- `/api/auth/register/`
- `/api/auth/login/`
- `/api/auth/profile/`
- `/api/collection/`
- `/api/inquiries/`
- `/admin/`

Secondary/support:
- `/api/auth/refresh/`
- `/api/auth/me/`
- `/api/auth/password-reset/`
- `/api/auth/password-reset/confirm/`
- `/api/saved/`
- `/api/artists/`
- `/api/artworks/`
- `/api/shows/`
- `/api/external/exchange-rates/`
- `/api/external/museum-search/`

## 6) QR Entry + Staff QR Generator

Runtime QR entry route:
- Printed code target: `https://<frontend>/qr/<qr_identifier>`
- API resolver: `GET /api/exhibits/qr/<qr_identifier>/`
- Identifier source: `Exhibit.qr_identifier` (`id + 1000`, generated in model save)

Staff QR print utility:
- `frontend/public/exhibit-qr-codes.html`
- Hosted path: `<frontend>/exhibit-qr-codes.html`

## 7) Automated Testing (Current Build)

Most recent local run (SQLite override):
- Total tests: **17**
- Result: **all passing**

Command used:
```bash
cd backend
DJANGO_DEBUG=1 DJANGO_DB_SSL_REQUIRE=0 DJANGO_LOCAL_DATABASE_URL=sqlite:////tmp/exhibitguide_test.sqlite3 /absolute/path/to/venv/bin/python manage.py test
```

Coverage focus:
- `backend/users/tests_api.py`: profile, password reset, inquiries, collection status transitions
- `backend/exhibits/tests.py`: exhibit model behavior including QR identifier generation
- `backend/users/tests.py`: model compatibility behavior
- `backend/exhibits/tests_external_api.py`: exchange-rate and museum API proxy integration

## 8) Accessibility Compliance (WCAG 2.1 A)

This build is aligned to **WCAG 2.1 Level A** for core user journeys.

Implemented accessibility controls include:
- Keyboard-operable dialogs with focus trap, Escape-to-close, and focus return after close.
- Programmatic dialog semantics (`role="dialog"`, `aria-modal`, labelled titles).
- Form labels and accessible error messaging (`aria-invalid`, `aria-describedby`, `role="alert"`).
- Live status announcements for non-blocking updates (`role="status"`, `aria-live="polite"`).
- Tab interface semantics on exhibit content (`role="tablist"`, `role="tab"`, `role="tabpanel"`).
- Consistent visible focus indicators via `:focus-visible` across buttons, links, inputs, and controls.
- Reduced-motion fallback (`prefers-reduced-motion`) for users with motion sensitivity.
- Improved alternative text for exhibit imagery (title + artist where available).

Primary files updated for accessibility:
- `frontend/src/InterestModal.jsx`, `frontend/src/InterestModal.css`
- `frontend/src/Dashboard.jsx`, `frontend/src/Dashboard.css`
- `frontend/src/ExhibitDetail.jsx`, `frontend/src/ExhibitDetail.css`
- `frontend/src/LoginPage.jsx`, `frontend/src/RegisterPage.jsx`
- `frontend/src/PasswordResetRequestPage.jsx`, `frontend/src/PasswordResetConfirmPage.jsx`
- `frontend/src/ExhibitImage.jsx`, `frontend/src/index.css`, `frontend/src/ScanScreen.css`

Validation status:
- Frontend build passes (`npm run build`).
- Backend tests pass (17/17) with local SQLite override.

## 9) Assessment Mapping (Requirement Status)

### A) Frameworks assessment (Django + DB)

| Requirement | Status | Current evidence |
|---|---|---|
| Django concepts applied | Met | Django apps, DRF views/serializers, admin, permissions |
| Database integration in Django | Met | ORM models/relations/migrations, environment-based DB switching |
| Authentication + authorisation | Met | JWT auth routes, `IsAuthenticated`, `IsStaffOrReadOnly`, protected frontend routes |
| Clean code structure (templates/styling/JS) | Met | Decoupled React frontend + Django API, organized route/components/apps |
| Hosted Django app fully functional and accessible | Met | Hosted functional flow is verifiable and WCAG 2.1 A accessibility controls are implemented in current frontend build |

### B) Final assignment guide

| Requirement | Status | Current evidence |
|---|---|---|
| Front-end concepts | Met | React SPA routing, stateful auth flow, responsive UI |
| Back-end concepts | Met | DRF endpoints, serializers, model-backed workflows |
| Secure web application | Met | Django auth, password validation, protected routes, CSRF/security settings |
| Clear and concise documentation | Met (with scope note) | README is now assessor-first and implementation-linked |
| Hosted app fully functional and accessible | Met | Functional hosted checks are documented and WCAG 2.1 A accessibility controls are implemented in current frontend build |

Feature checklist status:

| Feature expectation | Status | Notes |
|---|---|---|
| User registration and login | Met | Implemented and tested |
| Dashboard after login | Met | Implemented and tested |
| Idea-specific feature set | Met | QR-first exhibit flow, watchlist/enquiry, profile enrichment |
| Responsive design | Met | Implemented in frontend CSS/layouts |
| External API integration | Met | Third-party integrations implemented via Frankfurter exchange-rate API and The Met Collection API, surfaced in exhibit detail |
| Automated testing | Met | 17 passing tests (current run) |
| Version control workflow | Partially met | Git history exists; assessor validates quality from commits/branch usage |
| Deployment | Partially met | Render deployment is live; assessor validates uptime/accessibility at marking time |

## 10) Deployment Snapshot (Render)

Current architecture:
- Web Service: Django API/admin (`backend/`)
- Static Site: React frontend (`frontend/`)
- Managed Postgres

Critical environment variables:
- Backend:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=false`
  - `DATABASE_URL`
  - `DJANGO_ALLOWED_HOSTS`
  - `DJANGO_CORS_ALLOWED_ORIGINS`
  - `DJANGO_CSRF_TRUSTED_ORIGINS`
  - `FRONTEND_URL`
  - SMTP vars for password reset email:
    - `DJANGO_EMAIL_BACKEND`
    - `DJANGO_EMAIL_HOST`
    - `DJANGO_EMAIL_PORT`
    - `DJANGO_EMAIL_HOST_USER`
    - `DJANGO_EMAIL_HOST_PASSWORD`
    - `DJANGO_EMAIL_USE_TLS`
    - `DJANGO_EMAIL_USE_SSL`
    - `DJANGO_DEFAULT_FROM_EMAIL`
- Frontend:
  - `VITE_API_URL` (build-time)

Required frontend rewrite rule:
- `/*` -> `/index.html` (Rewrite)

## 11) Evidence Index (Key Files)

- Frontend routes and guards: `frontend/src/App.jsx`
- Auth context/token handling: `frontend/src/AuthContext.jsx`
- Exhibit/API fetch UI: `frontend/src/ExhibitList.jsx`, `frontend/src/ExhibitDetail.jsx`, `frontend/src/Dashboard.jsx`
- API root routing: `backend/exhibit_guide_pwa/urls.py`
- Exhibit/public API routes: `backend/exhibits/api_urls.py`
- External API proxy views: `backend/exhibits/views.py` (`ExchangeRatesView`, `MuseumSearchView`)
- Auth/user API routes: `backend/users/api_urls.py`
- Auth/profile/inquiry views: `backend/users/api_views.py`
- Exhibit and QR model logic: `backend/exhibits/models.py`
- User activity models: `backend/users/models.py`
- Test evidence: `backend/users/tests_api.py`, `backend/exhibits/tests.py`, `backend/users/tests.py`
- External integration tests: `backend/exhibits/tests_external_api.py`
- Deployment/runtime dependencies: `backend/requirements.txt`, `backend/runtime.txt`

## 12) Current Gaps (Explicit)

1. No critical functional gaps for current assessment scope.

