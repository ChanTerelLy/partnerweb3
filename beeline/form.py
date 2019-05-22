from django import forms
from .models import Auth, DateTime

class AuthForm(forms.ModelForm):
    class Meta:
        model = Auth
        fields = ('sell_code', 'operator','password')

class DateTimeForm(forms.ModelForm):
    class Meta:
        model = DateTime
        fields = ('datetime', 'comments')
