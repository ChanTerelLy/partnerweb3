from .models import ACL
from django.core.exceptions import PermissionDenied
import datetime

def check_access(function):
    def wrap(request, *args, **kwargs):
        try:
            request.session['operator']
        except:
            return function(request, *args, **kwargs)
        access = ACL.objects.filter(code=request.session['operator']).first()
        if access:
            if datetime.date.today()  < access.date_end:
                raise PermissionDenied
            else:
                return function(request, *args, **kwargs)
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap