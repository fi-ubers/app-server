# Manual de Proyecto

## Introducción

Este proyecto consiste de un servidor Web HTTP accesible a través de una REST API para la aplicación **FIUBER**. **FIUBER** es una aplicación intencionada para conectar a los pasajeros con los conductores de vehículos que ofrecen servicio de transporte particular. Esta aplicación permite a los potenciales pasajeros: obtener estimaciones de costo un viaje antes de realizarlo, elegir al conductor que desean, solicitar al chofer y una vez que terminan el viaje realizar el pago utilizando cualquiera de los medios de pago disponibles. 

Este sistema se basa en un diseño de 3 capas que permite el funcionamiento de la aplicación:

+ [Cliente](https://github.com/fi-ubers/client) 
+ **App** **Server**
+ [Shared Server](https://github.com/fi-ubers/shared-server)

Este proyecto provee una implementación para la capa de App Server del sistema. En el archivo *simpleAPI.yml* puede encontrarse documentación detallada sobre la interfaz provista por el servidor para comunicarse con una aplicación cliente. 

## Arquitectura y Diseño

Para implementar esta aplicación se utilizó una arquitectura de 3 capas (3-Tier), donde el *App Server* representa la capa lógica o de negocios. La capa de datos es provista por el [Shared Server](https://github.com/fi-ubers/shared-server) y es allí donde se almacenan los datos de los usuarios de la aplicación, tanto conductores como pasajeros, los viajes y los servidores activos. La aplicación está pensada para permitir la coexistencia de múltiples *App Servers* que utilizan al *Shared Server* como servicio web para almacenar datos y como punto de acceso a la API de pagos, que se provee de forma externa.

Diagrama general de capas:

![alt text](https://github.com/fi-ubers/app-server/blob/master/docs/ArchDiagram.png)

## Casos de uso y diagramas de flujo

## Módulos y paquetes

**TODO**: diagrama de paquetes/esquema(?)
 
+ *src/main/myApp.py* : aquí se encuentran definidos todos los *endpoints* definidos para la REST API y su vinculación a los *recursos* designados para cada uno.
 
+ *src/main/resources/* : es el directorio que contiene todos los *recursos* o *handlers* encargados de manejar los requests realizados a los endpoints definidos en *myApp.py*

+ *src/main/com/* : aquí residen los archivos que permiten la comunicación con otras aplicaciones. 
  
  + *ServerRequest.py* es el módulo que permite realizar requests al *Shared Server*.
 
  + *NotificationManager.py* es el módulo que permite conectarse con el servicio de *Firebase* para enviar notificaciones a los clientes.
	
  + *TokenGenerator.py* es el módulo encargado de la validación de los *tokens* de seguridad utilizados en la comunicación entre las tres capas.
	
+ *src/main/mongodb/* : 
	
  + *MongoController.py* : es el módulo encargado de la conexión con la base de datos remota o local, si la anterior no estuviera definida.
 
+ *src/main/model/* : en este directorio se encuentran los archivos encargados de modelar las estructuras de las entidades conceptuales importantes del sistema para garantizar la compatibilidad entre los datos intercambiados entre el *Cliente* y el *Shared Server*.
 
  + *TripStates.py* : en este módulo se definen todos los estados posibles de un viaje. Permite mappear la información de un viaje desde el formato recibido desde el cliente al formato de viajes compatible con el *Shared Server*.
 
  + *Client.py* : en este módulo se definen todos los estados posibles de un usuario (pasajero o chofer). Permite mappear los datos de los usuarios a un formato compatible con el utilizado por la base de datos local.


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






