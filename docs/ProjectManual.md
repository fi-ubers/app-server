# Manual de Proyecto

## Introducción

## Arquitectura y Diseño

## Módulos y paquetes


## Herramientas utilizadas

Esta sección está destinada a mencionar las herramientas, librerías y APIs más relevantes utilizadas en este proyecto. Destacamos que esta no pretende ser una descripción de todas las librerías utilizadas, sino una breve mención de aquellas más relevantes para la funcionalidad de este proyecto.

- **GUnicorn** + **Flask**
	Este proyecto consiste en un servidor HTTP basado en *GUnicorn*. Para confeccionar la REST API que permite la comunicación con el servidor, se utilizó un framework para Python llamado *Flask*. 
		
- **Google Maps API**
	Se utilizó *Google Maps API* para obtener recorridos de viaje para los vehículos a partir del origen y el destino deseado. A partir de la información provista por Google Directions el usuario de la aplicación puede realizar un request al endpoint /directions para obtener tanto el recorrido como la estimación del costo de viaje.
		
- **Firebase**
	Se utilizó firebase como servicio web para poder proveer un servicio de mensajería (chat) entre el viajero y el conductor. Adicionalmente se utilizó Firebase para enviar notificaciones de eventos (como mensajes nuevos o la cancelación de un viaje) a los usuarios de la aplicación. 
		
- **Docker**
	Para asegurar la flexibilidad y garantizar la compatibilidad en distintas plataformas, se utilizó Docker + Docker Compose. Existen 2 containers principales, uno para la base de datos y otro para la aplicación. Los archivos de configuración de docker pueden encontrarse en el directorio raíz del proyecto. En estos archivos se definen los nombres, puertos y propiedades principales de los containers, así como también las variables de entorno y dependencias de cada uno:

	 + *Dockerfile*
	
	 + *docker-compose.yml*
		
- **MongoDB**
	Mongo Database es el sistema de base de datos (NoSQL) seleccionado para este proyecto. Existe una base de test definida en el archivo *docker-compose.yml* que será la utilizada por el servidor como base default. El usuario puede optar por mantener esta base o definir la propia en el archivo citado. De no encontrarse una definición se utiliza el servicio de Mongo localmente.

## Algoritmos relevantes
	
	
	
## Bugs conocidos y puntos a mejorar



