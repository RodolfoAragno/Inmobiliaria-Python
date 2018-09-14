from django.shortcuts import render
from django.http import JsonResponse
from contratos.models import Contrato, MesContrato, ConceptoVario
from propiedades.models import Propiedad
from personas.models import Inquilino, Persona
import decimal
from datetime import date
from babel.dates import format_date
import json

def convertir_a_float(num):
	if num is None:
		return None
	else:
		return float(num)


def modificar_mes(request):
	if request.method == 'POST':
		id_mes = request.POST.get('id_mes')
		mes = MesContrato.objects.get(pk=id_mes)
		impuesto = request.POST.get('impuesto')
		if impuesto == 'varios_inquilino':
			nuevo_valor = json.loads(request.POST.get('nuevo_valor'))
			for vario in nuevo_valor:
				if vario['descripcion'] == '' or vario['monto'] == '':
					if int(vario['id']) > 0:
						c = ConceptoVario.objects.get(pk=vario['id'])
						c.delete()
				else:
					if int(vario['id']) < 0:
						c = ConceptoVario()
					else:
						c = ConceptoVario.objects.get(pk=vario['id'])
					c.descripcion = vario['descripcion']
					c.monto = vario['monto']
					c.mes = mes
					c.save()
		elif impuesto == 'varios_propietario':
			nuevo_valor = json.loads(request.POST.get('nuevo_valor'))
			for vario in nuevo_valor:
				if vario['descripcion'] == '' or vario['monto'] is None or vario['monto'] == '':
					if int(vario['id']) > 0:
						c = ConceptoVario.objects.get(pk=vario['id'])
						c.delete()
				else:
					if int(vario['id']) < 0:
						c = ConceptoVario()
					else:
						c = ConceptoVario.objects.get(pk=vario['id'])
					c.descripcion = vario['descripcion']
					c.monto = vario['monto']
					c.mes = mes
					c.para_propietario = True
					c.save()
		else:
			nuevo_valor = request.POST.get('nuevo_valor')
			if nuevo_valor == '':
				nuevo_valor = None
			else:
				nuevo_valor = decimal.Decimal(nuevo_valor).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
			if impuesto == 'tasa':
				mes.tasa = nuevo_valor
			elif impuesto == 'agua':
				mes.agua = nuevo_valor
			elif impuesto == 'api':
				mes.api = nuevo_valor
			elif impuesto == 'expensas':
				mes.expensas = nuevo_valor
			mes.save()
		return JsonResponse(mes.a_diccionario())


def meses_contrato(request, id_contrato):
	if request.method == 'POST':
		pass# guardar mes que cambia
	else:
		meses = MesContrato.objects.filter(contrato__id=id_contrato).order_by('fecha_vencimiento').all()
		resultado = []
		for mes in meses:
			resultado.append(mes.a_diccionario())
		return JsonResponse(resultado, safe=False)

def propiedades(request):
	dni = request.GET.get('dni')
	apellido = request.GET.get('apellido')
	direccion = request.GET.get('direccion')
	resultado = []
	if dni + apellido + direccion == '':
		return JsonResponse(resultado, safe=False)
	
	props = Propiedad.objects.all()
	if dni != '':
		props = props.filter(propietario__persona__dni=dni)
	if direccion != '':
		props = props.filter(direccion__icontains=direccion)
	if apellido != '':
		props = props.filter(propietario__persona__apellido__icontains=apellido)
	
	for propiedad in props:
		p = {
			'id': propiedad.id,
			'direccion': propiedad.direccion,
			'nombre_propietario': propiedad.propietario.persona.getApellidoNombre(),
			'dni_propietario': propiedad.propietario.persona.dni,
			'tiene_contrato': propiedad.getContratoActivo() is not None
		}
		resultado.append(p)
	return JsonResponse(resultado, safe=False)

def inquilinos(request):
	dni = request.GET.get('dni')
	nombre = request.GET.get('nombre')
	resultado = []
	if dni != '' and nombre != '':
		inqs = Inquilino.objects.filter(persona__dni=dni).filter(persona__apellido__icontains=nombre)
	elif dni != '':
		inqs = Inquilino.objects.filter(persona__dni=dni)
	elif nombre != '':
		inqs = Inquilino.objects.filter(persona__apellido__icontains=nombre)
	else:
		return JsonResponse(resultado, safe=False)
	for inquilino in inqs:
		i = {
			'dni': inquilino.persona.dni,
			'nombre': inquilino.persona.getApellidoNombre()
		}
		resultado.append(i)
	return JsonResponse(resultado, safe=False)