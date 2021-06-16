from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from setup.models import BtUser, BtLocation


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        result = super().clean()
        entered_user = BtUser.objects.get(username=result['username'])
        if not entered_user:
            self.add_error('username', f'Nie ma takiego użytkownika {entered_user.first_name}')
        elif not entered_user.is_active:
            raise ValidationError('Użytkownik nieaktywny')


class BtUserCreationForm(forms.ModelForm):
    class Meta:
        model = BtUser
        fields = ('username',
                  'email',
                  'password',
                  'first_name',
                  'last_name',
                  'is_superuser',
                  'is_staff',
                  'is_active',
                  'department',
                  'manager',
                  'employee_level')

    def save(self, commit=True):
        user = super(BtUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LocationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    profit_center = forms.CharField(label="Profit Center", max_length=10,)

    class Meta:
        model = BtLocation
        fields = "__all__"


    def clean_profit_center(self):
        profit_center = self.cleaned_data['profit_center']
        obj = BtLocation.objects.filter(profit_center=profit_center)
        if obj:
            raise forms.ValidationError('Ten Profit center juz istnieje Proszę popraw pole Profit Center')

