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
This section is designed for first-time assessors.

If the hosted app is unavailable, run locally using the Local Setup section and then follow the same steps below.

### Persona 1: Visitor Flow (Public -> Enquiry -> Dashboard)
Goal: verify the end-to-end visitor journey from scan to enquiry and saved exhibit management.

1. Open `exhibit-qr-codes.html` and use one of the provided QR links (or scan one QR code if testing on mobile).
2. Confirm the QR route opens an exhibit preview page at `/exhibits/qr/<qr_identifier>/`.
3. On the exhibit page, select **Express Interest**.
4. Create a new account at `/register/`.
5. After registration, confirm redirect to `/dashboard/`.
6. In the dashboard, verify the scanned exhibit appears.
7. Select **Enquire** and submit once with default contact method, then again with phone/text selected to verify phone requirement behavior.
8. Confirm success message after enquiry.
9. Use dashboard filters (`Scanned`, `Watching`, `Enquired`) to verify state changes and visibility.
10. Open `/profile/` and confirm saved details can be reviewed or updated.

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
Public and auth routes:
- `/exhibits/`
- `/exhibits/qr/<qr_identifier>/`
- `/register/`
- `/login/`
- `/logout/`
- `/password-reset/`

Authenticated routes:
- `/dashboard/`
- `/profile/`

Admin route:
- `/admin/`

## Live Application and Repository
- Repository: this project repository
- Hosted URL configured in settings: `https://exhibitguide.onrender.com`
- Note: hosted availability depends on deployment state and hosting uptime.

## Hosted Accessibility Evidence (Run-Through)
Use this sequence to verify the hosted app is functional and accessible.

1. Open the hosted root and confirm a successful page load (HTTP 200).
2. Open `/exhibits/` and confirm the scan/entry page renders.
3. Open `/exhibits/qr/<qr_identifier>/` using a known seeded record and confirm exhibit details render.
4. Open `/register/`, create an account, and confirm redirect to `/dashboard/`.
5. Log out and log in again via `/login/` to verify session/auth flow.
6. Open `/profile/` while signed in and confirm profile page access.
7. Submit a dashboard enquiry and confirm success feedback.
8. Open `/admin/` with staff credentials and confirm admin index access.

Expected outcome:
- public routes are available,
- authenticated routes enforce login,
- admin route enforces staff authorization,
- core visitor and admin workflows are operational.

## Documentation Map (Analysis to Design to Implementation to Test)
- Project brief and requirements framing: `Research/ExhibitGuide_Project_Brief.pdf`
- UX wireframes for scan and visitor flow: `Research/ExhibitGuide Scan Flow Wireframes.html`
- Pitch context and product framing: `Research/ExhibitGuide Pitch Deck.html`
- Core domain models: `exhibit_guide_pwa/exhibits/models.py`
- User activity and inquiry models: `exhibit_guide_pwa/users/models.py`
- Public exhibit flow implementation: `exhibit_guide_pwa/exhibits/views.py`
- Authentication + dashboard implementation: `exhibit_guide_pwa/users/views.py`
- Route design and URL architecture: `exhibit_guide_pwa/exhibit_guide_pwa/urls.py`, `exhibit_guide_pwa/exhibits/urls.py`
- Workflow tests and endpoint coverage: `exhibit_guide_pwa/users/tests.py`, `exhibit_guide_pwa/exhibits/tests.py`

## Submission Structure and Tidy-Up
To demonstrate clean submission hygiene, this project applies the following checks:

- Keep one primary Django project/app path for assessment (`exhibit_guide_pwa/`) and avoid duplicate copy folders.
- Keep exploratory notebooks out of submission roots unless they are explicitly required evidence.
- Exclude backup directories from tracked submission content.
- Keep generated/static artifact directories out of assessment focus unless required by deployment checks.
- Include the project `.gitignore` in LMS upload so assessors can reproduce the intended submission scope.
- Keep `.gitignore` Django-specific (for example `*.sqlite3`, `.env`) and avoid Flask-only patterns that do not apply to this project.

## Technical Stack
- Python 3.12
- Django 4.2
- PostgreSQL (when `DATABASE_URL` is provided) / SQLite (local default)
- Django ORM
- Django auth system (`UserCreationForm`, `AuthenticationForm`, password reset views)
- HTML templates, CSS, JavaScript
- `crispy_forms` + `crispy_bootstrap5` (installed and configured)
- WhiteNoise + Gunicorn for deployment support

