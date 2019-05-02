from django.shortcuts import render, redirect
from personas.models import Persona, Inquilino, Propietario
from contratos.models import Contrato
from datetime import date

def listado_inquilinos(request):
    inqs = Inquilino.objects.filter(activo=True).order_by("persona__apellido","persona__nombre")
    return render(request, 'personas/listado_inquilinos.html', {'inquilinos':inqs})

def listado_propietarios(request):
    props = Propietario.objects.filter(activo=True).order_by("persona__apellido","persona__nombre")
    return render(request, 'personas/listado_propietarios.html', {'propietarios': props})

def cargar_propietario(request, dni=None):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        # Buscar si no hay una persona con ese DNI
        try:
            pers = Persona.objects.get(dni=dni)
        except:
            # No está cargado
            pers = Persona()
        pers.fromPost(request.POST)
        prop = Propietario(persona=pers, activo=True)
        pers.save()
        prop.save()
        return redirect('ver_propietario', dni)
    else:
        if dni is None:
            dni = request.GET.get("dni")

        if dni is not None:
            # Modificar
            try:
                persona = Persona.objects.get(dni=dni)
            except:
                return render(request, 'personas/alta_propietario.html', {"persona":Persona(dni=dni)})
            else:
                return render(request, 'personas/modificar_propietario.html', {"persona":persona})
        else: # Cargar
            return render(request, 'personas/alta_propietario.html')

def cargar_inquilino(request, dni=None):#Carga y activa un inquilino
    if request.method == 'POST':
        dni = request.POST.get("dni")
        # Buscar si no hay una persona con ese DNI
        try:
            persona = Persona.objects.get(dni=dni)
        except:
            # No está cargado
            persona = Persona().fromPost(request.POST)
            try:
                persona.save()
            except:
                return render(request, 'personas/alta_inquilino.html', {'error': "Error al guardar la persona.", 'persona': persona})
            else:
                inq = Inquilino(persona=persona)
                inq.save()
                return redirect('listado_inquilinos')
        else:
            #hay persona
            persona.fromPost(request.POST)
            persona.save()

            try: 
                inq = Inquilino.objects.filter(persona=persona)[0]
            except:
                #no hay inquilino
                inq = Inquilino(persona = persona )
            
            inq.activo = True
            inq.save()
            return redirect('listado_inquilinos')
    else:
        if dni is None:
            dni = request.GET.get("dni")
        if dni is not None:
            # Modificar
            try:
                persona = Persona.objects.get(dni=dni)
            except:
                return render(request, 'personas/alta_inquilino.html', {"persona":Persona(dni=dni)})
            else:
                return render(request, 'personas/modificar_inquilino.html', {"persona":persona})
        else: # Cargar
            return render(request, 'personas/alta_inquilino.html')

def eliminar_inquilino(request, dni):
	try:
		inq = Inquilino.objects.get(persona__dni=dni)
	except:
		return redirect('listado_inquilinos')
	else:
		if request.method == 'POST':
			inq.activo = False
			inq.save()
			return redirect('listado_inquilinos')
		else:
			# aca verificar q se puede dar de baja
			# (no esta en algun contrato activo)
			return render(request, 'personas/baja_inquilino.html', { 'inquilino': inq })

def eliminar_propietario(request, dni):
	try:
		prop = Propietario.objects.get(persona__dni=dni)
	except:
		return redirect('listado_propietarios')
	else:
		if request.method == 'POST':
			prop.activo = False
			prop.save()
			return redirect('listado_propietarios')
		else:
			# aca verificar q se puede dar de baja
			# (no esta en algun contrato activo)
			return render(request, 'personas/baja_propietario.html', { 'propietario': prop })

def ver_inquilino(request, dni):
    try:
        inquilino = Inquilino.objects.get(persona__dni=dni)
    except:
        return render(request, 'personas/ver_inquilino.html', {
            'inquilino': None,
        })
    contratos = Contrato.objects.filter(inquilino__persona__dni=dni).order_by('-id').prefetch_related()
    activos = []
    inactivos = []
    for contrato in contratos:
        if contrato.activo:
            activos.append(contrato)
        else:
            inactivos.append(contrato)
    return render(request, 'personas/ver_inquilino.html', {
        'inquilino': inquilino,
        'contratos_activos': activos,
        'contratos_inactivos': inactivos,
		'hoy': date.today()
    })

def ver_propietario(request, dni):
    try:
        propietario = Propietario.objects.get(persona__dni=dni)
        propiedades = propietario.propiedad_set.all()
    except:
        return render(request, 'personas/ver_propietario.html', { 
            'propietario': None,
            'propiedades': None
        })
    contratos = Contrato.objects.filter(propiedad__propietario__persona__dni=dni).order_by('-id').prefetch_related()
    activos = []
    inactivos = []
    for contrato in contratos:
        if contrato.activo:
            activos.append(contrato)
        else:
            inactivos.append(contrato)
    return render(request, 'personas/ver_propietario.html', { 
        'propietario': propietario,
        'propiedades': propiedades,
        'contratos_activos': activos,
        'contratos_inactivos': inactivos,
		'hoy': date.today()
    })