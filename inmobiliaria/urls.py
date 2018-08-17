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
from django.urls import path, include
from inmobiliaria import views

urlpatterns = [
    path('personas/', include('personas.urls')),
    path('propiedades/', include('propiedades.urls')),
    path('contratos/', include('contratos.urls')),
    path('parametros/', include('parametros.urls')),
    path('ajax/', include('ajax.urls')),
    path('', views.inicio, name='inicio'),
]
