import datetime

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.forms import UserLoginForm, UserRegistrationForm, UserUpdateForm, ContactForm
from scraping.models import Error

User = get_user_model()


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
        messages.success(request, 'Пользователь успешно создан!')
        return render(request, 'accounts/register_done.html', {'new_user': new_user})

    return render(request, 'accounts/register.html', {'form': form})


def update_view(request):
    contact_form = ContactForm()
    # Проверка авторизации пользователя
    if request.user.is_authenticated:
        user = request.user
        # данные в форму передаются
        # либо из метода POST
        if request.method == 'POST':
            form = UserUpdateForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                # изменение данных пользователя
                user.city = data['city']
                user.language = data['language']
                user.send_email = data['send_email']
                user.save()
                messages.success(request, 'Данные успешно изменены!')
                return redirect('accounts:update')
        # либо начальные данные

        form = UserUpdateForm(initial={'city': user.city,
                                       'language': user.language,
                                       'send_email': user.send_email})
        return render(request, 'accounts/update.html', {'form': form, 'contact_form': contact_form})
    else:
        return redirect('accounts:login')


def delete_view(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            qs = User.objects.get(pk=user.pk)
            qs.delete()
            messages.error(request, 'Пользователь удален')

    return redirect('home')


def contact_view(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST or None)
        if contact_form.is_valid():
            data = contact_form.cleaned_data
            city = data.get('city')
            language = data.get('language')
            email = data.get('email')
            # проверка наличия данных за сегодня
            qs_errors = Error.objects.filter(timestamp=datetime.date.today())
            if qs_errors.exists():
                # получаем экземпляр класса (в списке он будет всегда один, т.к. фильтруем по дате)
                err = qs_errors.first()
                data = err.data.get('user_data', [])
                # обновляем объект
                data.append({'city': city, 'language': language, 'email': email})
                # добавляем в список user_data
                err.data['user_data'] = data
                # сохраняем в БД
                err.save()
            else:
                data = [{'city': city, 'language': language, 'email': email}]
                Error(data={'user_data': data}).save()

            messages.success(request, 'Данные отправлены администрации.')
            return redirect('accounts:update')
        else:
            return redirect('accounts:update')
    else:
        return redirect('accounts:update')


