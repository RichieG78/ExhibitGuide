# ExhibitGuide

## Project Summary
ExhibitGuide is a Django web application for gallery and exhibit experiences.

It provides:
- a public exhibit flow based on QR links,
- user registration and login,
- a user dashboard for saved works and enquiries,
- an admin area used as a lightweight CMS for artists, artworks, shows, exhibits, and enquiry follow-up.

This README is written as a technical assessment and handover guide. It maps implementation evidence to the published requirements and rubric language.

## Assessor Quick Start (Recommended Test Order)

> ### ▶ Start here
> **`https://exhibitguide-react-frontend.onrender.com/start.html`**
>
> This page shows a scannable QR code for every artwork, with instructions. Point a phone
> camera at any code to enter the application exactly as a gallery visitor would — no app
> and no account required. Without a phone, selecting a code opens the same page in the
> browser.

This section is designed for first-time assessors.

If the hosted app is unavailable, run locally using the Local Setup section and then follow the same steps below.

### Persona 1: Visitor Flow (Public -> Enquiry -> Dashboard)
Goal: verify the end-to-end visitor journey from scan to enquiry and saved exhibit management.

1. Open `<frontend>/start.html` and scan any code with a phone camera (or select one to
   open it in the browser). See **QR Code Entry Flow** below.
2. Confirm the QR route opens that work's public exhibit page at `/qr/<qr_identifier>`
   — no sign-in required.
3. On the exhibit page, select **Express Interest in Purchasing** and submit an email
   address. This captures a lead anonymously; confirm the success banner appears.
4. Create a new account at `/register/`.
5. After registration, confirm redirect to `/dashboard` (empty for a new account).
6. Return to an exhibit and select **Save to watchlist**, then reopen `/dashboard`
   and confirm the work appears with status `watching`.
7. Select **Enquire** on that dashboard card and confirm the status changes to `enquired`.
8. Use the dashboard filters (`All`, `Watching`, `Enquired`) to verify state changes.
9. Open `/profile/` and confirm collector details can be reviewed and updated.
10. Log out from the dashboard, then confirm `/dashboard` redirects to `/login`.

What this flow checks:
- QR-first public entry route,
- registration/login,
- authenticated dashboard behavior,
- enquiry creation,
- profile update path.

### Persona 2: Gallery Owner Flow (Admin CMS + Prospect Monitoring)
Goal: verify admin can manage content and monitor visitor interest.

1. Log in to `/admin/` with a staff/superuser account.
2. Create or update an `Artist`.
3. Create or update an `Artwork` linked to that artist.
4. Create or update a `Show`.
5. Create an `Exhibit` linked to the show and artwork.
6. Confirm the exhibit generates a `qr_identifier` after save.
7. Open the public preview link from exhibit admin and verify it resolves correctly.
8. Complete the visitor flow above to create at least one enquiry.
9. Return to `/admin/` and verify monitoring data: `GalleryInquiry` contains enquiry content/timestamps, `Prospect` contains contact details/callback preference, exhibit admin inlines show related enquiries/prospects, and filters work by show/exhibit/date.

What this flow checks:
- CMS CRUD for artists, artworks, shows, exhibits,
- relationship linking across schema,
- enquiry/prospect visibility for gallery follow-up.

### Minimal Route Checklist For Assessment

Frontend routes (React app):

| Route | Access | Purpose |
|-------|--------|---------|
| `/` | Public | Exhibit list |
| `/exhibits/<id>` | Public | Exhibit detail |
| `/qr/<qr_identifier>` | Public | QR code entry point (scan destination) |
| `/scan`, `/scan/<id>` | Public | In-gallery scan simulation screen |
| `/register`, `/login` | Public | Account creation and sign-in |
| `/password-reset`, `/reset-password` | Public | Password reset request and confirmation |
| `/dashboard` | Authenticated | Saved exhibits (watchlist and enquiries) |
| `/profile` | Authenticated | Collector profile management |
| `/manage`, `/manage/new`, `/manage/<id>/edit` | Staff only | Exhibit create/edit/delete |

Backend routes (Django API + admin):

| Route | Access | Purpose |
|-------|--------|---------|
| `/api/exhibits/` | Public read, staff write | Exhibit list and CRUD |
| `/api/exhibits/qr/<qr_identifier>/` | Public | QR lookup by printed identifier |
| `/api/artists/`, `/api/artworks/`, `/api/shows/` | Public | Supporting read endpoints |
| `/api/interest/` | Public | Anonymous lead capture |
| `/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/` | Public | JWT authentication |
| `/api/auth/me/`, `/api/auth/profile/` | Authenticated | Current user and profile |
| `/api/collection/`, `/api/saved/`, `/api/inquiries/` | Authenticated | Per-user collector data |
| `/admin/` | Staff | Django admin CMS |

