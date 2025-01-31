from django.shortcuts import render
from django.http import HttpResponse

rooms=[
    {'id': '1', 'name':'lets learn python'},
    {'id': '2', 'name':'front end developer'},
    {'id': '3', 'name':'use django'}
]

def home(request):
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)

def room(request,pk):
    room = None
    for i in rooms:
        if i['id'] == int(pk):
            room = i
    return render(request, 'base/room.html',{'room': room})
# Create your views here.
