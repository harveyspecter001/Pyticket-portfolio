from django.urls import path,include
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import static
from .views import * 
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('',views.login.as_view(), name='login'),
    path('accounts/profile/',views.home.as_view(), name='home'),
    path('logout/',views.logout.as_view(), name='logout'),
    path('add_server/',views.add_server, name='add_server'),
    path('api/update_server_info/', UpdateServerInfoAPIView.as_view(), name='update_server_info'),

    path('configure_bot/<int:server_id>/', views.configure_bot.as_view(), name='configure_bot'),


    #path('configure_bot/<int:server_id>/', views.configure_bot.as_view(), name='configure_bot'),
    
    
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    
    path('api/bot_configuration/<int:server_id>/', BotConfigView.as_view()),



    path('api-auth/', include('rest_framework.urls')),

    path('accounts/',include('allauth.urls')),

    #path('login/', views.login, name='login'),
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
    