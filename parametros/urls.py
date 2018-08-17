from django.urls import path
from parametros import views

urlpatterns = [
	path('', views.parametros, name='parametros'),
]