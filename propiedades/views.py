from django.shortcuts import render, redirect
from propiedades.models import Propiedad
from personas.models import Propietario
from datetime import date


def listado_propiedades(request):
	propiedades = Propiedad.objects.filter(propietario__activo=True).filter(activa=True)
	return render(request, 'propiedades/listado_propiedades.html', {'propiedades': propiedades})

def cargar_propiedad(request, dni=None):
	if request.method == 'POST':
		propiedad = Propiedad().fromPost(request.POST)
		propietario = Propietario.objects.get(persona__dni=request.POST.get("dni"))
		propiedad.propietario = propietario
		propiedad.activa = True
		propiedad.save()
		return redirect('ver_propiedad', propiedad.id)
	else:
		if dni is None:
			return render(request, 'propiedades/alta_propiedad.html')
		else:
			try:
				propietario = Propietario.objects.get(persona__dni=dni)
			except:
				return render(request, 'propiedades/alta_propiedad.html', {'propietario_error': True})
			return render(request, 'propiedades/alta_propiedad.html', {'propietario':propietario})

def ver_propiedad(request, id):
	try:
		propiedad = Propiedad.objects.get(id=id)
	except:
		propiedad = None
	contrato = None
	for c in propiedad.contratos.all():
		print(c.fecha_fin)
		if c.activo and c.fecha_fin >= date.today():
			contrato = c
	return render(request, 'propiedades/ver_propiedad.html', {
		'propiedad':propiedad,
		'contrato': contrato
	})

def modificar_propiedad(request, id):
	if request.method == 'POST':
		propiedad = Propiedad.objects.get(id=id)
		propiedad.fromPost(request.POST)
		propiedad.activa = True
		propiedad.save()
		return redirect('ver_propiedad', propiedad.id)
	else:
		try:
			propiedad = Propiedad.objects.get(id=id)
		except:
			propiedad = None
		return render(request, 'propiedades/modificar_propiedad.html', {'propiedad':propiedad})

def eliminar_propiedad(request, id):
	if request.method == 'POST':
		propiedad = Propiedad.objects.get(id=id)
		propiedad.activa = False
		propiedad.save()
		return redirect('listado_propiedades')
	else:
		try:
			propiedad = Propiedad.objects.get(id=id)
		except:
			propiedad = None
		return render(request, 'propiedades/baja_propiedad.html', {'propiedad':propiedad})