from django.core.management.base import BaseCommand, CommandError
from contratos.models import Contrato
from parametros.models import Parametros
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Convierte contratos con actualizaciones anuales a semestrales'
    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Testear que se convirtieron los valores',
        )
        parser.add_argument(
            '--guardar',
            action='store_true',
            help='Escribir cambios a la DB',
        )

    def handle(self, *args, **options):
        if options['test']:
            for contrato in Contrato.objects.all():
                assert contrato.montos is not None, "Contrato #{} no tiene montos semestrales".format(contrato.pk)
                assert len(contrato.montos) == 4, "Contrato #{} tiene montos semestrales pero != 4 semestres".format(contrato.pk)
                assert contrato.monto_primer_anio is None, "Contrato #{} tiene formato de montos viejos".format(contrato.pk)
                assert contrato.monto_segundo_anio is None, "Contrato #{} tiene formato de montos viejos".format(contrato.pk)
            self.stdout.write("Todo OK!")
        else:
            params = Parametros.objects.get(pk=1)
            incremento = params.incremento_segundo_anio
            cant = 0
            for contrato in Contrato.objects.all():
                editado = False
                if contrato.montos is None or len(contrato.montos) != 4:
                    assert contrato.monto_primer_anio is not None, "Contrato #{} no se puede convertir; monto 1er anio = null".format(contrato.pk)
                    monto = contrato.monto_primer_anio
                    montos = []
                    montos.append(monto)
                    montos.append(monto)
                    montos.append(monto + monto * incremento)
                    montos.append(monto + monto * incremento)
                    contrato.montos = montos
                    contrato.monto_primer_anio = None
                    contrato.monto_segundo_anio = None
                    editado = True
                if editado:
                    cant += 1
                    if options['guardar']:
                        contrato.save()
            if options['guardar']:
                self.stdout.write("Todo OK! Editados: {} contratos".format(cant))
            elif cant > 0:
                self.stdout.write("Para editar: {} contratos -> Ejecutar con --guardar para modificarlos".format(cant))
            else:
                self.stdout.write("Todo OK, nada para cambiar")
