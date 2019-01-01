from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def user(request, username):
    return HttpResponse("Hi, you are watching a user page.")
