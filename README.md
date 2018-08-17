# Inmobiliaria

## Correr servidor Python:

* Setear `SECRET_KEY`:
	* [Generar](https://www.miniwebtool.com/django-secret-key-generator/)
	* `export SECRET_KEY=<llave>`
* Setear `DATABASE_URL`:
	* Ejemplo para Postgres:
		* `postgres://<usuario>:<contraseña>@<host>:<puerto>/<base_de_datos>`
* Levantar servidor web de Python.

## Configuración de nginx

```
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    gzip	on;
    server {
		location /static/ {
			root <carpeta principal>;
			expires 30d;
		}
		
		location / {
			proxy_pass http://127.0.0.1:8000/;
			proxy_set_header Host $host;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		}
    }
}
```

## Otros

* Agregar key SSH de la computadora servidor en Configuración > Repositorio > Deploy keys.