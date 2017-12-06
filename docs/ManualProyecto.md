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

## Shared Server

Un servidor web HTTP implementado en Javascript usando nodeJs. También presenta una interfaz gráfica implementada con Angular.

## Hitos de desarrollo

El desarrollo de este proyecto fue realizado en forma incremental, de forma tal que las funcionalidades fueron incorporadas de acuerdo con los siguientes hitos:


## Diagrama de estados de los usuarios

![Diagrama de estados de los pasajeros](https://github.com/fi-ubers/app-server/blob/master/docs/PassStateDiag.png)

![Diagrama de estados de los conductores](https://github.com/fi-ubers/app-server/blob/master/docs/DriverStateDiag.png)



