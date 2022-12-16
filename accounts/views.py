from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from accounts.forms import UserLoginForm


def login_view(request):
    form = UserLoginForm(request.POST or None)

    # Если форма валидна
    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        # Авторизация пользователя
        user = authenticate(request, username=email, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')
