from django import forms
from .models import Auth, DateTime

class AuthForm(forms.ModelForm):
    class Meta:
        model = Auth
        fields = ('sell_code', 'operator','password')
        widget = {'password' : forms.TextInput(attrs = {'class' : 'form-control'})}

class DateTimeForm(forms.Form):
    datetime = forms.DateField(widget=forms.DateTimeInput(attrs={'readonly':'readonly'}),  required=False)
    comments = forms.CharField(max_length=1000, required=False)
    status = forms.ChoiceField(choices=[(21, 'Позвонить клиенту'),(2028,'Отказ 2028')], required=False)
    # subject = forms.CharField(max_length=100)
    # message = forms.CharField(widget=forms.Textarea)
    # sender = forms.EmailField()
    # cc_myself = forms.BooleanField(required=False)