from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from accounts.forms import UserLoginForm, UserRegistrationForm


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


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        # commit - предзапись пользователя
        new_user = form.save(commit=False)
        # шифрование пользователя
        new_user.set_password(form.cleaned_data['password'])
        # сохранение пользователя
        new_user.save()
        return render(request, 'accounts/register_done.html', {'new_user': new_user})

    return render(request, 'accounts/register.html', {'form': form})
