from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib import admin

urlpatterns = [
    path('promouter/<int:id>/', promouter_address_to_do, name='promouter_addresses'),
    path('load_image/', load_image, name='load_image'),
    path('promouter_images/<int:id>/', promouter_images, name='promouter_images'),
    path(r'promoute_report/', PromouteReport.as_view(), name='promoute-report'),
    path(r'promoute_report_insert/', PromouteReportInsertForm.as_view(), name='promoute-report-insert'),
    path(r'promoute_report_find/', PromouteReportFindForm.as_view(), name='promoute-report-find'),
    path(r'promoute_report_choose/', PromouteReportTemplateView.as_view(), name='promoute-report-choose'),
    path(r'promouter_choose/', PromouterListView.as_view(), name='promouter_choose'),
]