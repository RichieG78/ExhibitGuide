"""Views that drive account access, the collector dashboard, and profile updates."""

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from exhibits.models import Exhibit

from .forms import GalleryInquiryForm, SavedCollectionForm, UserAccountForm, UserProfileForm, UserRegisterForm
from .models import GalleryInquiry, Prospect, SavedCollection, SavedExhibit, UserProfile


def register(request):
    """Register a user and preserve any scanned exhibit context through the auth flow."""
    # If the visitor came from an exhibit scan, keep that exhibit id in session.
    interest_exhibit_id = request.GET.get('interest_exhibit') or request.POST.get('interest_exhibit')
    if interest_exhibit_id:
        request.session['interest_exhibit_id'] = str(interest_exhibit_id)

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully. Welcome, {username}.')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(
        request,
        'users/register.html',
        {
            'form': form,
            'interest_exhibit_id': interest_exhibit_id or request.session.get('interest_exhibit_id'),
        },
    )


def login(request):
    """Sign a user in and keep their scanned exhibit context intact."""
    interest_exhibit_id = request.GET.get('interest_exhibit') or request.POST.get('interest_exhibit')
    if interest_exhibit_id:
        request.session['interest_exhibit_id'] = str(interest_exhibit_id)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Signed in successfully.')
            return redirect(request.POST.get('next') or 'dashboard')
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        'users/login.html',
        {
            'form': form,
            'interest_exhibit_id': interest_exhibit_id or request.session.get('interest_exhibit_id'),
        },
    )


def logout(request):
    """Sign the user out and show a simple confirmation page."""
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return render(request, 'users/logout.html')


@login_required
def profile(request):
    """Let the signed-in user update account details and their collector profile."""
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    # Copy names from the auth user model the first time a profile is opened.
    updated = False
    if not profile_obj.firstname and request.user.first_name:
        profile_obj.firstname = request.user.first_name
        updated = True
    if not profile_obj.lastname and request.user.last_name:
        profile_obj.lastname = request.user.last_name
        updated = True
    if updated:
        profile_obj.save(update_fields=['firstname', 'lastname'])

    if request.method == 'POST':
        # Account details and profile details are saved together on one page.
        account_form = UserAccountForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if account_form.is_valid() and profile_form.is_valid():
            account_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        account_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile_obj)

    profile_image_url = profile_obj.image.url if profile_obj.image else None
    display_name = request.user.get_full_name().strip() or request.user.username

    return render(
        request,
        'users/profile.html',
        {
            'account_form': account_form,
            'profile_form': profile_form,
            'profile_obj': profile_obj,
            'profile_image_url': profile_image_url,
            'display_name': display_name,
        },
    )