## Live Application and Repository
- Repository: this project repository (branch `react-and-rest-version`)
- Frontend (React) hosted URL: `https://exhibitguide-react-frontend.onrender.com`
- Backend (Django REST API + admin) hosted URL: `https://exhibitguide-1.onrender.com`
- Start here: open the **frontend** URL. The backend URL serves the REST API and the Django
  admin only; it has no browsable pages of its own.
- This version deploys as two Render services; see **Deployment Runbook (Render)** below.
- The original single-service Django application is deployed separately from `main` at
  `https://exhibitguide.onrender.com`.
- Note: hosted availability depends on deployment state and hosting uptime. On Render's
  free tier the backend sleeps when idle, so the first request may take 30–60 seconds.

## Hosted Accessibility Evidence (Run-Through)
Use this sequence to verify the hosted app is functional and accessible.

1. Open the hosted frontend root and confirm the exhibit list renders (HTTP 200).
2. Open an exhibit from the list and confirm the detail page renders.
3. Open `/qr/<qr_identifier>` using a seeded identifier (for example `/qr/1001`) and
   confirm the exhibit page renders without signing in.
4. Open `/register`, create an account, and confirm redirect to `/dashboard`.
5. Log out and sign in again via `/login` to verify the JWT auth flow.
6. Open `/profile` while signed in and confirm profile details load.
7. Save an exhibit, then enquire from the dashboard and confirm the status updates.
8. Open `<backend>/admin/` with staff credentials and confirm admin index access.

Expected outcome:
- public routes are available without authentication,
- authenticated routes enforce login,
- admin route enforces staff authorization,
- core visitor, collector, and admin workflows are operational.

## QR Code Entry Flow

The QR journey is the product's primary public entry point: a visitor standing in the
gallery scans a code beside a work and immediately reaches that work's page — no app
install and no account required.

### How it works

| Step | Detail |
|------|--------|
| Printed code encodes | `https://<frontend>/qr/<qr_identifier>` |
| Frontend route | `/qr/:qrId` renders the public exhibit detail page |
| API lookup | `GET /api/exhibits/qr/<qr_identifier>/` (public, unauthenticated) |
| Identifier source | `Exhibit.qr_identifier`, generated automatically in `Exhibit.save()` once a record is first persisted (database id + 1000) |

`qr_identifier` is deliberately separate from the database primary key: printed codes stay
stable and readable, and internal record ids are not exposed on gallery signage.

Anonymous visitors can read the full exhibit page, play the audio guide, and submit
**Express Interest in Purchasing**, which records a `Prospect` lead (with dwell time)
without an account. Member-only actions such as **Save to watchlist** appear only when
signed in.

### Two QR pages, for two audiences

| Page | For | Purpose |
|------|-----|---------|
| `<frontend>/start.html` | **Visitors and assessors** | The entry point. Shows every code with instructions; codes are generated automatically on load, and each is selectable for browser-only testing. |
| `<frontend>/exhibit-qr-codes.html` | Gallery staff | Print-oriented generator with configurable site and API addresses, for producing wall labels. |

### Generating and printing codes

The generator is served by the frontend at `<frontend>/exhibit-qr-codes.html`
(source: `frontend/public/exhibit-qr-codes.html`). It reads live exhibit data from the
API, so every exhibit with a `qr_identifier` — including newly created ones — receives a
code labelled with its artwork title and artist.

1. Open `<frontend>/exhibit-qr-codes.html`.
2. Enter the **frontend site URL** (encoded into the codes) and the **API URL**
   (queried for exhibit data). Both are remembered in the browser.
3. Select **Generate codes**, then **Print**. The print stylesheet lays the codes out
   four to a row and hides the on-screen controls.

The page must be opened over `http(s)` rather than as a local `file://` document: a
`file://` page sends a `null` origin, which the API's CORS policy rejects.

> **Printed codes are permanent.** Set the final production frontend URL before printing,
> and scan one code with a phone to confirm it resolves. Changing the site URL afterwards
> invalidates every printed code.

## Documentation Map (Analysis to Design to Implementation to Test)
- Project brief and requirements framing: `Research/ExhibitGuide_Project_Brief.pdf`
- UX wireframes for scan and visitor flow: `Research/ExhibitGuide Scan Flow Wireframes.html`
- Pitch context and product framing: `Research/ExhibitGuide Pitch Deck.html`
- Core domain models: `backend/exhibits/models.py`
- User activity and inquiry models: `backend/users/models.py`
- Public exhibit flow implementation: `backend/exhibits/views.py`, `frontend/src/ExhibitDetail.jsx`
- Authentication, profile, and collector API implementation: `backend/users/api_views.py`, `backend/users/serializers.py`
- Route design and URL architecture: `frontend/src/App.jsx`, `backend/exhibit_guide_pwa/urls.py`, `backend/exhibits/api_urls.py`, `backend/users/api_urls.py`
- Workflow tests and endpoint coverage: `backend/users/tests_api.py`, `backend/exhibits/tests.py`

## Submission Structure and Tidy-Up
To demonstrate clean submission hygiene, this project applies the following checks:

