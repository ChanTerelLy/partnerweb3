from django import forms

class AuthForm(forms.Form):
    sell_code = forms.CharField(required=False, label='Код   ', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'G800-37'}))
    operator = forms.CharField(required=False, label='Номер ', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'9111111111'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'text-form-control', 'placeholder':'123'}), label='Пароль', )

class DateTimeForm(forms.Form):
    datetime = forms.DateField(widget=forms.DateTimeInput(attrs={'readonly':'readonly'}),label='Таймер',  required=False)
    status = forms.ChoiceField(choices=[(21, 'Позвонить клиенту'),(2028,'Отказ 2028')],label='Статус', required=False)
    comments = forms.CharField(max_length=300, label='Коммент')