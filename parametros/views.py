from django.shortcuts import render, redirect
from parametros.models import Parametros
from django.core.exceptions import ValidationError

def parametros(request):
	parametros = Parametros.cargar()
	if request.method == 'POST':
		porc_prop = request.POST.get('porcentaje_propietario', None)
		incr_anual = request.POST.get('incremento_anual', None)
		int_diario = request.POST.get('interes', None)
		email_dir = request.POST.get('email_direccion', None)
		email_asu = request.POST.get('email_asunto', None)
		email_msj = request.POST.get('email_mensaje', None)
		parametros.porcentaje_propietario = porc_prop
		parametros.incremento_segundo_anio = incr_anual
		parametros.interes_diario = int_diario
		parametros.email_direccion = email_dir
		parametros.email_asunto = email_asu
		parametros.email_mensaje = email_msj
		try:
			parametros.save()
			return render(request, 'parametros/parametros.html', {
				'parametros': parametros,
				'guardado': True
			})
		except ValidationError as err:
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