# ExhibitGuide

## Project Summary
ExhibitGuide is a Django web application for gallery and exhibit experiences.

It provides:
- a public exhibit flow based on QR links,
- user registration and login,
- a user dashboard for saved works and enquiries,
- an admin area that can be used as a lightweight CMS for artists, artworks, shows, exhibits, and enquiry follow-up.

This README is written for assignment assessment. It maps implementation evidence to the published requirements and rubric language.

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
7. Select **Enquire** and submit:
- first with default contact method,
- then with phone/text selected to verify phone requirement behavior.
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
9. Return to `/admin/` and verify monitoring data:
- `GalleryInquiry` shows visitor enquiry content and timestamps,
- `Prospect` shows contact details and callback preference,
- exhibit admin inlines show enquiries/prospects for that exhibit,
- filters allow viewing by show/exhibit/date.

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
- Admin CMS workflows for:
	- Artists
	- Artworks
	- Shows
	- Exhibits
	- Visitor enquiries (`GalleryInquiry`)
	- Prospect records (`Prospect`)

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
| Automated testing | Met | 24 tests currently pass |
| Version control workflow | Partially met | Git is used; branch/commit workflow quality is reviewed from repository history |
| Deployment | Partially met | Deployment dependencies/config are present; hosted verification required at assessment time |

### Distinction-Focused Reading of Current Evidence
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
- Total tests: 24
- Status: all passing

Command used:

```bash
cd exhibit_guide_pwa
python manage.py test
```

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
cd exhibit_guide_pwa
python manage.py migrate
```

4. (Optional) Create an admin user:

```bash
python manage.py createsuperuser
```

5. Run the server:

```bash
python manage.py runserver
```

## Deployment Notes
- `whitenoise` and `gunicorn` are included.
- `dj-database-url` is configured for environment-based database switching.
- `runtime.txt` is present.

Important for production review:
- move secret values to environment variables,
- run with `DEBUG=False`,
- validate host and static file settings on the deployment platform.

## Known Gaps and Next Steps
To close remaining checklist gaps:
1. Add at least one external API integration relevant to exhibit experience.
2. Confirm hosted URL uptime and include a short deployment verification record (for example screenshots and route checks).
3. Add explicit role/permission documentation (guest, authenticated user, admin).
4. Optionally add stricter object-level ownership checks in tests for all user-editable records.
