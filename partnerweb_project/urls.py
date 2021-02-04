from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceViewSet
from rest_framework.routers import DefaultRouter

from tickets_handler.views import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet)

urlpatterns = [
    path('', include('tickets_handler.urls')),
    path('', include('call_center.urls')),
    path('', include('territory.urls')),
    path('', include('analytic.urls')),
    path('', include('tools.urls')),
    url(r'^$', views.redirect_auth, name='redirect_auth'),
    url(r'^', include(router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns