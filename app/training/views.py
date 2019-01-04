from celery.decorators import task
from django.http import HttpResponse
from django.shortcuts import render

from training.tasks import add

def everything(request):
    res = add.delay(4, 6)
    return HttpResponse(res.get())
    return HttpResponse('You are about to train everything')
