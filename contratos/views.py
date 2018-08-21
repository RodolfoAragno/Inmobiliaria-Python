from django.shortcuts import render, redirect
from contratos.models import Contrato, MesContrato, ConceptoVario
from personas.models import Persona, Inquilino
from propiedades.models import Propiedad
from parametros.models import Parametros
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from babel.dates import format_date
from num2words import num2words
import os
import json
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')

def pagar(request, id_contrato, id_mes):
	mes = MesContrato.objects.get(pk=id_mes)
	if request.method == 'POST':
		mes.fecha_pagado_propietario = date.today()
		mes.save()
		return redirect(pagar, id_contrato, id_mes)
	else:
		return render(request, 'cobros_pagos/pagar_mes.html', {
			'mes': mes,
			'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es')
		})

def recibo_pago(request, id_contrato, id_mes):
	mes = MesContrato.objects.get(pk=id_mes)
	total = mes.totalAPagar()
	txt = '{} con {} centavos'.format(
		num2words(int(total), lang='es'),
		num2words(int((total - int(total)) *100), lang='es')
	)
	return render(request, 'cobros_pagos/recibo_pago.html', {
		'mes': mes,
		'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es'),
		'total_texto': txt
	})


def cobrar(request, id_contrato, id_mes):
	mes = MesContrato.objects.get(pk=id_mes)
	if request.method == 'POST':
		mes.fecha_pagado_inquilino = date.today()
		mes.save()
		return redirect(cobrar, id_contrato, id_mes)
	else:
		return render(request, 'cobros_pagos/cobrar_mes.html', {
			'mes': mes,
			'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es'),
			'email_cuerpo': 'dfgdfgd\nsaidjasdasd'
		})

def recibo_cobro(request, id_contrato, id_mes):
	mes = MesContrato.objects.get(pk=id_mes)
	total = mes.totalACobrar()
	txt = '{} con {} centavos'.format(
		num2words(int(total), lang='es'),
		num2words(int((total - int(total)) *100), lang='es')
	)
	return render(request, 'cobros_pagos/recibo_cobro.html', {
		'mes': mes,
		'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es'),
		'total_texto': txt
	})

def grilla(request, id_contrato):
	parametros = Parametros.cargar()
	if parametros.id is None:
		return render(request, 'error/parametros.html')
	contrato = Contrato.objects.get(pk=id_contrato)
	return render(request, 'contratos/grilla.html', {'contrato': contrato})

def listado_contratos(request):
	return render(request, 'contratos/listado_contratos.html', {
		'contratos': Contrato.objects.filter(activo=True, fecha_fin__gte=date.today().isoformat())
	})

def ver_contrato(request, id_contrato):
	return render(request, 'contratos/ver_contrato.html', {
		'contrato': Contrato.objects.get(pk=id_contrato)
	})

def alta_contrato(request):
	parametros = Parametros.cargar()
	if parametros.id is None:
		return render(request, 'error/parametros.html')
	if request.method == 'POST':
		datos = json.loads(request.POST.get('datos_contrato'))
		contrato = Contrato()
		contrato.propiedad = Propiedad.objects.get(pk=datos['id_propiedad'])
		if contrato.propiedad.getContratoActivo() is not None:
			return render(request, 'contratos/alta_contrato.html', {
				'incremento_anual': str(incremento).replace(',', '.'),
				'error': 'La propiedad ya tiene un contrato activo.'
			})
		contrato.inquilino = Inquilino.objects.get(persona__dni=datos['dni_inquilino'])
		contrato.fecha_inicio = date.fromtimestamp(int(datos['fecha_inicio']) / 1000);
		contrato.monto_primer_anio = datos['monto']
		contrato.save()
		for dni_garante in json.loads(datos['garantes']):
			contrato.garantes.add(Persona.objects.get(pk=dni_garante))
		contrato.save()
		return redirect('ver_contrato', contrato.id)
	else:
		incremento = parametros.incremento_segundo_anio + 1
		return render(request, 'contratos/alta_contrato.html', {
			'incremento_anual': str(incremento).replace(',', '.'),
			'texto_incremento': str((incremento - 1) * 100).replace('.', ','),
			'texto_porcentaje': str(parametros.porcentaje_propietario * 100).replace('.', ',')
		})

