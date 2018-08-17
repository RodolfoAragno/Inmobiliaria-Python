"""inmobiliaria URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from propiedades import views

urlpatterns = [
	path('cargar/<int:dni>', views.cargar_propiedad, name='cargar_propiedad'),# /propiedades/cargar/DNI
    path('cargar', views.cargar_propiedad, name='cargar_propiedad'),# /propiedades/cargar
	path('<int:id>/modificar', views.modificar_propiedad, name='modificar_propiedad'),# /propiedades/cargar/DNI
	path('<int:id>/baja', views.eliminar_propiedad, name='eliminar_propiedad'),# /propiedades/cargar/DNI
    path('<int:id>/', views.ver_propiedad, name='ver_propiedad'),# /propiedades/ID
    path('', views.listado_propiedades, name='listado_propiedades'),# /propiedades/
]
