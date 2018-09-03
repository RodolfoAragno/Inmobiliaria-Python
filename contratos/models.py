from django.db import models
import os
from mailmerge import MailMerge
from datetime import datetime, timedelta, date
from personas.models import Propietario, Inquilino, Persona
from propiedades.models import Propiedad
from dateutil.relativedelta import relativedelta
from num2words import num2words
from babel.dates import format_date
from parametros.models import Parametros
import decimal

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')
TEMPLATES_DIR = os.environ.get('TEMPLATES_DIR')

class Contrato(models.Model):
	"""Model definition for Contrato."""
	inquilino = models.ForeignKey(Inquilino, on_delete=models.DO_NOTHING, related_name="contratos")
	propiedad = models.ForeignKey(Propiedad, on_delete=models.DO_NOTHING, related_name="contratos")
	fecha_inicio = models.DateField(auto_now=False, auto_now_add=False)
	fecha_mitad = models.DateField(auto_now=False, auto_now_add=False)# fecha_inicio + relativedelta(years=1) - relativedelta(days=1)
	fecha_fin = models.DateField(auto_now=False, auto_now_add=False)
	
	monto_primer_anio = models.DecimalField(max_digits=12, decimal_places=2) # monto fijo mensual del alquiler
	monto_segundo_anio = models.DecimalField(max_digits=12, decimal_places=2)

	fecha_firma = models.DateField(null=True, default=None)
	
	activo = models.BooleanField(default=True)# para borrarlos
	garantes = models.ManyToManyField(Persona, related_name='+')
	
	def save(self, *args, **kwargs):
		parametros = Parametros.cargar()
		# calcula fecha_fin y fecha_mitad:
		if type(self.fecha_inicio) is str:
			self.fecha_fin = datetime.strptime(self.fecha_inicio, "%Y-%m-%d").date() + relativedelta(years=2) - relativedelta(days=1)
			self.fecha_mitad = datetime.strptime(self.fecha_inicio, "%Y-%m-%d").date() + relativedelta(years=1) - relativedelta(days=1)
		else:
			self.fecha_fin = self.fecha_inicio + relativedelta(years=2) - relativedelta(days=1)
			self.fecha_mitad = self.fecha_inicio + relativedelta(years=1) - relativedelta(days=1)
		# calcula monto del 2do año
		self.monto_segundo_anio = self.monto_primer_anio * parametros.incremento_segundo_anio
		super().save(*args, **kwargs)
	
	def generar_documento(self):
		texto_garantes = ''
		garantes = []
		for garante in self.garantes.all():
			garantes.append(garante.getNombreApellido().upper())
			texto_garantes += "El/la señor/a {}, D.N.I. {}, domiciliado/a en calle {}, ciudad de {}, Provincia de {};".format(
				garante.getNombreApellido().upper(),
				garante.dni.__str__(),
				garante.direccion,
				garante.ciudad,
				garante.provincia
			)
		for _ in range(len(garantes), 6):
			garantes.append('')
		document = MailMerge(os.path.join(TEMPLATES_DIR, 'documentos/contrato.docx'))
		document.merge(
			INQUILINO_NOMBRE=self.inquilino.persona.getNombreApellido().upper(),
			INQUILINO_DNI=self.inquilino.persona.dni.__str__(),
			INQUILINO_NACIONALIDAD=self.inquilino.persona.nacionalidad,
			PROPIEDAD_DIRECCION=self.propiedad.direccion,
			PROPIEDAD_CARACTERISTICAS=self.propiedad.descripcion,
			CONTRATO_FECHA_INICIO=format_date(self.fecha_inicio, format='long', locale='es'),
			CONTRATO_FECHA_FIN=format_date(self.fecha_fin, format='long', locale='es'),
			CONTRATO_FECHA_MITAD=format_date(self.fecha_mitad, format='long', locale='es'),
			CONTRATO_PERIODO1=format_date(self.fecha_inicio, format='long', locale='es') + ' al ' + format_date(self.fecha_fin, format='long', locale='es'),
			CONTRATO_CUOTA1=num2words(self.monto_primer_anio, lang='es').upper() + ' (${})'.format(self.monto_primer_anio),
			CONTRATO_CUOTA2=num2words(self.monto_segundo_anio, lang='es').upper() + ' (${})'.format(self.monto_segundo_anio),
			GARANTES=texto_garantes,
			CONTRATO_FECHA_FIRMA=format_date(self.fecha_firma, format='long', locale='es'),
			FIRMAS_INQUILINO=self.inquilino.persona.getNombreApellido().upper(),
			GARANTE1_NOMBRE=garantes[0],
			GARANTE2_NOMBRE=garantes[1],
			GARANTE3_NOMBRE=garantes[2],
			GARANTE4_NOMBRE=garantes[3],
			GARANTE5_NOMBRE=garantes[4],
			GARANTE6_NOMBRE=garantes[5],
		)
		dir_guardado = os.path.join(MEDIA_ROOT, 'documentos/contratos/')
		if not os.path.exists(dir_guardado):
			os.makedirs(dir_guardado)
		document.write(
			os.path.join(dir_guardado, '{}_{}_{}.docx'.format(self.id, self.inquilino.persona.apellido, self.propiedad.propietario.persona.apellido))
		)
		return
	
	def generar_meses(self):
		#generar el poder a travez de la propiedad
		aux_fecha_vencimiento = datetime(self.fecha_inicio.year, self.fecha_inicio.month, 10)
		#convertir el dia de vencimiento en parametro
		for _ in range(12):#meses del primer año
			mes = MesContrato()
			mes.contrato = self
			mes.fecha_vencimiento = aux_fecha_vencimiento
			mes.monto = self.monto_primer_anio
			mes.save(creando=True)
			aux_fecha_vencimiento += relativedelta(months = 1)
		for _ in range(12):
			mes = MesContrato()
			mes.contrato = self
			mes.fecha_vencimiento = aux_fecha_vencimiento
			mes.monto = self.monto_segundo_anio
			mes.save(creando=True)
			aux_fecha_vencimiento += relativedelta(months = 1)
		return
	
	def generar_poder(self):
		parametros = Parametros.cargar()
		document = MailMerge(os.path.join(TEMPLATES_DIR, 'documentos/autorizacion.docx'))
		document.merge(
			FECHA_FIRMA_TEXTO=format_date(date.today(), format='long', locale='es'),
			DNI=str(self.propiedad.propietario.persona.dni),
			DOMICILIO=self.propiedad.propietario.persona.direccion,
			CIUDAD=self.propiedad.propietario.persona.ciudad,
			PROVINCIA=self.propiedad.propietario.persona.provincia,
			TELEFONO=self.propiedad.propietario.persona.telefono,
			CELULAR='',
			PROPIEDAD_DIRECCION=self.propiedad.direccion,
			PROPIEDAD_CIUDAD=self.propiedad.ciudad,
			PROPIEDAD_PROVINCIA=self.propiedad.provincia,
			PROPIEDAD_DESCRIPCION=self.propiedad.descripcion,
			IMPORTE_MENSUAL=str(self.monto_primer_anio),
			IMPORTE_PROPIETARIO=str(self.monto_primer_anio * parametros.porcentaje_propietario),
			IMP_EXPENSAS='',
			PLAZO=str((self.fecha_fin - self.fecha_inicio).days)
		)
		dir_guardado = os.path.join(MEDIA_ROOT, 'documentos/contratos/')
		if not os.path.exists(dir_guardado):
			os.makedirs(dir_guardado)
		document.write(
			os.path.join(dir_guardado, 'autorizacion_{}_{}.docx'.format(self.propiedad.propietario.persona.apellido, self.propiedad.direccion))
		)
		return

