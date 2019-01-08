from celery.decorators import task
from django.http import HttpResponse
from django.shortcuts import render

from training.tasks import add

def everything(request):
    return HttpResponse('Training has started')
