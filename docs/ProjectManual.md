# Manual de Proyecto

## Contenidos

[TOC]

## Introducción

Este proyecto consiste de un servidor Web HTTP accesible a través de una REST API para la aplicación **FIUBER**. **FIUBER** es una aplicación intencionada para conectar a los pasajeros con los conductores de vehículos que ofrecen servicio de transporte particular. Esta aplicación permite a los potenciales pasajeros: obtener estimaciones de costo un viaje antes de realizarlo, elegir al conductor que desean, solicitar al chofer y una vez que terminan el viaje realizar el pago utilizando cualquiera de los medios de pago disponibles. 

Este sistema se basa en un diseño de 3 capas que permite el funcionamiento de la aplicación:

+ [Cliente](https://github.com/fi-ubers/client) 
+ **App** **Server**
+ [Shared Server](https://github.com/fi-ubers/shared-server)

Este proyecto provee una implementación para la capa de App Server del sistema. En el archivo *simpleAPI.yml* puede encontrarse documentación detallada sobre la interfaz provista por el servidor para comunicarse con una aplicación cliente. 

## Relación con el cliente y el *Shared Server*

Para implementar esta aplicación se utilizó una arquitectura de 3 capas (3-Tier), donde el *App Server* representa la capa lógica o de negocios. La capa de datos es provista por el [Shared Server](https://github.com/fi-ubers/shared-server) y es allí donde se almacenan los datos de los usuarios de la aplicación, tanto conductores como pasajeros, los viajes y los servidores activos. La aplicación está pensada para permitir la coexistencia de múltiples *App Servers* que utilizan al *Shared Server* como servicio web para almacenar datos y como punto de acceso a la API de pagos, que se provee de forma externa.

Diagrama general de capas:

![alt text](https://github.com/fi-ubers/app-server/blob/master/docs/ArchDiagram.png)

Por lo tanto, las funcionalidades implementadas estaban en parte limitadas por la API que se provee desde el *Shared Server*. A continuación se detallan la estructura del código del *App Server* así como los aspectos clave de la arquitectura y diseño.

## Estructura de paquetes

La división del código en distintos módulos y paquetes se resume a continuación. Todo el código relevante a las distintas funcionalidades de la aplicación se encuentran en el directorio *src/main*. El código de las pruebas unitarias y de integración se encuentra en *src/test*.

+ *src/main/myApp.py* : aquí se encuentran definidos todos los *endpoints* definidos para la REST API y su vinculación a los *recursos* designados para cada uno.

+ *src/main/resources* : es el directorio que contiene todos los controladores de los *recursos*, encargados de manejar los requests realizados a los endpoints definidos en *myApp.py*. Los controladores de de endpoints similares están definidos en un mismo archivo.

+ *src/main/com* : aquí residen los archivos que implementan módulos auxiliares. Éstos manejan tanto la comunicación con otras aplicaciones (i.e. shared-server o Google API), como el aislamiento de operaciones comunes a varios endpoints (e.g. validación de tokens del application server). 

  + *ServerRequest.py* es el módulo que permite realizar requests al *Shared Server*.
  + *NotificationManager.py* es el módulo que permite conectarse con el servicio de *Firebase* para enviar notificaciones a los clientes.
  + *TokenGenerator.py* es el módulo encargado de la validación de los *tokens* de seguridad utilizados en la comunicación entre las tres capas.
  + *ResponseMaker.py* es un módulo que encapsula la generación de respuestas de la API: serialización de json y respuestas estándar de error.
  + *Distances.py* encapsula la lógica de cálculo de distancias entre coordenadas dadas en formato latitud-longitud.

+ *src/main/mongodb* : 

  + *MongoController.py* : es el módulo encargado de la conexión con la base de datos remota o local, si la anterior no estuviera definida.

+ *src/main/mode/* : en este directorio se encuentran los archivos encargados de modelar las estructuras de las entidades conceptuales importantes del sistema para garantizar la compatibilidad entre los datos intercambiados entre el *Cliente* y el *Shared Server*.

  + *TripStates.py* : en este módulo se definen todos los estados posibles de un viaje. Permite mappear la información de un viaje desde el formato recibido desde el cliente al formato de viajes compatible con el *Shared Server*.

  + *Client.py* : en este módulo se definen todos los estados posibles de un usuario (tanto para pasajero como para chofer). Permite mappear los datos de los usuarios a un formato compatible con el utilizado por la base de datos local.


##Arquitectura y diseño

Todo el diseño del *App Server* gira en torno a las dos entidades principales dentro del dominio de negocios: los *Users* (Usuarios) y los *Trips* (Viajes). Ambas entidades son modeladas dentro del *App Server* como diccionarios, con una sierie de campos requeridos y otras opcionales. Las razones detrás de esta decisión radican en 1) la facilidad del manejo de estos objetos en python y 2) la cercanía de los mismos al formato de comunicación con el *Shared Server*.

### Users

Los *Users* dentro de la aplicación representan a una persona que utiliza un cliente en su teléfono. Así pues distinguimos dos roles dentro de los *Users*: los *Passengers* (pasajeros) y los *Drivers* (conductores). Ambos tienen la misma información básica (i.e. datos personales), pero se diferencian en algunos atributos y en cómo se relacionan con el resto de las entidades. El esquema de datos de un *User* tal y como se lo maneja en la aplicación y se lo guarda en la base de datos es el siguiente.

```json
{
  Hey:"Hola"
}
```

### Trips

Los *Trips* representan un viaje en cualquiera de sus estadíos: desde un viaje que se ha propuesto pero todavía carece de conductor, hasta uno que ha finalizado pero tiene pago pendiente. Al igual que los *Users* los *Trips* se modelan internamente como un diccionario y se guardan como tales en la base de datos. Todos los *Trips* tienen asociada necesariamente un objeto de tipo *Directions* que indica las direcciones del camino (i.e. puntos de origen y destino, tiempo estimado, distancia estimada y una serie de waypoints que marcan el camino paso a paso).

El estado de un viaje se codifica en un campo especial dentro de su estructura, y éste a su vez indica la validez y o necesidad de incluir los otros campos. La estructura completa de un viaje es la siguiente:

```json

```

### Diagramas de estados



## Dependencias y herramientas


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

## Bugs conocidos y puntos a mejorar

Debido a restricciones temporales, existen algunos aspectos de este proyecto que requieren ser mejorados o concluidos. A continuación, realizamos una breve descripción de las falencias y bugs detectados hasta el momento:

+ **Controles de concurrencia en la base de datos:** actualmente no existen controles de concurrencia sobre la base de datos. Como se mencionó anteriormente, uno de los objetivos de esta aplicación es que puedan coexistir varias instancias de *App Server* trabajando sobre una misma base hosteada en la web (salvo que por algún motivo se trabaje sobre una base de datos instanciada en forma local). Debido a que en MONGODB no existe el concepto de transacción para garantizar la integridad de los datos, estos controles deben realizarse en forma manual. En nuestra implementación, estos controles no están implementados, pudiendo ocasionarse una *race condition* si varios usuarios quisieran realizar modificaciones sobre la base al mismo tiempo.