def firmar_contrato(request, id_contrato):
	contrato = Contrato.objects.get(pk=id_contrato)
	if request.method == 'POST':
		contrato.fecha_firma = datetime.strptime(request.POST.get('fecha_firma'), "%d/%m/%Y")
		contrato.save()
		contrato.generar_meses()
		return redirect('ver_contrato', id_contrato)
	else:
		return render(request, 'contratos/firmar_contrato.html', {'contrato': contrato})

def baja_contrato(request, id_contrato):
	contrato = Contrato.objects.get(pk=id_contrato)
	if request.method == 'POST':
		contrato.activo = False
		contrato.save()
		return redirect('listado_contratos')
	else:
		return render(request, 'contratos/baja_contrato.html', {'contrato': contrato})

def descargar_documento(request, id_contrato):
	contrato = Contrato.objects.get(pk=id_contrato)
	dir_guardado = os.path.join(MEDIA_ROOT, 'documentos/contratos/', '{}_{}_{}.docx'.format(
		contrato.id, contrato.inquilino.persona.apellido, contrato.propiedad.propietario.persona.apellido)
	)
	if contrato.fecha_firma is None or not os.path.isfile(dir_guardado):
		contrato.generar_documento()
	with open(dir_guardado, 'rb') as fh:
		response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
		response['Content-Disposition'] = 'inline; filename=' + os.path.basename(dir_guardado)
		return response

def descargar_autorizacion(request, id_contrato):
	contrato = Contrato.objects.get(pk=id_contrato)
	dir_guardado = os.path.join(MEDIA_ROOT, 'documentos/contratos/', 'autorizacion_{}_{}.docx'.format(
		contrato.propiedad.propietario.persona.apellido, contrato.propiedad.direccion)
	)
	if contrato.fecha_firma is None or not os.path.isfile(dir_guardado):
		contrato.generar_poder()
	with open(dir_guardado, 'rb') as fh:
		response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
		response['Content-Disposition'] = 'inline; filename=' + os.path.basename(dir_guardado)
		return response


def open_connection(email, contrasenia):
	conn = smtplib.SMTP_SSL('smtp.gmail.com')
	conn.login(email, contrasenia)
	return conn

def enviar_email(request, id_contrato, id_mes):
	mes = MesContrato.objects.get(pk=id_mes)
	parametros = Parametros.cargar()
	if parametros.id is None:
		return render(request, 'error/parametros.html')
	if request.method == 'POST':
		email_inquilino = request.POST.get('email_inquilino')
		if email_inquilino is not None:
			adress_inquilino = email_inquilino.split('@')
		email_asunto = request.POST.get('asunto')
		email_mensaje = request.POST.get('cuerpo')
		email_detalle = request.POST.get('detalle')
		email_inmobiliaria = parametros.email_direccion.split('@')
		email_contrasenia = parametros.email_contrasenia

		try:
			conn = open_connection(parametros.email_direccion, email_contrasenia)
			msg = EmailMessage()
			msg['Subject'] = email_asunto
			msg['From'] = Address("Gazze Inmobiliaria", email_inmobiliaria[0], email_inmobiliaria[1])
			msg['To'] = (Address(mes.contrato.inquilino.persona.getNombreApellido(), adress_inquilino[0], adress_inquilino[1]))
			msg.set_content("""\
			<html>
				<head></head>
				<body>
					<p>{}</p>
					{}
				</body>
			</html>
			""".format(email_mensaje, email_detalle), subtype='html')
			conn.send_message(msg)
		except smtplib.SMTPAuthenticationError:
			return render(request, 'cobros_pagos/email.html', {
				'mes': mes,
				'asunto': email_asunto,
				'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es'),
				'cuerpo': email_mensaje,
				'email_inquilino': email_inquilino,
				'error': 'El email y/o contraseña de la inmobiliaria son inválidos.'
			})
		except:
			return render(request, 'cobros_pagos/email.html', {
				'mes': mes,
				'asunto': email_asunto,
				'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es'),
				'cuerpo': email_mensaje,
				'email_inquilino': email_inquilino,
				'error': 'Error al enviar el email.'
			})
		else:
			conn.close()
			return render(request, 'cobros_pagos/email.html', {
				'mes': mes,
				'enviado': True
			})
	else:
		return render(request, 'cobros_pagos/email.html', {
			'mes': mes,
			'asunto': parametros.email_asunto,
			'texto_mes': format_date(mes.fecha_vencimiento, format='MMMM yyyy',locale='es'),
			'cuerpo': parametros.email_mensaje,
			'email_inquilino': mes.contrato.inquilino.persona.email
		})