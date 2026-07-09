from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from exhibits.models import Exhibit

from .forms import GalleryInquiryForm, SavedCollectionForm, UserAccountForm, UserProfileForm, UserRegisterForm
from .models import GalleryInquiry, Prospect, SavedCollection, SavedExhibit, UserProfile


# Create your views here.
def register(request):
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
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return render(request, 'users/logout.html')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    # Seed profile fields from auth-user names where available.
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
        account_form = UserAccountForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile_obj)
        if account_form.is_valid() and profile_form.is_valid():
            account_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated from your account information.')
            return redirect('profile')
    else:
        account_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile_obj)

    return render(
        request,
        'users/profile.html',
        {
            'account_form': account_form,
            'profile_form': profile_form,
        },
    )


@login_required
def dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    collections = SavedCollection.objects.filter(user=request.user).prefetch_related('exhibits').order_by('-created_at')
    saved_exhibits = SavedExhibit.objects.filter(user=request.user).select_related('exhibit').order_by('-saved_at')
    saved_exhibit_ids = set(saved_exhibits.values_list('exhibit_id', flat=True))

    featured_interest_exhibit = None
    scanned_exhibit = None
    interest_exhibit_from_query = request.GET.get('interest_exhibit')
    if interest_exhibit_from_query:
        request.session['interest_exhibit_id'] = str(interest_exhibit_from_query)
    interest_exhibit_id = interest_exhibit_from_query or request.session.get('interest_exhibit_id')
    if interest_exhibit_id:
        featured_interest_exhibit = Exhibit.objects.filter(id=interest_exhibit_id).first()

    if featured_interest_exhibit and featured_interest_exhibit.id not in saved_exhibit_ids:
        scanned_exhibit = featured_interest_exhibit

    if not featured_interest_exhibit:
        saved_item = saved_exhibits.first()
        if saved_item:
            featured_interest_exhibit = saved_item.exhibit

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_exhibit':
            exhibit_id = request.POST.get('exhibit_id')
            if exhibit_id:
                exhibit = Exhibit.objects.filter(id=exhibit_id).first()
                if exhibit:
                    SavedExhibit.objects.get_or_create(user=request.user, exhibit=exhibit)
                    messages.success(request, f'{exhibit.artwork} added to your watchlist.')
                else:
                    messages.error(request, 'Exhibit not found.')
            return redirect('dashboard')

        elif action == 'add_to_collection':
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
            collection_form = SavedCollectionForm(request.POST)
            if collection_form.is_valid():
                collection = collection_form.save(commit=False)
                collection.user = request.user
                collection.save()
                collection_form.save_m2m()
                messages.success(request, f'Collection "{collection.name}" created.')
                return redirect('dashboard')

        elif action == 'send_inquiry':
            inquiry_form = GalleryInquiryForm(request.POST)
            if inquiry_form.is_valid():
                missing_fields = []
                if not profile or not profile.firstname:
                    missing_fields.append('first name')
                if not profile or not profile.lastname:
                    missing_fields.append('last name')
                if not request.user.email:
                    missing_fields.append('email')
                if not profile or not profile.phone:
                    missing_fields.append('phone')

                if missing_fields:
                    messages.error(
                        request,
                        'Please complete your profile before sending an inquiry: '
                        + ', '.join(missing_fields)
                        + '.',
                    )
                else:
                    inquiry = inquiry_form.save(commit=False)
                    inquiry.user = request.user
                    inquiry.save()

                    prospect, created = Prospect.objects.get_or_create(
                        exhibit=inquiry.exhibit,
                        email=request.user.email,
                        defaults={
                            'name': f"{profile.firstname if profile else ''} {profile.lastname if profile else ''}".strip(),
                            'phone': profile.phone if profile else '',
                            'dwell_time': 0,
                            'call_back_request': True,
                        },
                    )
                    if not created:
                        prospect.name = f"{profile.firstname if profile else ''} {profile.lastname if profile else ''}".strip() or prospect.name
                        prospect.phone = profile.phone if profile else prospect.phone
                        prospect.call_back_request = True
                        prospect.save(update_fields=['name', 'phone', 'call_back_request'])

                    messages.success(request, 'Inquiry sent to the gallery owner.')
                    return redirect('dashboard')
    collection_form = SavedCollectionForm()
    inquiry_form = GalleryInquiryForm(initial={'exhibit': featured_interest_exhibit} if featured_interest_exhibit else None)
    enquired_exhibit_ids = set(
        GalleryInquiry.objects.filter(user=request.user).values_list('exhibit_id', flat=True)
    )

    context = {
        'collection_form': collection_form,
        'inquiry_form': inquiry_form,
        'saved_exhibits': saved_exhibits,
        'scanned_exhibit': scanned_exhibit,
        'enquired_exhibit_ids': enquired_exhibit_ids,
        'collections': collections,
        'featured_interest_exhibit': featured_interest_exhibit,
    }
    return render(request, 'users/dashboard.html', context)
