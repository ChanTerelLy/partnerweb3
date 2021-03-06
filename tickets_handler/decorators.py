from django.shortcuts import redirect

from .models import ACL
from django.core.exceptions import PermissionDenied
import datetime

def check_access(function):
    def wrap(request, *args, **kwargs):
        try:
            request.session['operator']
        except:
            return redirect('login')
        access = ACL.objects.filter(code=request.session['operator']).first()
        if access:
            if datetime.date.today()  < access.date_end:
                raise PermissionDenied
            else:
                return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)
    return wrap