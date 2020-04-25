from django import forms

class PromoutingReportForm(forms.Form):
    addresses = forms.CharField(widget=forms.Textarea, label='Адреса')
    agent = forms.CharField(max_length=50)

class PromoutingReportFindForm(forms.Form):
    street = forms.CharField(max_length=50, label='Введите улицу')