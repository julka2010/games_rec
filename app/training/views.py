from django.http import HttpResponse

from training.tasks import train_everything

def everything(request):
    train_everything.delay()
    return HttpResponse('Training has started')
