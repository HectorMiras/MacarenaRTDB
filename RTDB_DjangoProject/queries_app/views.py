from django.shortcuts import render
from django.http import HttpResponse
from datetime import  datetime

# Create your views here.
def home(request):
    context = {'name': 'Hector'}
    return render(request,'MainSearch.html', context)

def mainSearch(request):
    date1 = request.POST['fecha1']
    date2 = request.POST['fecha2']
    message = "Se ha realizado una búsqueda entre las fechas " + date1 + " y " + date2
    context = {'mensaje': message}
    return render(request, 'MainSearch.html', context)