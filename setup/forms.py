from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from setup.models import BtUser


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        result = super().clean()
        entered_user = BtUser.objects.get(username=result['username'])
        entered_password = result['password']
        users = BtUser.objects.all()

        if not entered_user:
            self.add_error('username', f'Nie ma takiego użytkownika {entered_user.first_name}')
        elif not entered_user.is_active:
            raise ValidationError('Użytkownik nieaktywny')

        if entered_password != entered_user.password:
            self.add_error('password', 'Błędne hasło')



