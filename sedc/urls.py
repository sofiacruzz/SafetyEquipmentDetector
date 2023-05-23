from django.urls import path
from django.contrib import admin
from tarr import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('info/', views.info, name='info'),
    path('logout/', views.signout, name="logout"),
    path('login/', views.login, name='login'),
    path('cam/', views.cam, name='cam'),
    path('camera/', views.livefe, name="live_camera"),
    path('activate/<uidb64>/<token>', views.activate, name="activate")
]
