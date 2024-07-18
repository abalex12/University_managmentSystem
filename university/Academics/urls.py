# urls.py

from django.urls import path
from . import views

app_name = 'Academics'
urlpatterns = [
   
    path('course_registration/', views.course_registration, name='course_registration'),
]