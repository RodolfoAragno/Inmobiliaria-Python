from django.shortcuts import render, redirect
from parametros.models import Parametros
from django.core.exceptions import ValidationError

def parametros(request):
	parametros = Parametros.cargar()
	if request.method == 'POST':
		parametros.porcentaje_propietario = request.POST.get('porcentaje_propietario', None)
		parametros.incremento_segundo_anio = request.POST.get('incremento_anual', None)
		parametros.interes_diario = request.POST.get('interes', None)
		parametros.email_direccion = request.POST.get('email_direccion', None)
		parametros.email_asunto = request.POST.get('email_asunto', None)
		parametros.email_mensaje = request.POST.get('email_mensaje', None)
		contr = request.POST.get('email_contrasenia', None)
		if contr is not None and contr != '':
			parametros.email_contrasenia = contr

		try:
			parametros.save()
			parametros.porcentaje_propietario *= 100
			parametros.incremento_segundo_anio *= 100
			parametros.interes_diario *= 100
			return render(request, 'parametros/parametros.html', {
				'parametros': parametros,
				'guardado': True
			})
		except ValidationError as err:
			parametros.porcentaje_propietario *= 100
			parametros.incremento_segundo_anio *= 100
			parametros.interes_diario *= 100
			return render(request, 'parametros/parametros.html', {
				'parametros': parametros,
				'error': err
			})
	else:
		if parametros.id is None:
			return render(request, 'parametros/parametros.html')
		parametros.porcentaje_propietario *= 100
		parametros.incremento_segundo_anio *= 100
		parametros.interes_diario *= 100
		return render(request, 'parametros/parametros.html', {'parametros': parametros})