from django.shortcuts import render
from .models import Subscribers
from django.http import HttpResponse, JsonResponse
from django.core import serializers

# Create your views here.

def get_subscriber(request):
    sub = Subscribers.objects.filter(called=False).first()
    sub.called = True
    sub.save()
    serialized_obj = serializers.serialize('json', [sub])
    return JsonResponse(serialized_obj, safe=False)

def set_subscriber(request):
    id_sub = request.GET.get('id_sub')
    status = request.GET.get('status')
    sub = Subscribers.objects.get(id=id_sub)
    sub.status_result = status
    return JsonResponse({'response' : 'OK'})
