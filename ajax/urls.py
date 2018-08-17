from django.urls import path
from ajax import views

urlpatterns = [
	path('modificar_mes', views.modificar_mes),
	path('meses/<int:id_contrato>', views.meses_contrato),
	path('propiedades', views.propiedades),
	path('inquilinos', views.inquilinos),
	path('garantes', views.garantes),
]