from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from tickets_handler import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', include('tickets_handler.urls')),
    path('', include('call_center.urls')),
    path('', include('territory.urls')),
    # path('', include('analytic.urls')),
    url(r'^$', views.redirect_auth, name='redirect_auth'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns