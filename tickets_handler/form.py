from django import forms

class AuthForm(forms.Form):
    sell_code = forms.CharField(required=False, label='Код', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'G800-37'}))
    operator = forms.CharField(required=False, label='Номер', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'9111111111'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'text-form-control', 'placeholder':'123'}), label='Пароль', required=False)

class DateTimeForm(forms.Form):
    datetime = forms.DateField(widget=forms.DateTimeInput(attrs={'readonly':'readonly'}),label='Таймер',  required=False)
    status = forms.ChoiceField(choices=[(21, 'Позвонить клиенту'),(2028,'Отказ 2028'),(16,'ЖЗК 2028')],label='Статус', required=False)
    comments = forms.CharField(max_length=300, label='Комментарий', required=False)

class CreateTicketForm(forms.Form):
    class AjaxChoiceField(forms.ChoiceField):
        def valid_value(self, value):
            return True
    flat = forms.IntegerField(label='Квартира')
    client_surname = forms.CharField(label='Фамилия', widget=forms.TextInput(
        attrs={'class': 'text-form-control', 'placeholder': 'Иванов'}))
    client_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'Иван'}))
    client_patrony = forms.CharField(label='Отчество', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'Иванович'}))
    phone_number_1 = forms.CharField(max_length=10, label='Номер телефона', widget=forms.TextInput(attrs={'class':'text-form-control', 'placeholder':'9111111111'}))
    basket = AjaxChoiceField(label='Taриф')

class Feedback(forms.Form):
    descr = forms.CharField(widget=forms.Textarea, label='Опишите вашу проблему или предложение')
