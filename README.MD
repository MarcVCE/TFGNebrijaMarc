![Código Correcto](https://img.shields.io/badge/c%C3%B3digo-correcto-brightgreen) 
![Depuración Correcta](https://img.shields.io/badge/debbuging-correct-brightgreen)

![Representación de IA](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.43MCcgwhXrJY59twDinlfQAAAA%26pid%3DApi&f=1&ipt=8da7144a4c0aed1037934e4dc51251cff7522231dd18ebba35e50e49431c852d&ipo=images)

# Proyecto de IA

  

Este es un proyecto de Inteligencia Artificial. Sigue los pasos a continuación para configurar y ejecutar el proyecto. Hay dos formas de crear tu entorno virtual, o con conda, o con venv.

  

## Requisitos

  

- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

- [Docker](https://docs.docker.com/get-docker/)

- [Python](https://www.python.org/downloads/release/python-3122/)

  
  

## Instalación (No haría falta hacer esta sección si lo despliegas con docker)

  

### 1. Crear un entorno virtual con Conda:

  

```bash

conda  create  -n  ia  python=3.12

```

  

### 2. Activar el entorno virtual:

  

```bash

conda  activate  ia

```

  

### 3. Instalación de dependencias

  

Puedes instalar las dependencias automáticamente usando un archivo `requirements.txt` o manualmente una por una.

  

#### Instalación automática:

  

```bash

pip  install  -r  requirements.txt

```

  

#### Instalación manual:

  

```bash

pip  install  python-telegram-bot==21.1.1

pip  install  python-dotenv

pip  install  -U  google-generativeai

pip  install  prompt-toolkit==3.0.28

pip  install  ipython

etc

```

  

## Configuración

  

### 1. Crear algunas de tus API keys:

  

- [Google AI Studio](https://aistudio.google.com/app/apikey)

- [BotFather en Telegram](https://t.me/BotFather)

- [Consola Google Cloud](https://console.cloud.google.com)

  

### 2. Configurar el archivo de entorno:

  

1. Cambia el `.env.sample` por `.env` en el directorio raíz del proyecto.

2. Edita el archivo `.env` y agrega tus claves/token.

  

```env

# Ejemplo de contenido del archivo .env

TELEGRAM_API_TOKEN=xxx

GOOGLE_API_KEY=xxxx

CLOUD_API=xxxx

```


## Pruebas Tests de carpeta testinggraphfiles

Para sacar resultados (no tests o cobertura) de los ficheros que no son tests (sin _test en su nombre de archivo) , simplemente se corren con 

```bash

python nombrearchivo.py

```

dentro de la carpeta en la terminal de VSC. Una vez dicho esto:

  Antes que nada, lo más vital es hacer una cobertura de los archivos de test que hay en la carpeta, si no,
  los comandos posteriores no funcionarán dado que no hay data.
  Con este comando  
  
```bash

coverage run -m pytest

```

Se muestra por terminal el porcentaje de cobertura que se ha producido en los archivos _test.
Una vez con esto, hay data para hacer un 

```bash

coverage report

```
  
 para mostrar por terminal la cobertura de todos los archivos de esa carpeta, y de forma más
 detallada que la anterior,dado que en la respuesta también hay parámetros adicionales que se tienen en cuenta.

Si lo que se quiere es la cobertura más precisa y detallada que se puede lograr, se puede hacer un 

```bash

coverage html

```

Es el que utilicé para generar la carpeta de html. En el index.html realmente es dónde está todo. 




  

## Uso

 - *Uso con docker :*

  ### Inicializar el proyecto con Docker

  

Para construir y ejecutar el contenedor Docker por primera vez, utiliza el siguiente comando:

  
  

```bash

docker  compose  up  --build

```

  

Una vez que el contenedor ha sido creado, para inicializar el contenedor en las siguientes veces, simplemente utiliza:

  
  

```bash

docker  compose  up

```

 - *Uso sin docker :*

  ### Inicializar el proyecto sin Docker

Para inicializar sin docker, se debe configurar el proyecto como se especifica en el apartado configuración y
corre desde la carpeta dónde está el proyecto:
```bash

python main.py

```

## Activación
En caso de usar el entorno virtual con pip y venv (desconzco si pasa lo mismo con conda), es bastante
importante hacer CTRL+Shift+P en Visual Studio, y seleccionar el intérprete del entorno virtual que quieras
utilizar, el intérprete se encuentra o bien en .\venv\Scripts\python.exe  , si tu carpeta virtual 
se llama venv o bien .\env\Scripts\python.exe , si tu carpeta virtual se llama env
