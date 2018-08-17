from django.shortcuts import render
from parametros.models import Parametros

def inicio(request):
	parametros = Parametros.cargar()
	return render(request, 'inicio.html', {
		'parametros_no_seteados': parametros.id is None
	})