- Keep one primary Django project/app path for assessment (`backend/`) and avoid duplicate copy folders.
- Keep exploratory notebooks out of submission roots unless they are explicitly required evidence.
- Exclude backup directories from tracked submission content.
- Keep generated/static artifact directories out of assessment focus unless required by deployment checks.
- Include the project `.gitignore` in LMS upload so assessors can reproduce the intended submission scope.
- Keep `.gitignore` Django-specific (for example `*.sqlite3`, `.env`) and avoid Flask-only patterns that do not apply to this project.

## Technical Stack

Backend (`backend/`) — REST API and admin only; no server-rendered application pages:
- Python 3.12, Django 4.2, Django ORM
- Django REST Framework (`djangorestframework`)
- JWT authentication (`djangorestframework-simplejwt`)
- `django-cors-headers` for cross-origin access from the React frontend
- PostgreSQL (when `DATABASE_URL` is provided) / SQLite (local default)
- Django auth system + token-based password reset
- WhiteNoise + Gunicorn for deployment support

Frontend (`frontend/`) — separate single-page application:
- React 19 with Vite
- React Router for client-side routing
- Native `fetch` for API calls (no HTTP client dependency)
- CSS custom properties implementing the Figma design system
  (DM Serif Display + Instrument Sans)

## Core Features Implemented
- Public scan page and exhibit preview page
- User registration, login, logout
- Password reset flow via API (`/api/auth/password-reset/*`) with React reset screens
- User profile update page
- Dashboard with scan/watchlist filtering, enquiry flow, and status transitions (watching -> lead -> prospect)
- Enquiry modal and enquiry workflow
- Contact preference capture (email/phone/text) during enquiry
- Optional profile enrichment during enquiry
- Staff exhibit management in-app (`/manage`) plus Django admin CMS for artists, artworks, shows, exhibits, enquiries (`GalleryInquiry`), and prospects (`Prospect`)

## Development Evidence (Inception to Tested Endpoints)
This section provides explicit evidence of software development, not only final features.

### Analysis and Design Inputs
Design started from the brief and was translated into explicit user journeys:
- Visitor journey: scan QR -> view exhibit -> express interest -> authenticate -> enquire.
- Gallery journey: manage content -> monitor interest -> follow up leads.

Wireframe traceability:
- Scan and visitor interaction layouts are documented in `Research/ExhibitGuide Scan Flow Wireframes.html`.
- Pitch artefacts provide the product rationale and target outcomes in `Research/ExhibitGuide Pitch Deck.html`.

Design decisions carried from analysis to implementation:
- Low-friction first touchpoint required a public QR route before authentication.
- Data model had to support reusable artwork/show relationships and visitor inquiry capture.
- Admin had to support non-developer content operations without a custom staff frontend.

### Inception Statement (Problem, Users, Success Criteria)
Initial problem:
- Visitors at physical exhibitions need a low-friction path from artwork discovery to contact with the gallery.

Primary user groups:
- Visitor/collector (public + authenticated flow)
- Gallery owner/admin (content and lead management)

Success criteria defined at project inception:
- A visitor can scan a QR code and open a meaningful exhibit page.
- A visitor can register/login and save interest in works.
- A visitor can submit an enquiry with preferred contact method.
- Gallery staff can manage artists, artworks, shows, and exhibits from Django admin.
- Gallery staff can view and follow up visitor enquiries.

### Feature Development Ledger (What, How, Why, Test)
| Feature | Why this was needed | How it was built | Endpoint(s) | Test evidence |
|---|---|---|---|---|
| QR-first exhibit entry | Reduce friction between in-person viewing and digital engagement | `Exhibit` stores `qr_identifier`; `ExhibitByQrView` exposes a public lookup consumed by the React `/qr/:qrId` route | `/qr/<qr_identifier>` (frontend), `/api/exhibits/qr/<qr_identifier>/` (API) | `exhibits/tests.py` covers `qr_identifier` auto-generation underpinning the QR flow |
| Registration + login | Convert anonymous interest into persistent user state | JWT auth endpoints in `users/api_views.py` consumed by React `AuthContext` (tokens in browser storage, refresh on 401) | `/register`, `/login` (frontend); `/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/` (API) | `users/tests_api.py` verifies registration, token issue, and protected-endpoint access |
| Dashboard watchlist | Keep visitor intent after initial scan | `SavedExhibit` model + `POST /api/saved/` and `DELETE /api/saved/<exhibit_id>/` from the React dashboard | `/dashboard`, `/api/saved/` | `users/tests_api.py` verifies collection semantics and authenticated access |
| Enquiry workflow | Turn viewing intent into actionable lead data for gallery follow-up | `POST /api/inquiries/` writes/updates `GalleryInquiry`; repeat submissions are idempotent and can upgrade lead -> prospect via purchase marker | `/dashboard`, `/api/inquiries/`, `/api/collection/` | `users/tests_api.py` validates create, repeat idempotency, and lead-to-prospect upgrade |
| Profile enrichment during enquiry | Avoid repeatedly asking users for contact details | Dashboard enquiry modal saves profile fields first through `PATCH /api/auth/profile/` then submits enquiry | `/dashboard`, `/profile`, `/api/auth/profile/` | `users/tests_api.py` validates profile patch rules (including preferred contact/phone validation) |
| Admin CMS for content operations | Give non-developer operators control over exhibit content | Django admin registration/inlines for artist/artwork/show/exhibit and lead records | `/admin/` | Manual assessor steps documented in Persona 2 flow |

