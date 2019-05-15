from django.conf.urls import url,include
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    url(r'^$',views.home, name = 'home'),
    url(r'^login/',auth_views.LoginView.as_view(template_name = 'survey/login.html'), name = 'login'),
    url(r'logout/',views.log_out, name = 'logout'),
    url(r'^signup/',views.signup, name = 'signup'),
    url(r'^profile/',views.profile, name = 'profile'),
    url(r'^create/',views.create, name = 'create'),                                #create a new survey
    url(r'^fill/$',views.fill, name = 'fill'),                                     #gives list of public surveys
    url(r'^fill/(?P<pk>[0-9]+)$', views.check, name = 'check'),                    #authenticate private surveys
    url(r'^fill/(?P<pk>[0-9]+)/(?P<pwd>.*)$', views.take, name = 'take'),          #take the survey
    #url(r'^response/(?<pk1>[0-9]+)$', views.response, name = 'response'),
    url(r'^detail/(?P<pk>[0-9]+)$', views.detail, name = 'detail'),                #details of draft surveys
    url(r'detail/(?P<pk>[0-9]+)/add', views.addqtn, name = 'addqtn'),              #add a new question to the draft
    url(r'^results/(?P<pk>[0-9]+)', views.result, name = 'results'),               #show results
    url(r'^publish/(?P<pk>[0-9]+)', views.publish, name = 'publish'),              #publish
    url(r'^deleteqtn/(?P<pk>[0-9]+)', views.deleteqtn, name = 'deleteqtn'),        #to delete a question

]