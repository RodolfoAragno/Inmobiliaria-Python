from django.db import models
from django.contrib.postgres.fields import ArrayField
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
	
	monto_primer_anio = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None) # monto fijo mensual del alquiler
	monto_segundo_anio = models.DecimalField(max_digits=12, decimal_places=2, null=True, default=None)
	montos = ArrayField(
		models.DecimalField(max_digits=12, decimal_places=2),
		size=4,
		null=True,
		default=None,
	)

	fecha_firma = models.DateField(null=True, default=None)
	
	activo = models.BooleanField(default=True)# para borrarlos
	garantes = models.ManyToManyField(Persona, related_name='+')

	@property
	def fecha_fin_primer_semestre(self):
		return self.fecha_inicio + relativedelta(months=6) - relativedelta(days=1)

	@property
	def fecha_inicio_segundo_semestre(self):
		return self.fecha_inicio + relativedelta(months=6)

	@property
	def fecha_fin_segundo_semestre(self):
		return self.fecha_inicio + relativedelta(months=12) - relativedelta(days=1)

	@property
	def fecha_inicio_tercer_semestre(self):
		return self.fecha_inicio + relativedelta(months=12)

	@property
	def fecha_fin_tercer_semestre(self):
		return self.fecha_inicio + relativedelta(months=18) - relativedelta(days=1)

	@property
	def fecha_inicio_cuarto_semestre(self):
		return self.fecha_inicio + relativedelta(months=18)

	@property
	def fecha_fin_cuarto_semestre(self):
		return self.fecha_inicio + relativedelta(months=24) - relativedelta(days=1)
	
	@property
	def es_semestral(self):
		return self.montos[0] != self.montos[1] or self.montos[2] != self.montos[3]

	def save(self, *args, **kwargs):
		parametros = Parametros.cargar()
		super().save(*args, **kwargs)
	
	def generar_documento(self):
		texto_garantes = "El/la señor/a NOMBRE, D.N.I. DNI, domiciliado/a en calle DOMICILIO, ciudad de Santa Fe, Provincia de Santa Fe"
		document = None
		if self.es_semestral:
			document = MailMerge(os.path.join(TEMPLATES_DIR, 'documentos/contrato_semestral.docx'))
			document.merge(
				INQUILINO_NOMBRE=self.inquilino.persona.getNombreApellido().upper(),
				INQUILINO_DNI=self.inquilino.persona.dni.__str__(),
				INQUILINO_NACIONALIDAD=self.inquilino.persona.nacionalidad,
				PROPIEDAD_DIRECCION=self.propiedad.direccion,
				PROPIEDAD_CARACTERISTICAS=self.propiedad.descripcion,
				CONTRATO_FECHA_INICIO=format_date(self.fecha_inicio, format='long', locale='es'),
				CONTRATO_FECHA_FIN=format_date(self.fecha_fin_cuarto_semestre, format='long', locale='es'),
				CONTRATO_FECHA_MITAD=format_date(self.fecha_fin_segundo_semestre, format='long', locale='es'),
				CONTRATO_FECHA_INICIO_SEGUNDO_SEMESTRE=format_date(self.fecha_inicio_segundo_semestre, format='long', locale='es'),
				CONTRATO_FECHA_INICIO_TERCER_SEMESTRE=format_date(self.fecha_inicio_tercer_semestre, format='long', locale='es'),
				CONTRATO_FECHA_INICIO_CUARTO_SEMESTRE=format_date(self.fecha_inicio_cuarto_semestre, format='long', locale='es'),
				CONTRATO_FECHA_FIN_TERCER_SEMESTRE=format_date(self.fecha_fin_tercer_semestre, format='long', locale='es'),
				CONTRATO_PERIODO1=format_date(self.fecha_inicio, format='long', locale='es') + ' al ' + format_date(self.fecha_fin_primer_semestre, format='long', locale='es'),
				CONTRATO_CUOTA1=num2words(self.montos[0], lang='es').upper() + ' (${})'.format(self.montos[0]),
				CONTRATO_CUOTA2=num2words(self.montos[1], lang='es').upper() + ' (${})'.format(self.montos[1]),
				CONTRATO_CUOTA3=num2words(self.montos[2], lang='es').upper() + ' (${})'.format(self.montos[2]),
				CONTRATO_CUOTA4=num2words(self.montos[3], lang='es').upper() + ' (${})'.format(self.montos[3]),
				GARANTES=texto_garantes,
				CONTRATO_FECHA_FIRMA=format_date(self.fecha_firma, format='long', locale='es'),
				FIRMAS_INQUILINO=self.inquilino.persona.getNombreApellido().upper(),
				GARANTE1_NOMBRE="GARANTE 1",
				GARANTE2_NOMBRE="GARANTE 2",
				GARANTE3_NOMBRE="GARANTE 3",
				GARANTE4_NOMBRE="GARANTE 4",
				GARANTE5_NOMBRE="GARANTE 5",
			)
		else:
			document = MailMerge(os.path.join(TEMPLATES_DIR, 'documentos/contrato.docx'))
			document.merge(
				INQUILINO_NOMBRE=self.inquilino.persona.getNombreApellido().upper(),
				INQUILINO_DNI=self.inquilino.persona.dni.__str__(),
				INQUILINO_NACIONALIDAD=self.inquilino.persona.nacionalidad,
				PROPIEDAD_DIRECCION=self.propiedad.direccion,
				PROPIEDAD_CARACTERISTICAS=self.propiedad.descripcion,
				CONTRATO_FECHA_INICIO=format_date(self.fecha_inicio, format='long', locale='es'),
				CONTRATO_FECHA_FIN=format_date(self.fecha_fin_cuarto_semestre, format='long', locale='es'),
				CONTRATO_FECHA_MITAD=format_date(self.fecha_inicio_tercer_semestre, format='long', locale='es'),
				CONTRATO_PERIODO1=format_date(self.fecha_inicio, format='long', locale='es') + ' al ' + format_date(self.fecha_fin_segundo_semestre, format='long', locale='es'),
				CONTRATO_CUOTA1=num2words(self.montos[0], lang='es').upper() + ' (${})'.format(self.montos[0]),
				CONTRATO_CUOTA2=num2words(self.montos[2], lang='es').upper() + ' (${})'.format(self.montos[2]),
				GARANTES=texto_garantes,
				CONTRATO_FECHA_FIRMA=format_date(self.fecha_firma, format='long', locale='es'),
				FIRMAS_INQUILINO=self.inquilino.persona.getNombreApellido().upper(),
				GARANTE1_NOMBRE="GARANTE 1",
				GARANTE2_NOMBRE="GARANTE 2",
				GARANTE3_NOMBRE="GARANTE 3",
				GARANTE4_NOMBRE="GARANTE 4",
				GARANTE5_NOMBRE="GARANTE 5",
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
		for semestre in range(4):
			for _ in range(6):
				mes = MesContrato()
				mes.contrato = self
				mes.fecha_vencimiento = aux_fecha_vencimiento
				mes.monto = self.montos[semestre]
				mes.save(creando=True)
				aux_fecha_vencimiento += relativedelta(months = 1)
		return
	
	def generar_poder(self):
		parametros = Parametros.cargar()
		domicilio = None
		if self.propiedad.propietario.persona.direccion and self.propiedad.propietario.persona.direccion != '':
			domicilio = ', domiciliado/a en calle ' + self.propiedad.propietario.persona.direccion
		ciudad = None
		if self.propiedad.propietario.persona.ciudad and self.propiedad.propietario.persona.ciudad != '':
			ciudad = ', de la Ciudad de ' + self.propiedad.propietario.persona.ciudad
		provincia = None
		if self.propiedad.propietario.persona.provincia and self.propiedad.propietario.persona.provincia != '':
			provincia = ', Provincia de ' + self.propiedad.propietario.persona.provincia
		telefono = None
		if self.propiedad.propietario.persona.telefono and self.propiedad.propietario.persona.telefono != '':
			telefono = ', Teléfono Nro.: ' + self.propiedad.propietario.persona.telefono
		descrip = None
		if self.propiedad.descripcion and self.propiedad.descripcion != '':
			descrip = ' compuesta de: ' + self.propiedad.descripcion
		document = None
		if self.es_semestral:
			document = MailMerge(os.path.join(TEMPLATES_DIR, 'documentos/autorizacion_semestral.docx'))
			document.merge(
				FECHA_FIRMA_TEXTO=format_date(date.today(), format='long', locale='es'),
				NOMBRE=self.propiedad.propietario.persona.getNombreApellido().upper(),
				DNI=str(self.propiedad.propietario.persona.dni),
				DOMICILIO=domicilio,
				CIUDAD=ciudad,
				PROVINCIA=provincia,
				TELEFONO=telefono,
				PROPIEDAD_DIRECCION=self.propiedad.direccion,
				PROPIEDAD_CIUDAD=self.propiedad.ciudad,
				PROPIEDAD_PROVINCIA=self.propiedad.provincia,
				PROPIEDAD_DESCRIPCION=self.propiedad.descripcion,
				IMPORTE_MENSUAL=str(self.montos[0]),
				IMPORTE_PROPIETARIO=str((self.montos[0] - self.montos[0] * parametros.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)),
				IMPORTE_MENSUAL_2=str(self.montos[1]),
				IMPORTE_PROPIETARIO_2=str((self.montos[1] - self.montos[1] * parametros.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)),
				IMPORTE_MENSUAL_3=str(self.montos[2]),
				IMPORTE_PROPIETARIO_3=str((self.montos[2] - self.montos[2] * parametros.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)),
				IMPORTE_MENSUAL_4=str(self.montos[3]),
				IMPORTE_PROPIETARIO_4=str((self.montos[3] - self.montos[3] * parametros.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)),
				PLAZO=str((self.fecha_fin_cuarto_semestre - self.fecha_inicio).days) + ' días'
			)
		else:
			document = MailMerge(os.path.join(TEMPLATES_DIR, 'documentos/autorizacion.docx'))
			document.merge(
				FECHA_FIRMA_TEXTO=format_date(date.today(), format='long', locale='es'),
				DNI=str(self.propiedad.propietario.persona.dni),
				DOMICILIO=domicilio,
				CIUDAD=ciudad,
				PROVINCIA=provincia,
				TELEFONO=telefono,
				PROPIEDAD_DIRECCION=self.propiedad.direccion,
				PROPIEDAD_CIUDAD=self.propiedad.ciudad,
				PROPIEDAD_PROVINCIA=self.propiedad.provincia,
				PROPIEDAD_DESCRIPCION=self.propiedad.descripcion,
				IMPORTE_MENSUAL=str(self.montos[0]),
				IMPORTE_PROPIETARIO=str((self.montos[0] - self.montos[0] * parametros.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)),
				IMPORTE_MENSUAL_2=str(self.montos[2]),
				IMPORTE_PROPIETARIO_2=str((self.montos[2] - self.montos[2] * parametros.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)),
				PLAZO=str((self.fecha_fin_cuarto_semestre - self.fecha_inicio).days) + ' días'
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

	@classmethod
	def from_db(cls, db, field_names, values):
		instance = super().from_db(db, field_names, values)
		instance.calcular_intereses()
		return instance

	def save(self, creando=False):
		if self.id is not None:
			self.calcular_intereses()
		if creando:
			params = Parametros.cargar()
			self.monto_propietario = (self.monto - self.monto * params.porcentaje_propietario).quantize(decimal.Decimal('10.55'), rounding=decimal.ROUND_DOWN)
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
			self.intereses = (self.totalACobrar(conIntereses=False) * parametros.interes_diario * dias_interes).quantize(decimal.Decimal('0.1234'), rounding=decimal.ROUND_DOWN)
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