### Development Sequence (Concise Build Narrative)
1. Modelled core gallery domain (`Artist`, `Artwork`, `Show`, `Exhibit`) to support reusable relationships.
2. Added public browsing and QR-based entry so users can start without authentication.
3. Added authentication to persist interest and support a personal dashboard.
4. Added watchlist and filtering behaviors to manage browsing intent over time.
5. Added enquiry capture and prospect creation to connect visitor actions to business outcomes.
6. Added profile persistence and contact preferences to improve follow-up quality.
7. Hardened delivery with tests and deployment configuration.

This sequence is intended to evidence iterative development from first problem framing to tested user outcomes.

### Why These Technical Decisions
- Django ORM over raw SQL: chosen for maintainability, migrations, and relationship integrity.
- Separate `Artwork` and `Show` entities: supports reusability and avoids data duplication.
- JWT auth + API-first password reset: supports decoupled React frontend while preserving Django security primitives.
- Admin-as-CMS approach: fastest path to operator usability without building a separate staff frontend.
- Testing focused on user workflows: validates high-value routes and state transitions rather than only isolated helpers.

### Django Implementation Details (How and Where)
Database integration in Django:
- Domain schema is defined in `backend/exhibits/models.py` (`Artist`, `Artwork`, `Show`, `Exhibit`).
- User interaction schema is defined in `backend/users/models.py` (`SavedExhibit`, `SavedCollection`, `GalleryInquiry`, `Prospect`, `UserProfile`).
- Relationships use ORM foreign keys and many-to-many fields to enforce data integrity and simplify query logic.

Authentication and authorization in Django:
Authentication and authorization in Django:
- Registration, profile, password reset, and collection/inquiry actions are exposed as REST endpoints in `backend/users/api_views.py`.
- React route protection uses `RequireAuth` and `RequireStaff` wrappers in `frontend/src/App.jsx`.
- API-level protection uses DRF permissions (`IsAuthenticated` for user data and `IsStaffOrReadOnly` for exhibit writes).

Code snippet (staff-only writes + public reads pattern):

```python
class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
```

## Authentication and Authorization Evidence (Inception to Tested)
This section shows how auth and access boundaries are implemented in the current React + API architecture.

### Implementation Summary
1. JWT token issue/refresh is provided by `/api/auth/login/` and `/api/auth/refresh/`.
2. React stores and refreshes tokens via `AuthContext`, then attaches bearer auth in `authFetch`.
3. Protected frontend routes (`/dashboard`, `/profile`) use `RequireAuth`; staff routes (`/manage*`) use `RequireStaff`.
4. User-scoped API endpoints (`/api/auth/profile/`, `/api/collection/`, `/api/saved/`, `/api/inquiries/`) require authentication.
5. Exhibit writes are limited to staff via `IsStaffOrReadOnly`; public read routes remain open.

Role/access matrix in this project:

| Role | Allowed | Restricted |
|---|---|---|
| Guest (anonymous) | `/`, `/exhibits/<id>`, `/qr/<qr_identifier>`, `/scan`, `/register`, `/login`, `/password-reset`, `/reset-password`, `POST /api/interest/`, public exhibit reads | `/dashboard`, `/profile`, `/manage`, `/api/collection/`, `/api/saved/`, `/api/inquiries/`, exhibit writes, `/admin/` |
| Authenticated user | Dashboard/profile routes and user-scoped collector APIs | Staff exhibit writes, `/manage*`, Django admin |
| Staff/admin user | All authenticated routes plus `/manage*` and exhibit CRUD writes, plus `/admin/` CMS workflows | N/A for current scope |

### Tested Endpoints and Evidence
Authentication and collector API behavior is covered in `backend/users/tests_api.py`, including:
1. profile read/update behavior and validation,
2. password reset request + confirm flow,
3. inquiry creation, idempotent repeat handling, and lead-to-prospect upgrades,
4. collection status transitions (`lead` then `prospect`).

## Data Schema Overview
Main domain models:
- `Artist`
- `Artwork` (FK to `Artist`)
- `Show`
- `Exhibit` (FK to `Artwork`, FK to `Show`, FK to Django `User` as owner/publisher)

User activity models:
- `UserProfile` (OneToOne with Django `User`)
- `SavedExhibit` (FK to user and exhibit)
- `SavedCollection` (FK to user, M2M to exhibit)
- `GalleryInquiry` (FK to user and exhibit)
- `Prospect` (lead record linked to exhibit)

