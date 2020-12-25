# chat/views.py
from django.shortcuts import render

def index(request):
    title = "Chat Room Request"
    return render(request, 'chat/index.html', {"title":title})

def room(request, room_name):
    title = "Chat Room"
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'title': title,
    })