## Core Features Implemented
- Public scan page and exhibit preview page
- User registration, login, logout
- Password reset flow using Django built-in views
- User profile update page
- Dashboard with watchlist and status filters
- Enquiry modal and enquiry workflow
- Contact preference capture (email/phone/text) during enquiry
- Optional profile enrichment during enquiry
- Admin CMS workflows for artists, artworks, shows, exhibits, visitor enquiries (`GalleryInquiry`), and prospect records (`Prospect`)

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
| QR-first exhibit entry | Reduce friction between in-person viewing and digital engagement | `Exhibit` stores `qr_identifier`; exhibit routes expose a QR lookup view | `/exhibits/qr/<qr_identifier>/` | `exhibits/tests.py` covers exhibit model behavior used by the QR flow foundation |
| Registration + login | Convert anonymous interest into persistent user state | Django auth forms and custom auth views in user app | `/register/`, `/login/`, `/logout/` | `users/tests.py` verifies registration redirect and login behavior |
| Dashboard watchlist | Keep visitor intent after initial scan | `SavedExhibit` model and dashboard POST actions (`save_exhibit`, `remove_saved_exhibit`) | `/dashboard/` | `users/tests.py` validates idempotent save and remove actions |
| Enquiry workflow | Turn viewing intent into actionable lead data for gallery follow-up | Dashboard action `send_inquiry` writes `GalleryInquiry` + `Prospect`; validates contact preferences | `/dashboard/` | `users/tests.py` validates inquiry creation and phone-required validation |
| Profile enrichment during enquiry | Avoid repeatedly asking users for contact details | Optional `save_to_profile` path updates `UserProfile` from enquiry data | `/dashboard/`, `/profile/` | `users/tests.py` verifies profile update from enquiry submission |
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
- Built-in Django auth and password reset: secure defaults and reliable delivery for assessment scope.
- Admin-as-CMS approach: fastest path to operator usability without building a separate staff frontend.
- Testing focused on user workflows: validates high-value routes and state transitions rather than only isolated helpers.

### Django Implementation Details (How and Where)
Database integration in Django:
- Domain schema is defined in `exhibit_guide_pwa/exhibits/models.py` (`Artist`, `Artwork`, `Show`, `Exhibit`).
- User interaction schema is defined in `exhibit_guide_pwa/users/models.py` (`SavedExhibit`, `SavedCollection`, `GalleryInquiry`, `Prospect`, `UserProfile`).
- Relationships use ORM foreign keys and many-to-many fields to enforce data integrity and simplify query logic.

Authentication and authorization in Django:
- Registration uses `UserCreationForm` in `exhibit_guide_pwa/users/forms.py` and `register` view in `exhibit_guide_pwa/users/views.py`.
- Login uses Django `AuthenticationForm` in `exhibit_guide_pwa/users/views.py`.
- Route-level access control is handled with `@login_required` for protected pages such as dashboard/profile in `exhibit_guide_pwa/users/views.py`.
- Password reset is provided by Django auth views wired in `exhibit_guide_pwa/exhibit_guide_pwa/urls.py`.

Code snippet (auth + protected route pattern):

```python
@login_required
def dashboard(request):
	profile = UserProfile.objects.filter(user=request.user).first()
	# ... protected workflow logic for saved exhibits and inquiries ...
	return render(request, 'users/dashboard.html', context)
```

Code snippet (model relationship pattern):

```python
class SavedCollection(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_collections')
	exhibits = models.ManyToManyField(Exhibit, related_name='in_user_collections', blank=True)
```

## Authentication and Authorization Evidence (Inception to Tested)
This section demonstrates how authentication and authorization were developed iteratively from requirement to verified behavior.

### Inception Requirement and Design Intent
Authentication requirement at inception:
- persist visitor intent beyond anonymous scan flow,
- allow users to manage saved exhibits and enquiries over multiple sessions.

Authorization requirement at inception:
- public users should browse exhibit pages,
- signed-in users should access personal dashboard/profile,
- admin-only users should manage CMS content and enquiries in Django admin.

### Implementation Timeline (How)
1. Added registration/login/logout flow in `exhibit_guide_pwa/users/views.py` using Django auth forms.
2. Added protected user routes for dashboard/profile using `@login_required`.
3. Preserved scan context through auth handoff via session key `interest_exhibit_id`.
4. Wired Django password-reset views in `exhibit_guide_pwa/exhibit_guide_pwa/urls.py`.
5. Confirmed admin authorization boundary through Django admin access behavior.