def convertir_a_float(num):
	if num is None:
		return None
	else:
		return float(num)

class MesContrato(models.Model):
	"""Model definition for MesContrato."""
	contrato = models.ForeignKey(Contrato, on_delete=models.DO_NOTHING, related_name="meses")
	fecha_vencimiento = models.DateField()

	# monto fijo a pagar por el inquilino
	monto = models.DecimalField(max_digits=12, decimal_places=2)
	monto_propietario = models.DecimalField(max_digits=12, decimal_places=2)
	
	#impuestos y servicios definidos	
	api = models.DecimalField(max_digits=12, decimal_places=2, default=None, null=True)
	expensas = models.DecimalField(max_digits=12, decimal_places=2, default=None, null=True)
	agua = models.DecimalField(max_digits=12, decimal_places=2, default=None, null=True)
	tasa = models.DecimalField(max_digits=12, decimal_places=2, default=None, null=True)
	intereses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	varios_propietario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	varios_inquilino = models.DecimalField(max_digits=12, decimal_places=2, default=0)

	fecha_pagado_propietario = models.DateField(null=True, default=None)
	fecha_pagado_inquilino = models.DateField(null=True, default=None)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		#Mantener los intereses actualizados
		param = Parametros.cargar()
		if self.id != None: self.calcular_intereses()
		else self.monto_propietario = self.monto - self.monto * decimal.Decimal(param.porcentaje_propietario).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
		
	

	def save(self, creando=False):
		if not creando:
			self.calcular_intereses()
		#self.monto_propietario = self.monto - self.monto * decimal.Decimal(0.20).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
		super().save()

	def a_diccionario(self):
		pagado_inquilino = self.fecha_pagado_inquilino is not None
		pagado_propietario = self.fecha_pagado_propietario is not None
		grilla_mes = {
			'id_mes': self.id,
			'mes': format_date(self.fecha_vencimiento, format='MMMM yyyy',locale='es').upper(),
			'inquilino': convertir_a_float(self.monto),
			'propietario': convertir_a_float(self.monto_propietario),
			'tasa': convertir_a_float(self.tasa),
			'agua': convertir_a_float(self.agua),
			'api': convertir_a_float(self.api),
			'expensas': convertir_a_float(self.expensas),
			'intereses': convertir_a_float(self.intereses),
			'varios_inquilino': [],
			'varios_propietario': [],
			'pagado_inquilino': pagado_inquilino,
			'pagado_propietario': pagado_propietario
		}
		hoy = date.today()
		if not pagado_inquilino and self.fecha_vencimiento <= hoy:
			grilla_mes['dias_interes'] = (hoy - self.fecha_vencimiento).days
		varios_inquilino = ConceptoVario.objects.filter(mes=self, para_propietario=False).all()
		for vario in varios_inquilino:
			grilla_mes['varios_inquilino'].append({
				'id': vario.id,
				'descripcion': vario.descripcion,
				'monto': vario.monto
			})
		varios_propietario = ConceptoVario.objects.filter(mes=self, para_propietario=True).all()
		for vario in varios_propietario:
			grilla_mes['varios_propietario'].append({
				'id': vario.id,
				'descripcion': vario.descripcion,
				'monto': vario.monto
			})
		return grilla_mes
	
	def getDetallePropietario(self):
		detalles = []
		detalles.append({
			'descripcion': 'Monto mensual fijo {}'.format(format_date(self.fecha_vencimiento, format='MMMM yyyy',locale='es')),
			'valor': self.monto_propietario
		})
		varios_propietario = ConceptoVario.objects.filter(mes=self, para_propietario=True).all()
		for vario in varios_propietario:
			detalles.append({
				'descripcion': vario.descripcion,
				'valor': vario.monto
			})
		return detalles
	
	def getDetalle(self):
		detalles = []
		detalles.append({
			'descripcion': 'Monto mensual fijo {}'.format(format_date(self.fecha_vencimiento, format='MMMM yyyy',locale='es')),
			'valor': self.monto
		})
		if self.tasa != None and self.tasa > 0:
			detalles.append({
				'descripcion': 'Tasa {}'.format(format_date(self.fecha_vencimiento, format='MMMM yyyy',locale='es')),
				'valor': self.tasa
			})
		if self.agua != None and self.agua > 0:
			detalles.append({
				'descripcion': 'Agua {}'.format(format_date(self.fecha_vencimiento, format='MMMM yyyy',locale='es')),
				'valor': self.agua
			})
		if self.api != None and self.api > 0:
			detalles.append({
				'descripcion': 'API {}'.format(format_date(self.fecha_vencimiento, format='MMMM yyyy',locale='es')),
				'valor': self.api
			})
		if self.expensas != None and self.expensas > 0:
			detalles.append({
				'descripcion': 'Expensas {}'.format(format_date(self.fecha_vencimiento - relativedelta(months=1), format='MMMM yyyy',locale='es')),
				'valor': self.expensas
			})
		if self.intereses != None and self.intereses > 0:
			detalles.append({
				'descripcion': 'Intereses',
				'valor': self.intereses
			})
		varios_inquilino = ConceptoVario.objects.filter(mes=self, para_propietario=False).all()
		for vario in varios_inquilino:
			detalles.append({
				'descripcion': vario.descripcion,
				'valor': vario.monto
			})
		return detalles
	
	def totalACobrar(self, conIntereses=True):
		total = self.monto
		if self.api is not None:
			total += self.api
		if self.expensas is not None:
			total += self.expensas
		if self.agua is not None:
			total += self.agua
		if self.tasa is not None:
			total += self.tasa
		if self.intereses is not None and conIntereses:
			total += self.intereses
		varios_inquilino = ConceptoVario.objects.filter(mes=self, para_propietario=False).all()
		for vario in varios_inquilino:
			total += vario.monto
		return total

	def totalAPagar(self):
		total = self.monto_propietario
		varios_propietario = ConceptoVario.objects.filter(mes=self, para_propietario=True).all()
		for vario in varios_propietario:
			total += vario.monto
		return total

	def calcular_intereses(self):
		parametros = Parametros.cargar()
		pagado_inquilino = self.fecha_pagado_inquilino is not None
		if pagado_inquilino:
			return self.intereses
		hoy = date.today()
		if self.fecha_vencimiento <= hoy:
			dias_interes = decimal.Decimal((hoy - self.fecha_vencimiento).days)
			self.intereses = (self.totalACobrar(conIntereses=False) * parametros.interes_diario * dias_interes).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
		else:
			self.intereses = decimal.Decimal(0.00)
		return self.intereses

class ConceptoVario(models.Model):
	descripcion = models.CharField(max_length=150)
	monto = models.DecimalField(max_digits=12, decimal_places=2)
	a_favor = models.BooleanField(default=False)
	para_propietario = models.BooleanField(default=False)

	mes = models.ForeignKey(MesContrato, on_delete=models.DO_NOTHING, related_name='varios')

	def save(self, *args, **kwargs):
		try:
			super().save(*args, **kwargs)
		except:
			if self.id is not None:
				self.delete()
