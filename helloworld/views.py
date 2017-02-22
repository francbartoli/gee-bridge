from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse(
        'Hello, World. This is Django running on Google App Engine')
