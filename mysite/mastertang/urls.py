from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('user/', views.user, name='user'),
    path("test/", views.test, name="test"),
    path("y86_64-IDE/", views.toIDE, name="IDE"),
    path("chat/", views.tochat, name="chat"),
]
