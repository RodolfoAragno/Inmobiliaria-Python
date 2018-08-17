from django.db import models
from personas.models import Persona, Propietario

class Propiedad(models.Model):
	direccion = models.CharField(max_length=250, verbose_name='dirección')
	descripcion = models.TextField(verbose_name='descripción')
	ciudad = models.CharField(blank=True, max_length=50)
	provincia = models.CharField(blank=True, max_length=50)
	activa = models.BooleanField(default=True)
	propietario = models.ForeignKey(Propietario, on_delete=models.DO_NOTHING)
	
	def __str__(self):
		return '#' + str(self.id) + ' ' + self.direccion
	
	def getContratoActivo(self):
		for contrato in self.contratos.all():
			if contrato.activo:
				return contrato
		return None
	
	def generar_poder(self):
		pass
	
	def fromPost(self, post_obj):
		self.direccion = post_obj.get("direccion", '')
		self.descripcion = post_obj.get("descripcion", '')
		self.ciudad = post_obj.get("ciudad", '')
		self.provincia = post_obj.get("provincia", '')
		return self
