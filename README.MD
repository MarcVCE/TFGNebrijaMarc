

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
