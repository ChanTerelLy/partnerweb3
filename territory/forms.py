from django import forms
from datetime import date

class PromoutingReportForm(forms.Form):
    addresses = forms.CharField(widget=forms.Textarea, label='Адреса')
    agent = forms.CharField(max_length=50)
    date = forms.DateField(label='Дата', initial=date.today())

class PromoutingReportFindForm(forms.Form):
    street = forms.CharField(max_length=50, label='Введите улицу')

class AddressToDoForm(forms.Form):
    entrance_img = forms.ImageField(label='Фото стендов')
    mailbox_img = forms.ImageField(label='Фото почтовых ящиков')