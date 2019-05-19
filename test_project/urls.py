from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from boards import views
import beeline.views
import testing.views
from django.contrib.auth import views as auth_views


from accounts import views as accounts_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    url(r'^login_beeline$', beeline.views.auth, name='login_beeline'),
    url(r'^boards/(?P<pk>\d+)/$', views.board_topics, name='board_topics'),
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name='new_topic'),
    url('^tickets/', beeline.views.main_page, name='main_page_tickets'),
    url(r'^info/(?P<id>\d+)/$', beeline.views.ticket_info, name='ticket_info'),
    url(r'^signup/$', accounts_views.signup, name='signup'),
    path('global_search/', beeline.views.global_search, name='global_search'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    path('testing/', views.testing, name='testing'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^settings/password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    url(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),
]