Design intent:
- Artwork and Show are separate tables to support reuse across multiple exhibits.
- Enquiry and prospect data are tied to specific exhibits, which allows show-level reporting through exhibit relationships.

### DB Design Considerations
- Reuse over duplication: artwork metadata is stored once and referenced from exhibits.
- Separation of concerns: profile data (`UserProfile`) is separate from interest/enquiry data (`SavedExhibit`, `GalleryInquiry`, `Prospect`).
- Lead tracking: inquiry + prospect records are linked to a specific exhibit so reporting can roll up through show relationships.
- Predictable QR addressing: `Exhibit.save()` auto-generates `qr_identifier` once persisted, creating stable public links.

## Database Integration Playbook (SQLite, Local Postgres, Connected Postgres)
This project uses environment-based database switching in `backend/exhibit_guide_pwa/settings.py`.

How switching works:
- Local/debug mode (`DJANGO_DEBUG=true`): uses `DJANGO_LOCAL_DATABASE_URL` when set, otherwise SQLite at `backend/db.sqlite3`.
- Production mode (`DJANGO_DEBUG=false`): uses `DATABASE_URL` (preferred) or `DJANGO_PRODUCTION_DATABASE_URL`.
- Parsing and connection setup is handled through `dj_database_url.config(...)`.

### Option A: Run with SQLite (local, simplest)
Use when:
- you need deterministic local setup,
- or external Postgres is unavailable.

Commands:

```bash
cd backend
export DJANGO_DEBUG=true
unset DATABASE_URL
/absolute/path/to/venv/bin/python manage.py migrate
/absolute/path/to/venv/bin/python manage.py runserver
```

### Option B: Run with local PostgreSQL
Use when:
- you want parity with production behavior,
- and you control local Postgres users/permissions.

1. Create DB role and database (example):

```sql
CREATE ROLE exhibitguide_app WITH LOGIN PASSWORD 'change-this-password';
CREATE DATABASE exhibitguide_dev OWNER exhibitguide_app;
GRANT ALL PRIVILEGES ON DATABASE exhibitguide_dev TO exhibitguide_app;
```

2. Point Django to local Postgres:

```bash
export DJANGO_DEBUG=true
export DJANGO_LOCAL_DATABASE_URL="postgres://exhibitguide_app:change-this-password@127.0.0.1:5432/exhibitguide_dev"
```

3. Run migrations/app:

```bash
cd backend
/absolute/path/to/venv/bin/python manage.py migrate
/absolute/path/to/venv/bin/python manage.py runserver
```

### Option C: Run with a connected Postgres instance (for example Render)
Use when:
- validating against hosted infrastructure,
- reproducing production-like connectivity/security behavior.

Set:

```bash
export DJANGO_DEBUG=false
export DATABASE_URL="postgres://<user>:<password>@<host>:<port>/<database>"
```

Then run migrations/tests/app as normal.

### What Render does vs what the developer must do
What Render provides when you deploy a managed Postgres instance:
- hosted PostgreSQL service,
- network host/port and connection URL,
- managed availability and backups according to plan,
- TLS-capable endpoint.

What the developer remains responsible for:
- injecting correct `DATABASE_URL` into the web service environment,
- running `manage.py migrate` during deploy/release,
- ensuring Django security settings are production-safe (`DEBUG=False`, secure cookies, allowed hosts, CSRF trusted origins),
- handling schema evolution through migrations,
- validating app-level database permissions and least-privilege access,
- diagnosing connection issues (DNS, SSL mode, firewall/network policy).

Evidence in this repository:
- environment-driven DB selection: `backend/exhibit_guide_pwa/settings.py`
- deploy-oriented dependencies/config: `requirements.txt`, `runtime.txt`

## settings.py Environment Logic (How, Why, Local Testing)
This project loads environment values from `.env` when present and then applies safe defaults for local development.

How it works:
1. `load_dotenv(BASE_DIR / '.env')` loads key/value pairs for local runs.
2. `_bool_env(...)` and `_int_env(...)` parse environment values safely.
3. `DEBUG` is derived from environment values (`DJANGO_DEBUG`/`DEBUG`) instead of hard-coded values.
4. `SECRET_KEY` must be present in non-debug mode; in local debug mode only, a development fallback is used.
5. Database source is chosen by mode:
   - `DJANGO_DEBUG=true` -> `DJANGO_LOCAL_DATABASE_URL` or SQLite fallback,
   - `DJANGO_DEBUG=false` -> `DATABASE_URL` (or `DJANGO_PRODUCTION_DATABASE_URL`).
6. `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are built from environment values to support local and hosted domains.

Why this is beneficial:
- separates secrets from source code,
- keeps local setup simple,
- supports the same codebase across local and hosted environments,
- reduces configuration drift between developers.

Example `.env` for local SQLite:

```env
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=replace-with-local-dev-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Example `.env` for local Postgres:

