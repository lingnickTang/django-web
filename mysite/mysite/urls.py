from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("mastertang.urls")),
    path("chat/",include("chat.urls")),
    path("IDE/",include("IDE.urls")),
]
