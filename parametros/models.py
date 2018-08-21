from django.db import models
from django.core.exceptions import ValidationError
import decimal


# parametros = Parametros.cargar()
class Parametros(models.Model):
	porcentaje_propietario = models.DecimalField(max_digits=3, decimal_places=2)
	incremento_segundo_anio = models.DecimalField(max_digits=3, decimal_places=2)
	interes_diario = models.DecimalField(max_digits=5, decimal_places=4)
	email_direccion = models.EmailField()
	email_asunto = models.CharField(max_length=150)
	email_mensaje = models.TextField()
	email_contrasenia = models.CharField(max_length=50)

	def save(self, *args, **kwargs):
		if Parametros.objects.exists() and not self.pk:
			raise ValidationError('Ya existen parametros en la DB')
		
		if self.porcentaje_propietario is None or decimal.Decimal(self.porcentaje_propietario.replace(',', '.')) < 0:
			raise ValidationError('El porcentaje del propietario no puede estar vacío o ser menor a cero')
		if self.incremento_segundo_anio is None or decimal.Decimal(self.incremento_segundo_anio.replace(',', '.')) < 0:
			print(self.incremento_segundo_anio)
			raise ValidationError('El incremento anual no puede estar vacío o ser menor a cero')
		if self.interes_diario is None or decimal.Decimal(self.interes_diario.replace(',', '.')) < 0:
			raise ValidationError('El interés diario no puede estar vacío o ser menor a cero')
		
		self.porcentaje_propietario = decimal.Decimal(self.porcentaje_propietario.replace(',', '.')) / 100
		self.incremento_segundo_anio = decimal.Decimal(self.incremento_segundo_anio.replace(',', '.')) / 100
		self.interes_diario = decimal.Decimal(self.interes_diario.replace(',', '.')) / 100
		return super(Parametros, self).save(*args, **kwargs)
	
	@classmethod
	def cargar(cls):
		try:
			return cls.objects.get()
		except cls.DoesNotExist:
			return cls()