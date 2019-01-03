from django.http import HttpResponse
from django.shortcuts import render

def everything(request):
    return HttpResponse('You are about to train everything')
