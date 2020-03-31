from django.contrib import admin
from .models import Workers, ACL, AdditionalTicket, Employer
admin.site.register(Workers)
admin.site.register(ACL)
admin.site.register(AdditionalTicket)
admin.site.register(Employer)