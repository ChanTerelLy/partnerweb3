from django import forms

class AuthForm(forms.Form):
    sell_code = forms.CharField(required=False)
    operator = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)

class DateTimeForm(forms.Form):
    datetime = forms.DateField(widget=forms.DateTimeInput(attrs={'readonly':'readonly'}),  required=False)
    status = forms.ChoiceField(choices=[(21, 'Позвонить клиенту'),(2028,'Отказ 2028')], required=False)
    comments = forms.Field()