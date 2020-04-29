from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib import admin

urlpatterns = [
    path('promouter/<int:id>/', promouter_address_to_do, name='promouter_addresses'),
    path('promouter/<int:id>/<int:house_id>/', promouter_address_to_do_detail, name='promouting_detail'),
    path(r'promoute_report/', PromouteReport.as_view(), name='promoute-report'),
    path(r'promoute_report_insert/', PromouteReportInsertForm.as_view(), name='promoute-report-insert'),
    path(r'promoute_report_find/', PromouteReportFindForm.as_view(), name='promoute-report-find'),
    path(r'promoute_report_choose/', PromouteReportTemplateView.as_view(), name='promoute-report-choose'),
]