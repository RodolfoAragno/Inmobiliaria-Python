from django.urls import path
from contratos import views

urlpatterns = [
	path('<int:id_contrato>/facturacion/cobrar/<int:id_mes>/email', views.enviar_email, name='enviar_email'),
    path('cargar', views.alta_contrato, name='cargar_contrato'),
    path('<int:id_contrato>/baja', views.baja_contrato, name='baja_contrato'),
    path('<int:id_contrato>/documentos/contrato', views.descargar_documento, name='descargar_contrato'),
    path('<int:id_contrato>/documentos/autorizacion', views.descargar_autorizacion, name='descargar_autorizacion'),
    path('<int:id_contrato>/firmar', views.firmar_contrato, name='firmar_contrato'),
    path('<int:id_contrato>/facturacion', views.grilla, name='grilla'),
    path('<int:id_contrato>/facturacion/pagar/<int:id_mes>/recibo', views.recibo_pago, name='recibo_pago'),
    path('<int:id_contrato>/facturacion/pagar/<int:id_mes>', views.pagar, name='pagar'),
    path('<int:id_contrato>/facturacion/cobrar/<int:id_mes>/recibo', views.recibo_cobro, name='recibo_cobro'),
    path('<int:id_contrato>/facturacion/cobrar/<int:id_mes>', views.cobrar, name='cobrar'),
    path('<int:id_contrato>/', views.ver_contrato, name='ver_contrato'),
    path('', views.listado_contratos, name='listado_contratos'),
]
