# app-server

[![Build Status](https://travis-ci.org/fi-ubers/app-server.svg?branch=master)](https://travis-ci.org/fi-ubers/app-server)
[![Coverage Status](https://coveralls.io/repos/github/fi-ubers/app-server/badge.svg?branch=master)](https://coveralls.io/github/fi-ubers/app-server?branch=master)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Aplicación en python (flask + gunicorn) con API RESTful para el app-server de Fiuber App.

Leer los issues para una lista de tareas que realizar.

Connect to... [https://fiuber-app-server.herokuapp.com/](https://fiuber-app-server.herokuapp.com/)

## Para correr el servidor

Es necesario crear un entorno virtual sobre el que correr el servidor, para ello se utiliza el paquete _virtualenv_ de python (`sudo pip install virtualenv`). Para crear un entorno virtual, estando en la carpeta del proyecto hacer `virtualenv venv`, se puede reemplazar _venv_ por cualquier otro nombre, pero cuidado porque esto crea una carpeta y no se debería agregar a ningún commit (_venv_ ya está en .gitignore).

Para entrar en el entorno virtual usar `source venv/bin/activate`, notar cómo el prompt indica entre paréntesis que se encuentra en el entorno venv. Aquí habría que instalar todos los paquetes que requiere la aplicación (si es que no se instalaron ya DENTRO del entorno virtual). Para facilitar las cosas están todos en el archivo _requirements.txt_, por lo que basta con hacer `pip install -r requirements.txt`. Se puede generar en cualquier momento un _requirements.txt_ haciendo `pip freeze > requirements.txt`.

**IMPORTANTE**: para salir del entorno virtual, simplemente tipear `deactivate`.

### Levantar el servidor localmente

Estando en el entorno virtual con las dependencias instaladas, se puede levantar el servidor con `gunicorn --bind localhost:5000 wsgi --chdir src/main/`.

### Levantar el servidor en Heroku

*WIP*

## Para realizar requests por consolas

Para poder probar los distintos endpoints de la API se puede utilizar un navegador (que realiza request de tipo GET) o bien usar el comando `curl` y hacerlo por consola. En particular la estructura del comando sería:

`curl -X _tipo_ -d _data_ http://someURL:somePort/someEndpoint`

Donde _tipo_ es POST, GET, etc; _data_ son los datos a mandar en la request (un string representando un .json o '' para no enviar nada). 

##Para generar la documentacion del código fuente

Ingresar el siguiente comando en la consola, desde el directorio raíz de la aplicación:

$ make

Los archivos de documentación se generarán automáticamente en la carpeta docs/documentation. Allí se podrá encontrar el subdirectorio correspondiente a cada formato disponible para visualizar la documentación (latex, html, etc.). Para visualizar la documentación en formato html, se debe ingresar a docs/documentation/html y seleccionar el archivo index.html. Para la documentación en latex, ingresar al directorio docs/documentation/latex y nuevamente ingresar el comando $make en la consola. Se generará un archivo .pdf con la documentación de la aplicación.
 