### Authentication and Authorization Architecture (What Django Provides)
Authentication:
- Django `User` model stores accounts and hashed passwords.
- `UserCreationForm` and `AuthenticationForm` provide validated account and sign-in flows.
- `auth_login` and `auth_logout` establish and clear session auth state.

Authorization:
- `@login_required` enforces route-level protection for signed-in-only views.
- Django admin authorization restricts `/admin/` to staff users.
- Django auth middleware/context processors expose request user state to templates and views.

Role/access matrix in this project:

| Role | Allowed | Restricted |
|---|---|---|
| Guest (anonymous) | `/exhibits/`, `/exhibits/qr/<qr_identifier>/`, `/register/`, `/login/` | `/dashboard/`, `/profile/`, admin content operations |
| Authenticated user | Dashboard/profile workflows, inquiries, collections | Django admin content operations (unless staff) |
| Staff/admin user | All authenticated routes + `/admin/` CMS workflows | N/A for current scope |

### Tested Endpoints and Evidence
Key authentication/authorization tests now included:
1. `test_profile_requires_login` in `exhibit_guide_pwa/users/tests.py`.
2. `test_dashboard_requires_login` in `exhibit_guide_pwa/users/tests.py`.
3. `test_login_honors_next_parameter` in `exhibit_guide_pwa/users/tests.py`.
4. `test_admin_index_rejects_non_staff_user` in `exhibit_guide_pwa/users/tests.py`.

These tests provide direct evidence that:
- protected routes cannot be accessed anonymously,
- authenticated navigation and redirects function correctly,
- non-staff users are blocked from admin-only workflows.

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
This project uses environment-based database switching via `DATABASE_URL` in `exhibit_guide_pwa/exhibit_guide_pwa/settings.py`.

How switching works:
- If `DATABASE_URL` is present, Django uses that database (typically PostgreSQL in production).
- If `DATABASE_URL` is missing, Django falls back to local SQLite.
- This is configured through `dj_database_url.config(...)` in settings.

### Option A: Run with SQLite (local, simplest)
Use when:
- you need deterministic local setup,
- or external Postgres is unavailable.

Commands:

```bash
cd exhibit_guide_pwa
export DATABASE_URL="sqlite:////absolute/path/to/exhibit_guide_pwa/db.sqlite3"
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
export DATABASE_URL="postgres://exhibitguide_app:change-this-password@127.0.0.1:5432/exhibitguide_dev"
```

3. Run migrations/app:

```bash
cd exhibit_guide_pwa
/absolute/path/to/venv/bin/python manage.py migrate
/absolute/path/to/venv/bin/python manage.py runserver
```

### Option C: Run with a connected Postgres instance (for example Render)
Use when:
- validating against hosted infrastructure,
- reproducing production-like connectivity/security behavior.

Set:

```bash
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
- environment-driven DB selection: `exhibit_guide_pwa/exhibit_guide_pwa/settings.py`
- deploy-oriented dependencies/config: `requirements.txt`, `runtime.txt`

## settings.py Environment Logic (How, Why, Local Testing)
This project loads environment values from `.env` when present and then applies safe defaults for local development.

How it works:
1. `load_dotenv(BASE_DIR / '.env')` loads key/value pairs for local runs.
2. `_bool_env(...)` and `_int_env(...)` parse environment values safely.
3. `DEBUG` is derived from environment values (`DJANGO_DEBUG`/`DEBUG`) instead of hard-coded values.
4. `SECRET_KEY` must be present in non-debug mode; in local debug mode only, a development fallback is used.
5. `DATABASE_URL` decides database backend:
   - set `DATABASE_URL` -> Postgres (or another supported URL),
   - unset `DATABASE_URL` -> SQLite fallback.
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
DATABASE_URL=postgres://exhibitguide_app:change-this-password@127.0.0.1:5432/exhibitguide_dev
DJANGO_DB_SSL_REQUIRE=false
```

Local validation steps:
1. Start with SQLite (`DATABASE_URL` unset), run `manage.py migrate`, then `manage.py check`.
2. Switch to Postgres (`DATABASE_URL` set), run `manage.py migrate`, then `manage.py check`.
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
| Demonstrate understanding and apply key concepts of Django | Met | Django app structure, forms, views, templates, auth views, messages, and admin are used throughout |
| Show clear understanding of database integration in Django | Met | ORM models with relationships, migrations, query filtering, and admin data operations |
| Show clear understanding of authentication and authorisation | Met | Register/login/logout, protected routes (`@login_required`), Django password reset flow |
| Demonstrate clean code structure including HTML templates, Bootstrap, JavaScript | Met (with note) | Clear app and template/static structure; Bootstrap use is via crispy forms integration rather than a full Bootstrap component system |
| Show evidence of a hosted Django app that is fully functional and accessible | Partially met | Hosting configuration is present; assessor should verify live uptime and route functionality at marking time |

