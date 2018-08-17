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
from personas import views

urlpatterns = [
    path('inquilinos/cargar/<int:dni>', views.cargar_inquilino, name='modificar_inquilino'),
    path('inquilinos/cargar', views.cargar_inquilino, name='cargar_inquilino'),
    path('inquilinos/eliminar/<int:dni>', views.eliminar_inquilino, name='eliminar_inquilino'),
    path('inquilinos/<int:dni>', views.ver_inquilino, name='ver_inquilino'),
    path('inquilinos/', views.listado_inquilinos, name='listado_inquilinos'),
    path('propietarios/cargar/<int:dni>', views.cargar_propietario, name='modificar_propietario'),
    path('propietarios/cargar', views.cargar_propietario, name='cargar_propietario'),
    path('propietarios/eliminar/<int:dni>', views.eliminar_propietario, name='eliminar_propietario'),
    path('propietarios/<int:dni>', views.ver_propietario, name='ver_propietario'),
    path('propietarios/', views.listado_propietarios, name='listado_propietarios'),
]
