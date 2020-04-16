from django import forms

class MozForm(forms.Form):
    moz_file = forms.FileField(label='Загрузите moz файл')