@login_required
def dashboard(request):
    """Show the signed-in collector dashboard and handle watchlist/inquiry actions."""
    profile = UserProfile.objects.filter(user=request.user).first()
    collections = SavedCollection.objects.filter(user=request.user).prefetch_related('exhibits').order_by('-created_at')
    saved_exhibits = SavedExhibit.objects.filter(user=request.user).select_related('exhibit').order_by('-saved_at')
    saved_exhibit_ids = set(saved_exhibits.values_list('exhibit_id', flat=True))

    featured_interest_exhibit = None
    scanned_exhibit = None
    # Prefer an exhibit passed in from the scan flow, then fall back to session.
    interest_exhibit_from_query = request.GET.get('interest_exhibit')
    if interest_exhibit_from_query:
        request.session['interest_exhibit_id'] = str(interest_exhibit_from_query)
    interest_exhibit_id = interest_exhibit_from_query or request.session.get('interest_exhibit_id')
    if interest_exhibit_id:
        featured_interest_exhibit = Exhibit.objects.filter(id=interest_exhibit_id).first()

    if featured_interest_exhibit and featured_interest_exhibit.id not in saved_exhibit_ids:
        # A scanned exhibit that is not saved yet belongs in the Scanned tab.
        scanned_exhibit = featured_interest_exhibit

    if not featured_interest_exhibit:
        saved_item = saved_exhibits.first()
        if saved_item:
            featured_interest_exhibit = saved_item.exhibit

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_exhibit':
            # Move a scanned exhibit into the user's watchlist.
            exhibit_id = request.POST.get('exhibit_id')
            if exhibit_id:
                exhibit = Exhibit.objects.filter(id=exhibit_id).first()
                if exhibit:
                    SavedExhibit.objects.get_or_create(user=request.user, exhibit=exhibit)
                    messages.success(request, f'{exhibit.artwork} added to your watchlist.')
                else:
                    messages.error(request, 'Exhibit not found.')
            return redirect('dashboard')

        elif action == 'remove_saved_exhibit':
            # Remove an exhibit from the user's watchlist.
            exhibit_id = request.POST.get('exhibit_id')
            deleted_count, _ = SavedExhibit.objects.filter(
                user=request.user,
                exhibit_id=exhibit_id,
            ).delete()
            if deleted_count:
                messages.success(request, 'Removed from your watchlist.')
            else:
                messages.error(request, 'Could not remove this exhibit from your watchlist.')
            return redirect('dashboard')

        elif action == 'add_to_collection':
            # Add an already-known exhibit into one of the user's saved collections.
            exhibit_id = request.POST.get('exhibit_id')
            collection_id = request.POST.get('collection_id')
            exhibit = Exhibit.objects.filter(id=exhibit_id).first()
            collection = collections.filter(id=collection_id).first() if collection_id else None
            if not exhibit:
                messages.error(request, 'Exhibit not found.')
            elif not collection:
                messages.error(request, 'Please select a collection.')
            else:
                collection.exhibits.add(exhibit)
                messages.success(request, f'Added {exhibit.artwork} to {collection.name}.')
            return redirect('dashboard')

        elif action == 'create_collection':
            # Create a new named collection from dashboard input.
            collection_form = SavedCollectionForm(request.POST)
            if collection_form.is_valid():
                collection = collection_form.save(commit=False)
                collection.user = request.user
                collection.save()
                collection_form.save_m2m()
                messages.success(request, f'Collection "{collection.name}" created.')
                return redirect('dashboard')

        elif action == 'send_inquiry':
            # Inquiries can be sent immediately, with optional profile enrichment.
            inquiry_form = GalleryInquiryForm(request.POST)
            if inquiry_form.is_valid():
                selected_methods = request.POST.getlist('contact_methods')
                if not selected_methods:
                    selected_methods = ['email']

                wants_phone_contact = any(method in {'phone', 'text'} for method in selected_methods)
                posted_phone = (request.POST.get('contact_phone') or '').strip()
                profile_phone = (profile.phone if profile else '').strip()
                phone_for_contact = posted_phone or profile_phone

                contact_email = (request.POST.get('contact_email') or request.user.email or '').strip()

                if not contact_email:
                    messages.error(request, 'Please add an email address so the gallery can reply.')
                    return redirect('dashboard')

                if wants_phone_contact and not phone_for_contact:
                    messages.error(request, 'Phone number is required when selecting phone or text contact.')
                    return redirect('dashboard')

                # Save the inquiry and include selected contact preferences in the message body.
                inquiry = inquiry_form.save(commit=False)
                inquiry.user = request.user
                methods_label = ', '.join(method.title() for method in selected_methods)
                inquiry.message = f"{inquiry.message}\n\nPreferred contact methods: {methods_label}"
                if wants_phone_contact:
                    inquiry.message += f"\nPhone: {phone_for_contact}"
                inquiry.save()

                first_name = (
                    (request.POST.get('first_name') or '').strip()
                    or (profile.firstname if profile else '').strip()
                    or request.user.first_name
                )
                last_name = (
                    (request.POST.get('last_name') or '').strip()
                    or (profile.lastname if profile else '').strip()
                    or request.user.last_name
                )
                full_name = f'{first_name} {last_name}'.strip() or request.user.username

                prospect, created = Prospect.objects.get_or_create(
                    exhibit=inquiry.exhibit,
                    email=contact_email,
                    defaults={
                        'name': full_name,
                        'phone': phone_for_contact,
                        'dwell_time': 0,
                        'call_back_request': wants_phone_contact,
                    },
                )
                if not created:
                    prospect.name = full_name or prospect.name
                    if phone_for_contact:
                        prospect.phone = phone_for_contact
                    prospect.call_back_request = wants_phone_contact
                    prospect.save(update_fields=['name', 'phone', 'call_back_request'])

                save_to_profile = request.POST.get('save_to_profile') == 'on'
                if save_to_profile:
                    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
                    updated_fields = []

                    if first_name and profile_obj.firstname != first_name:
                        profile_obj.firstname = first_name
                        updated_fields.append('firstname')
                    if last_name and profile_obj.lastname != last_name:
                        profile_obj.lastname = last_name
                        updated_fields.append('lastname')
                    if phone_for_contact and profile_obj.phone != phone_for_contact:
                        profile_obj.phone = phone_for_contact
                        updated_fields.append('phone')
                    if updated_fields:
                        profile_obj.save(update_fields=updated_fields)
                        profile = profile_obj

                    if contact_email and request.user.email != contact_email:
                        request.user.email = contact_email
                        request.user.save(update_fields=['email'])

                messages.success(request, 'Inquiry sent to the gallery owner.')
                return redirect('dashboard')
            messages.error(request, 'Could not send inquiry. Please check the form and try again.')
            return redirect('dashboard')
    collection_form = SavedCollectionForm()
    enquired_exhibit_ids = set(
        GalleryInquiry.objects.filter(user=request.user).values_list('exhibit_id', flat=True)
    )
    watching_exhibit_ids = saved_exhibit_ids - enquired_exhibit_ids

    if scanned_exhibit:
        initial_filter = 'scanned'
    elif watching_exhibit_ids:
        initial_filter = 'watching'
    elif enquired_exhibit_ids:
        # Keep the first visible state on load when all saved cards are already enquired.
        initial_filter = 'enquired'
    else:
        initial_filter = 'watching'

    profile_missing_fields = []
    if not profile or not profile.firstname:
        profile_missing_fields.append('first name')
    if not profile or not profile.lastname:
        profile_missing_fields.append('last name')
    if not request.user.email:
        profile_missing_fields.append('email')
    if not profile or not profile.phone:
        profile_missing_fields.append('phone')

    context = {
        'collection_form': collection_form,
        'saved_exhibits': saved_exhibits,
        'scanned_exhibit': scanned_exhibit,
        'enquired_exhibit_ids': enquired_exhibit_ids,
        'collections': collections,
        'featured_interest_exhibit': featured_interest_exhibit,
        'initial_filter': initial_filter,
        'profile_missing_fields': profile_missing_fields,
        'profile_first_name': (profile.firstname if profile else '') or request.user.first_name,
        'profile_last_name': (profile.lastname if profile else '') or request.user.last_name,
        'profile_phone': (profile.phone if profile else ''),
    }
    return render(request, 'users/dashboard.html', context)