```env
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=replace-with-local-dev-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_LOCAL_DATABASE_URL=postgres://exhibitguide_app:change-this-password@127.0.0.1:5432/exhibitguide_dev
DJANGO_DB_SSL_REQUIRE=false
```

Local validation steps:
1. Start with SQLite (`DJANGO_DEBUG=true`, `DJANGO_LOCAL_DATABASE_URL` unset), run `manage.py migrate`, then `manage.py check`.
2. Switch to Postgres (`DJANGO_LOCAL_DATABASE_URL` set), run `manage.py migrate`, then `manage.py check`.
3. Run tests in each mode where available to confirm parity for your local environment.

## Admin CMS Capability (Current State)
The admin area supports CRUD and relationship workflows needed by gallery directors.

Implemented admin operations:
- Create/edit/delete artists
- Create/edit/delete artworks and assign artist
- Create/edit/delete shows
- Create/edit/delete exhibits and assign show + artwork + publishing owner
- View visitor enquiries and prospects by exhibit and show
- Use inline editing paths to manage linked records faster (for example artworks under an artist, exhibits under a show)

## Assessment Mapping (Rubric-Aligned)

### A. Frameworks Assessment How-To Guide (Django + Database)

| Requirement | Status | Evidence |
|---|---|---|
| Demonstrate understanding and apply key concepts of Django | Met | Django app structure, DRF views/viewsets/serializers, model relationships, admin, and deployment settings are used throughout |
| Show clear understanding of database integration in Django | Met | ORM models with relationships, migrations, query filtering, and admin data operations |
| Show clear understanding of authentication and authorisation | Met | JWT register/login/refresh endpoints, `IsAuthenticated` per-user endpoints, staff-only exhibit writes (`IsStaffOrReadOnly`), protected React routes, token-based password reset |
| Demonstrate clean code structure including templates, styling, JavaScript | Met (with note) | Structure is a decoupled React SPA (`frontend/`) against a Django REST API (`backend/`); styling is a custom CSS design system implementing the project's Figma designs |
| Show evidence of a hosted Django app that is fully functional and accessible | Partially met | Hosting configuration is present; assessor should verify live uptime and route functionality at marking time |

Notes for assessors:
- Password storage is handled by Django built-in hashing and validators.
- Role model is effectively guest/authenticated/admin via Django defaults; no custom multi-role permission matrix is implemented.

### B. Final Assignment Guide (Front End, Back End, Security, Hosting)

| Requirement | Status | Evidence |
|---|---|---|
| Demonstrate understanding and apply key concepts of Front End development | Met | Responsive templates, page flows, CSS/JS behavior on public and authenticated pages |
| Show clear understanding of Back End development | Met | DRF API views/viewsets/serializers, Django ORM models, route handling, validation, and admin operations |
| Show clear understanding of implementing a secure web application | Met | CSRF middleware, Django auth, password hashing/validators, protected routes |
| Demonstrate clear and concise communication in documentation | Partially met | README and code docstrings/comments are present; presentation delivery is outside repository scope |
| Show evidence of a hosted web app that is fully functional and accessible | Partially met | Deployment-oriented dependencies/config are present; live verification needed during assessment |

Feature checklist from the final assignment brief:

| Feature expectation | Status | Notes |
|---|---|---|
| User registration and login | Met | Implemented |
| Dashboard after login | Met | Implemented |
| Idea-specific feature set | Met | Exhibit preview + watchlist + enquiries + profile capture |
| Responsive design | Met | Mobile-first with desktop breakpoints |
| External API integration | Not yet met | No external API integration is currently implemented |
| Automated testing | Met | 27 tests currently pass |
| Version control workflow | Partially met | Git is used; branch/commit workflow quality is reviewed from repository history |
| Deployment | Partially met | Deployment dependencies/config are present; hosted verification required at assessment time |

### Current Evidence Summary (Repository-Based)
Based on repository evidence only, the project currently demonstrates strong implementation in:
- Django concepts,
- database integration,
- authentication and security fundamentals,
- clean project structure and maintainability,
- automated testing for key flows.

Areas that still require assessor-time confirmation or further implementation:
- stable hosted accessibility during marking,
- at least one external API integration (explicit final-assignment feature item).

## Routes (Assessor Quick View)

See **Minimal Route Checklist For Assessment** near the top of this README for the full
frontend and API route tables. Summary:

Frontend (public): `/`, `/exhibits/<id>`, `/qr/<qr_identifier>`, `/scan`, `/register`,
`/login`, `/password-reset`, `/reset-password`
Frontend (authenticated): `/dashboard`, `/profile`
Frontend (staff): `/manage`, `/manage/new`, `/manage/<id>/edit`
API: `/api/exhibits/`, `/api/exhibits/qr/<qr_identifier>/`, `/api/interest/`,
`/api/auth/*`, `/api/collection/`, `/api/saved/`, `/api/inquiries/`
Admin: `/admin/`

