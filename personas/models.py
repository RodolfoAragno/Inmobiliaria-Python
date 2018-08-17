from django.db import models
from django.core.validators import MinValueValidator

class Persona(models.Model):
	# Atributos obligatorios
	dni = models.IntegerField(primary_key=True, verbose_name='DNI', validators=[MinValueValidator(0)])
	nombre = models.CharField(max_length=50, default='')
	apellido = models.CharField(max_length=50, default='')
	
	# Atributos opcionales
	email = models.EmailField(max_length=254, blank=True, default='')
	telefono = models.CharField(max_length=25, blank=True, default='')
	direccion = models.CharField(max_length=254, blank=True, default='')
	
	# Para garantes:
	ciudad = models.CharField(max_length=50, blank=True, default='Santa Fe')
	provincia = models.CharField(max_length=50, blank=True, default='Santa Fe')
	nacionalidad = models.CharField(max_length=35, blank=True, default='Argentino/a')
	
	class Meta:
		"""Meta definition for Persona."""
		verbose_name = 'Persona'
		verbose_name_plural = 'Personas'
	
	def __str__(self):
		"""Unicode representation of Persona."""
		return self.dni.__str__() + ' ' + self.apellido + ', ' + self.nombre

	def getApellidoNombre(self):
		return self.apellido + ', ' + self.nombre
	
	def getNombreApellido(self):
		return self.nombre + ' ' + self.apellido
	
	def aDiccionario(self):
		return {
			'dni': self.dni,
			'apellido': self.apellido,
			'nombre': self.nombre,
			'email': self.email,
			'telefono': self.telefono,
			'direccion': self.direccion,
			'ciudad': self.ciudad,
			'provincia': self.provincia,
			'nacionalidad': self.nacionalidad
		}
		
	def fromPost(self, post_obj ):
		# Falta validar los datos
		self.dni = post_obj.get("dni")
		self.nombre = post_obj.get("nombre", '')
		self.apellido = post_obj.get("apellido", '')
		self.email = post_obj.get("email", '')
		self.telefono = post_obj.get("telefono", '')
		self.direccion = post_obj.get("direccion", '')
		self.ciudad = post_obj.get("ciudad", '')
		self.provincia = post_obj.get("provincia", '')
		self.nacionalidad = post_obj.get("nacionalidad", '')
		return self

class Inquilino(models.Model):
	persona = models.OneToOneField(to=Persona, on_delete=models.CASCADE, primary_key=True)
	activo = models.BooleanField(default=True)

class Propietario(models.Model):
	persona = models.OneToOneField(to=Persona, on_delete=models.CASCADE, primary_key=True)
	activo = models.BooleanField(default=True)