# urls.py

from django.urls import path
from . import views

app_name = 'Users'

urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.SignInView.as_view(), name='sign-in'),
    path('logout/', views.logout_view, name='sign-out'),
    path('dashboard/', views.index, name='dashboard'), 
]