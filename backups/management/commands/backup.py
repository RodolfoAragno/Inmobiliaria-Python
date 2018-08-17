from django.core.management.base import BaseCommand, CommandError
import csv
import os
from propiedades.models import Propiedad
from personas.models import Persona, Inquilino, Propietario
from datetime import date


class Command(BaseCommand):
	help = 'Backup de datos'

	def handle(self, *args, **options):
		BASE_DIR = os.environ.get('GAZZE_BACKUP_DIR')
		carpeta = os.path.join(BASE_DIR, date.today().isoformat())
		if not os.path.exists(carpeta):
			os.makedirs(carpeta)
		
		propiedades = Propiedad.objects.all()
		with open(os.path.join(carpeta, 'propiedades.csv'), 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for prop in propiedades:
				writer.writerow([str(prop.id), prop.direccion, prop.descripcion, prop.ciudad, prop.provincia, str(prop.propietario.persona.dni)])
		
		personas = Persona.objects.all()
		with open(os.path.join(carpeta, 'personas.csv'), 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for persona in personas:
				writer.writerow([str(persona.dni), persona.apellido, persona.nombre, persona.email, persona.telefono, persona.ciudad, persona.provincia, persona.nacionalidad])
		
		inquilinos = Inquilino.objects.all()
		with open(os.path.join(carpeta, 'inquilinos.csv'), 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for inquilino in inquilinos:
				writer.writerow([str(inquilino.persona.dni), str(inquilino.activo)])
		
		propietarios = Propietario.objects.all()
		with open(os.path.join(carpeta, 'inquilinos.csv'), 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for propietario in propietarios:
				writer.writerow([str(propietario.persona.dni), str(propietario.activo)])
		
		self.stdout.write(self.style.SUCCESS('Backup exitoso.'))
		