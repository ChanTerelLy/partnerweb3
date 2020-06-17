from django.contrib import admin
from .models import Workers, ACL, AdditionalTicket, Employer, ChiefInstaller, Installer, AUP

admin.site.register(Workers)
admin.site.register(ACL)
admin.site.register(AdditionalTicket)
admin.site.register(Employer)
admin.site.register(ChiefInstaller)
admin.site.register(Installer)
admin.site.register(AUP)