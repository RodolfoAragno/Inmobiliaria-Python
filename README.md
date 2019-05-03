# Inmobiliaria

## Correr servidor Python:

1. Setear `SECRET_KEY`:
    * [Generar](https://www.miniwebtool.com/django-secret-key-generator/)
    * `export SECRET_KEY=<llave>`
2. Setear `DATABASE_URL`:
	* Ejemplo para Postgres:
		* `postgres://<usuario>:<contraseña>@<host>:<puerto>/<base_de_datos>`
3. Levantar servidor web de Python.

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

## Dominio

Para ingresar al servidor con un dominio falso. Por ejemplo: `http://inmobiliaria.xyz`
1. Setear IP fija en el router. Ej. `192.168.0.25`
2. Setear IP como servidor DNS.
3. Instalar `dnsmasq`.
4. Configuración:
	```
	>>> /etc/hosts
	<IP FIJA DEL SERVIDOR>	<nombre.xyz>

	>>> /etc/dnsmasq
	domain-needed
	bogus-priv
	local=/<nombre.xyz>/
	listen-address=127.0.0.1
	listen-address=<IP FIJA DEL SERVIDOR>
	bind-interfaces
	expand-hosts
	domain=<xyz>
	```

## Otros

* **Permisos del repositorio:**
    1. Agregar key SSH pública de la computadora servidor en Configuración > Repositorio > Deploy keys

## Key de VM de Gazze

.ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDZag+3CCi4AK/mXGHAn3HEiaOGpAvz5bUV4lZXgUsBuPXvkPvUUE1NmJOrDTgCP8Fc3xyMq3sJjxjwo34mS/U7twmdgnvFB/mh6ofuQQu9MSnQA7qvGi7Hyx8kI2CMMJxaB+ZSfxMS+Pn+lmiuV3aRq8xED6ondOljiQtrvdO3qf+TOUTjpWfer3xxCjtP14hYmsjEt3D5l29Fnt94monLiboaCdxUs7lYzgk/w5cWsxDzQ3uvIhrGfk2ENLFIB8cD+1hi7S5h2x6d12FTKM4WvM9qpbzTAYCQqg3/PVo45+ygw6+6Hy42OdNXaLZ1gxWKbpWUSxBp5QBe6efTvQT/ root@inmobiliaria
