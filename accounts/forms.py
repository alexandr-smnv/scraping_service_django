from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password


User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # clean -используется для проверки корректности данных КОНКРЕТНОГО поля формы и отвечает за вызов методов
    # to_python, validate и run_validators в правильном порядке и передачу их ошибок.
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email').strip()
        password = self.cleaned_data.get('password')

        if email and password:
            qs = User.objects.filter(email=email)
            # Метод exists() возвращает True, если возвращаемый QuerySet содержит один или несколько объектов,
            # и значение False, если QuerySet пустой.
            if not qs.exists():
                raise forms.ValidationError('Такого пользователя не существует')
            # Проверка правильности пароля
            if not check_password(password, qs[0].password):
                raise forms.ValidationError('Неверный пароль')
            # Проверка на возможность авторизации
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Данный аккаунт отключен')

        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label='Введите email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Введите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Введите пароль еще раз',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return data['password2']
