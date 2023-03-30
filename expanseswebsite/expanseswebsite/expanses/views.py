from django.shortcuts import render
# Create your views here.

def index(request):
    return render(request, 'expanses/index.html')

def add_expanses(request):
    return render(request, 'expanses/add_expanse.html')

