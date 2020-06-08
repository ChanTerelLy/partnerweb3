from django import forms
from datetime import date
from .models import Promouter
class PromoutingReportForm(forms.Form):
    addresses = forms.CharField(widget=forms.Textarea, label='Адреса')
    agent = forms.CharField(max_length=50)
    assign_to_promouter = forms.BooleanField(required=False, label='Назначить на залистовщика?')
    promouter_choice = forms.ModelChoiceField(queryset=Promouter.objects.all(), required=False,
                                              label='Выберите залистовщика')
    date = forms.DateField(label='Дата', initial=date.today())

class PromoutingReportFindForm(forms.Form):
    street = forms.CharField(max_length=50, label='Введите улицу')

class AddressToDoForm(forms.Form):
    entrance_img = forms.ImageField(label='Фото стендов')
    mailbox_img = forms.ImageField(label='Фото почтовых ящиков')

