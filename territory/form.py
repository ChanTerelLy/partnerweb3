from django import forms

class AddressToDoForm(forms.Form):
    promouter = forms.CharField()
    address = forms.CharField()
    entrance_img = forms.ImageField()
    mailbox_img = forms.ImageField()