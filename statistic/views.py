from django.shortcuts import render
from tickets_handler.beeline_parser.manager import NewDesign
from .models import MonthReport
from django.http import HttpResponse
def parse_statistic(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    MonthReport.parse_statistic(auth)
    return HttpResponse('Fine')