## Automated Testing
Current test run result:
- Total tests: 14
- Status: all passing with local SQLite override (`DJANGO_DEBUG=1`, `DJANGO_LOCAL_DATABASE_URL=sqlite:////tmp/exhibitguide_test.sqlite3`)

Endpoint-oriented testing evidence:
- Collector API behavior (`/api/auth/profile/`, `/api/auth/password-reset/*`, `/api/collection/`, `/api/inquiries/`) is validated in `users/tests_api.py`.
- Password reset email generation/link structure is validated in `users/tests_api.py` using `locmem` email backend.
- Inquiry idempotency and lead/prospect transitions are validated in `users/tests_api.py`.
- Exhibit model integrity supporting QR/public routing is validated in `exhibits/tests.py`.

### Key Test Design Samples
1. Profile patch validation (`users/tests_api.py`): requires phone when preferred contact is `phone` or `text`.
2. Password reset request + confirm (`users/tests_api.py`): generates reset link and confirms password update.
3. Inquiry repeat behavior (`users/tests_api.py`): duplicate inquiry returns `already_expressed=true` without extra rows.
4. Collection status progression (`users/tests_api.py`): verifies `lead` status and upgrade to `prospect`.

These tests were selected to verify high-value business behavior and data integrity, not only individual helper functions.

### Test Execution Commands
Run all tests with a deterministic local SQLite database:

```bash
cd backend
DJANGO_DEBUG=1 DJANGO_DB_SSL_REQUIRE=0 DJANGO_LOCAL_DATABASE_URL=sqlite:////tmp/exhibitguide_test.sqlite3 /absolute/path/to/venv/bin/python manage.py test
```

Run focused suites used for assessment demonstration:

```bash
cd backend
DJANGO_DEBUG=1 DJANGO_DB_SSL_REQUIRE=0 DJANGO_LOCAL_DATABASE_URL=sqlite:////tmp/exhibitguide_test.sqlite3 /absolute/path/to/venv/bin/python manage.py test users.tests_api exhibits.tests
```

PostgreSQL local test note:
- If `DATABASE_URL` points to an unreachable host, Django test setup fails before tests execute.
- In this repository, the common failure mode is DNS/host resolution for an external Postgres host, which appears as `OperationalError` during test database creation.
- For assessor reproducibility, either provide a reachable PostgreSQL URL or override `DATABASE_URL` to local SQLite for functional test execution.

### Running Tests on PostgreSQL (user/permissions requirements)
Minimum requirements for the database role used in `DATABASE_URL`:
- login permission,
- permission to connect to target database,
- permission to create and drop test databases (Django creates a test database),
- permission to create tables, indexes, sequences, and constraints in the test database.

Recommended setup for local assessment:
1. Create a dedicated role and grant createdb.

```sql
CREATE ROLE exhibitguide_test WITH LOGIN PASSWORD 'change-this-password' CREATEDB;
```

2. Create a base database owned by that role.

```sql
CREATE DATABASE exhibitguide_base OWNER exhibitguide_test;
GRANT ALL PRIVILEGES ON DATABASE exhibitguide_base TO exhibitguide_test;
```

3. Export a Postgres URL using that role.

```bash
export DATABASE_URL="postgres://exhibitguide_test:change-this-password@127.0.0.1:5432/exhibitguide_base"
```

4. Run tests.

```bash
cd backend
/absolute/path/to/venv/bin/python manage.py test
```

Troubleshooting checklist for assessor local Postgres failures:
1. Confirm host resolves and is reachable from the local machine.
2. Confirm credentials are valid by connecting with `psql` using the same host/user/db.
3. Confirm role has `CREATEDB` (or equivalent ability to create test DBs).
4. Confirm no policy/firewall is blocking DB access.
5. If using managed Postgres, confirm SSL requirements and URL parameters.

## Local Setup (Developer Reproducibility Sequence)
1. Clone the repository and open the project root.
2. Create and activate a virtual environment.
3. Install dependencies (the requirements file lives in the `backend/` folder):

```bash
pip install -r backend/requirements.txt
```

4. Choose a database mode:
- SQLite mode: leave `DATABASE_URL` unset.
- Postgres mode: set `DATABASE_URL` to your local or managed Postgres URL.

5. Run migrations:

```bash
cd backend
python manage.py migrate
```

6. Run checks and tests:

```bash
python manage.py check
python manage.py test users.tests exhibits.tests
```

7. (Optional) Create an admin user:

```bash
python manage.py createsuperuser
```

8. Run the server:

```bash
python manage.py runserver
```

9. Execute the hosted/local run-through checklist in this README to verify functional endpoints.

## Deployment Runbook (Render)

This version is a **decoupled application**, so it deploys as **two Render services**
plus a database — unlike the original single-service Django app on `main`:

| # | Service | Render type | Source directory |
|---|---------|-------------|------------------|
| 1 | Django REST API + admin | **Web Service** | `backend/` |
| 2 | React frontend | **Static Site** | `frontend/` |
| 3 | Database | **PostgreSQL** | — |

