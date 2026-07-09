"""Top-level URL routing for the project.

This file connects the main user account routes, the exhibit experience,
the Django admin, and development-only media serving.
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    # Back-office content management.
    path('admin/', admin.site.urls),
    # Signed-in collector experience.
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('profile/', user_views.profile, name='profile'),
    # Authentication flow.
    path('register/', user_views.register, name='register'),
    path('login/', user_views.login, name='login'),
    path('logout/', user_views.logout, name='logout'),
    # Password recovery flow powered by Django auth views.
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.txt',
            subject_template_name='users/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    # Public scan and exhibit pages live under /exhibits/.
    path('exhibits/', include('exhibits.urls')),
]

if settings.DEBUG:
    # Serve uploaded media files directly in local development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
