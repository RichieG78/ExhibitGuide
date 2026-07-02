from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from .forms import UserRegisterForm  #Import added


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('simulate-scan')  # Redirect to the simulate-scan view after successful registration
    else:
        form = UserRegisterForm() #UserRegisterForm instead of UserCreationForm
    return render(request, 'users/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Signed in successfully.')
            return redirect(request.POST.get('next') or 'simulate-scan')
    else:
        form = AuthenticationForm(request)

    return render(request, 'users/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return render(request, 'users/logout.html')