### Hosted URLs

| Service | URL |
|---------|-----|
| Frontend (React) | `https://exhibitguide-react-frontend.onrender.com` |
| Backend API + admin | `https://exhibitguide-1.onrender.com` |

### Service 1 — Django API (Web Service)

Root Directory: `backend` (the Django project with `manage.py` and `requirements.txt`).

```bash
# Build Command
pip install -r requirements.txt && python manage.py collectstatic --noinput

# Pre-Deploy Command (runs after build, before the new version goes live)
python manage.py migrate

# Start Command
gunicorn exhibit_guide_pwa.wsgi:application
```

Environment variables:

| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | A newly generated secret (do not reuse another deployment's key) |
| `DJANGO_DEBUG` | `false` |
| `DATABASE_URL` | Connection string from the Render Postgres instance |
| `DJANGO_ALLOWED_HOSTS` | This service's hostname |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://` origin of this service |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `https://` origin of the **frontend** static site |
| `FRONTEND_URL` | `https://` origin of the **frontend** static site (used to build password-reset links) |
| `DJANGO_EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `DJANGO_DEFAULT_FROM_EMAIL` | Sender address (for example `noreply@yourdomain.com`) |
| `DJANGO_EMAIL_HOST` | SMTP host from your provider |
| `DJANGO_EMAIL_PORT` | SMTP port (usually `587` for TLS or `465` for SSL) |
| `DJANGO_EMAIL_HOST_USER` | SMTP username |
| `DJANGO_EMAIL_HOST_PASSWORD` | SMTP password or app password |
| `DJANGO_EMAIL_USE_TLS` | `true` for STARTTLS setups (usually with port `587`) |
| `DJANGO_EMAIL_USE_SSL` | `false` unless your provider requires implicit SSL |

### Service 2 — React frontend (Static Site)

Root Directory: `frontend`.

```bash
# Build Command
npm ci && npm run build

# Publish Directory
dist
```

Environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://` origin of the **backend** service, with no trailing slash |

`VITE_API_URL` is read at **build time** — Vite compiles the value into the JavaScript
bundle. Changing it requires a **new deploy**, not just a restart. The variable must keep
its `VITE_` prefix to be exposed to application code.

**Required rewrite rule** (Redirects/Rewrites tab):

| Source | Destination | Action |
|--------|-------------|--------|
| `/*` | `/index.html` | Rewrite |

Client-side routes such as `/dashboard` and `/exhibits/5` exist only inside React Router.
Without this rule, loading or refreshing those URLs directly returns a 404.

### Deployment order

The two services reference each other's URLs, so deploy in this order:

1. Create the Postgres instance.
2. Create the backend Web Service (leave `DJANGO_CORS_ALLOWED_ORIGINS` and `FRONTEND_URL`
   unset for now) and note its URL.
3. Create the frontend Static Site with `VITE_API_URL` set to the backend URL; note its URL.
4. Set `DJANGO_CORS_ALLOWED_ORIGINS` and `FRONTEND_URL` on the backend, then redeploy it.
   Until this step is complete the frontend loads but every API call is blocked by CORS.
5. Seed content from the backend service's shell: `python manage.py seed_data`.
6. Create an admin account: `python manage.py createsuperuser`.

### Verification after deploy

1. Open the frontend URL and confirm the exhibit list renders.
2. Open an exhibit, then refresh the page — a 404 indicates the rewrite rule is missing.
3. Register an account and confirm redirection to the dashboard.
4. Save an exhibit, then confirm it appears in the dashboard as `watching`.
5. Open `<backend>/admin/` and confirm admin access.

Notes:
- `whitenoise`, `gunicorn`, and `dj-database-url` are already configured in this repository.
- If the frontend renders but shows no data, check `VITE_API_URL` and the backend's
  `DJANGO_CORS_ALLOWED_ORIGINS` first; browser console errors distinguish the two.
- On Render's free tier the backend spins down when idle, so the first request after a
  quiet period can take 30–60 seconds.

### Known deployment limitations
- **Uploaded images are not persistent.** Render's filesystem is ephemeral, so exhibit
  images uploaded through the staff interface are lost on redeploy. Seeded exhibits are
  unaffected because they reference external image URLs. Persistent uploads would require
  object storage (for example S3 or Cloudinary via `django-storages`).
- **Password-reset delivery requires SMTP credentials.** Production now defaults to SMTP,
   but messages still fail if provider variables are missing or incorrect
   (`DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`, and TLS/SSL settings).

## Known Gaps and Next Steps
To close remaining checklist gaps:
1. Add at least one external API integration relevant to exhibit experience.
2. Confirm hosted URL uptime and include a short deployment verification record (for example screenshots and route checks).
3. Add explicit role/permission documentation (guest, authenticated user, admin).
4. Optionally add stricter object-level ownership checks in tests for all user-editable records.
