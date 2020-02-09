from django import forms

class AuthForm(forms.Form):
    sell_code = forms.CharField(required=False, label='Код', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'G800-37'}))
    operator = forms.CharField(required=False, label='Номер', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'9111111111'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'text-form-control', 'placeholder':'123'}), label='Пароль', required=False)

class DateTimeForm(forms.Form):
    datetime = forms.DateField(widget=forms.DateTimeInput(attrs={'readonly':'readonly'}),label='Таймер',  required=False)
    status = forms.ChoiceField(choices=[(21, 'Позвонить клиенту'),(2028,'Отказ 2028')],label='Статус', required=False)
    comments = forms.CharField(max_length=300, label='Комментарий', required=False)

class CreateTicketForm(forms.Form):
    flat = forms.IntegerField(required=False, label='Квартира')
    client_surname = forms.CharField(required=False, label='Фамилия', widget=forms.TextInput(
        attrs={'class': 'text-form-control', 'placeholder': 'Иванов'}))
    client_name = forms.CharField(required=False, label='Имя', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'Иван'}))
    client_patrony = forms.CharField(required=False, label='Отчество', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'Иванович'}))
    phone_number_1 = forms.CharField(required=False, label='Номер телефона', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'9111111111'}))
    basket = forms.ChoiceField(required=False, label='Тариф')

class Feedback(forms.Form):
    descr = forms.CharField(widget=forms.Textarea, label='Опишите вашу проблему или предложение')