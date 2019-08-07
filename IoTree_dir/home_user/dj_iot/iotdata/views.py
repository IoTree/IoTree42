from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'iotdata/home.html')


def about(request):
    return render(request, 'iotdata/about.html', {'title': 'About'})