Notes for assessors:
- Password storage is handled by Django built-in hashing and validators.
- Role model is effectively guest/authenticated/admin via Django defaults; no custom multi-role permission matrix is implemented.

### B. Final Assignment Guide (Front End, Back End, Security, Hosting)

| Requirement | Status | Evidence |
|---|---|---|
| Demonstrate understanding and apply key concepts of Front End development | Met | Responsive templates, page flows, CSS/JS behavior on public and authenticated pages |
| Show clear understanding of Back End development | Met | Django views/forms/models, route handling, server-side validation, admin operations |
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
Public/auth:
- `/exhibits/`
- `/exhibits/qr/<qr_identifier>/`
- `/register/`
- `/login/`
- `/logout/`
- `/password-reset/` and related reset routes

Authenticated:
- `/dashboard/`
- `/profile/`

Admin:
- `/admin/`

## Automated Testing
Current test run result:
- Total tests: 27
- Status: all passing (with explicit SQLite override)

Endpoint-oriented testing evidence:
- Auth flow (`/register/`, `/login/`) is validated in `users/tests.py`.
- Dashboard actions (`/dashboard/`) are validated for save/remove/filter/inquiry behavior in `users/tests.py`.
- Profile access and profile persistence (`/profile/`) are validated in `users/tests.py`.
- Exhibit model integrity supporting public exhibit routes is validated in `exhibits/tests.py`.

### Key Test Design Samples
1. Registration flow test (`users/tests.py`): posts valid credentials and asserts redirect to `/dashboard/` plus user creation.
2. Dashboard idempotency test (`users/tests.py`): submits `save_exhibit` twice and asserts only one `SavedExhibit` row exists.
3. Inquiry validation test (`users/tests.py`): requests phone contact without a phone number and asserts no inquiry/prospect is created.
4. Profile update from inquiry test (`users/tests.py`): submits enquiry with `save_to_profile` and asserts profile fields persist.

These tests were selected to verify high-value business behavior and data integrity, not only individual helper functions.

### Test Execution Commands
Run all tests with a deterministic local SQLite database:

```bash
cd exhibit_guide_pwa
DATABASE_URL=sqlite:////absolute/path/to/exhibit_guide_pwa/db.sqlite3 /absolute/path/to/venv/bin/python manage.py test
```

Run focused suites used for assessment demonstration:

```bash
cd exhibit_guide_pwa
DATABASE_URL=sqlite:////absolute/path/to/exhibit_guide_pwa/db.sqlite3 /absolute/path/to/venv/bin/python manage.py test users.tests exhibits.tests
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
cd exhibit_guide_pwa
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
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Choose a database mode:
- SQLite mode: leave `DATABASE_URL` unset.
- Postgres mode: set `DATABASE_URL` to your local or managed Postgres URL.

5. Run migrations:

```bash
cd exhibit_guide_pwa
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
1. Create a Render Postgres instance.
2. Create a Render Web Service connected to this repository.
3. Configure build and start commands:

```bash
# Build Command
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

# Start Command
gunicorn exhibit_guide_pwa.wsgi:application
```

4. Set required environment variables in Render:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=false`
- `DATABASE_URL` (from Render Postgres)
- `DJANGO_ALLOWED_HOSTS` (include your Render hostname)
- `DJANGO_CSRF_TRUSTED_ORIGINS` (https origin for hosted domain)

5. Deploy and wait for successful build/start logs.
6. Open the hosted URL and execute the Hosted Accessibility Evidence run-through.

Notes:
- `whitenoise`, `gunicorn`, and `dj-database-url` are already configured in this repository.
- If deploy succeeds but pages fail, check host/origin environment values first.

## Known Gaps and Next Steps
To close remaining checklist gaps:
1. Add at least one external API integration relevant to exhibit experience.
2. Confirm hosted URL uptime and include a short deployment verification record (for example screenshots and route checks).
3. Add explicit role/permission documentation (guest, authenticated user, admin).
4. Optionally add stricter object-level ownership checks in tests for all user-editable records.
