# Manual de Proyecto

## Introducción

El proyecto **FIUBER** consistió en la implementación de una aplicación de viajes una aplicación intencionada para conectar a los pasajeros con los conductores de vehículos que ofrecen servicio de transporte particular.

El alcance del proyecto consiste en la implementación completa de la arquitectura de la aplicación, que está dada en 3 capas: la aplicación android de los clientes, un application server (por región) que contiene la lógica de negocios, y un shared server que ofrece servicio de base de datos centralizado, y funcionalidades compartidas.

Cada una de las tres capas, con su respectiva documentación y manual de instalación puede encontrarse en los siguientes links:

- [Cliente](https://github.com/fi-ubers/client) 
- [Application Server](https://github.com/fi-ubers/app-server)
- [Shared Server](https://github.com/fi-ubers/shared-server)

Un esquema de la arquitectura completa se muestra a continuación. Más adelante se indican los requerimientos de cada una de las partes, y para cada una de ellas la planificación y las decisiones de desarrollo más importantes.

![Diagrama de la arquitectura del proyecto](https://github.com/fi-ubers/app-server/blob/master/docs/ArchDiagram.png)

## Qué servicios provee FIUBER?

Esta aplicación ofrece al usuario los siguientes servicios:

- Servicio de Login de Usuarios.
- Edición y consulta de los datos de cuenta.
- Estimación de costo de viajes.
- Selección y solicitud de ruta de viaje.
- Selección y solicitud de conductor y vehículo para realizar un viaje.
- Tracking de posición de pasajeros y conductores en tiempo real (vía Google Maps).
- Servicio de pago de viaje realizado en función de la distancia recorrida.
- Consulta de historial de viajes.
- Data analytics.
- Administración de servidores y permisos de usuarios.
- Posibilidad de introducción de reglas para flexibilizar el cálculo de costos de viaje.
  
## Cliente

Consiste en una aplicación mobile para Android.

## Application Server

Un servidor web HTTP implementado en Python usando Gunicorn y Flask como frameworks.

El *Application Server* cumple la función de almacenar todos los datos pertinentes a los servicios provistos por la aplicación. Por ejemplo, los estados actuales de los usuarios y los viajes en curso se almacenan en esta capa. El *App Server* también funciona como gestor de transacciones contra el *Shared Server*, que es donde se almacenan todos los datos historicos de usuarios y viajes. Además de almacenar los datos de las operaciones en curso, el *App Server* provee la lógica de transición entre estados de los usuarios y el servicio de posicionamiento de choferes y pasajeros.

## Shared Server

Un servidor web HTTP implementado en Javascript usando nodeJs. También presenta una interfaz gráfica implementada con Angular.

## Hitos de desarrollo

El desarrollo de este proyecto fue realizado en forma incremental, de forma tal que las funcionalidades fueron incorporadas de acuerdo con los siguientes hitos:

|  CP  | Fecha | Cliente |  App Server  |  Shared Server  |  Común  |
|:---:|:---:|:----|:----------|:-----------|:-----|
|   **#1**    | 14/09 | <ul><li>Pantalla Login</li><li>Logs</li></ul> | <ul><li>REST API</li><li>Deploy en Keroku</li><li>Generación de documentación</li><li>Logs</li><li>Unit Tests</li><li>Integración con Travis</li></ul>|<ul><li>Deploy en Keroku</li><li>Generación de documentación</li><li>Servicio de gestión de App Servers</li><li>Logs</li><li>Unit Tests</li><li>Integración con Travis</li></ul>| <ul><li>Mockups</li><li>Reporte de coverage</li></ul> |
|   **#2**    | 12/10 |<ul><li>Pantalla principal</li><li>Vista perfil de usuario</li><li>Modificación perfil de usuario</li><li>Signup + Login contra App Server</li></ul>|<ul><li>Servicio de autenticación</li><li>Modificación de datos de perfil de usuario</li><li> Servicio de choferes disponibles</li><li>Modelo de datos Mongodb de perfiles/choferes</li></ul>|<ul><li>Servicio de gestión de usuarios de negocio</li><li>Servicio de gestión de datos de usuario</li><li>Modelo de datos de PostgreSql</li><li>Docker</li><li>Listado de Usuarios(backoffice)</li></ul>| <ul><li>Diseño</li><li>Modelo de datos</li></ul> |
|   **#3**    | 09/11 | <ul><li>Notificaciones push</li><li>Generación de documentación de código</li><li>Unit tests</li></ul> |  <ul><li>Servicio de posicionamiento</li><li> Servicio de viajes disponibles</li><li>Modelo de datos Mongodb completo</li></ul>  | <ul><li>Servicio de viajes</li><li>Servicio de cotización de viaje</li><li>Servicio de estado actual</li><li>Modelo de datos Postgresql completo</li><li>Estado actual (backoffice)></li><li>Historial de viajes (backoffice)></li></ul>  | <ul><li>Manual de instalación y configuración</li></ul> |
| **Entrega** | 07/12 |   -     |    -    |    -    |  <ul><li>Documentación actualizada</li><li>Funcionalidad completa</li></ul> |


