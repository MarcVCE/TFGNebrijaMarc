
# Proyecto de IA

Este es un proyecto de Inteligencia Artificial. Sigue los pasos a continuación para configurar y ejecutar el proyecto. Hay dos formas de crear tu entorno virtual, o con conda, o con venv.

## Requisitos

- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

## Instalación

### 1. Crear un entorno virtual con Conda:

```bash
conda create -n ia python=3.10
```

### 2. Activar el entorno virtual:

```bash
conda activate ia
```

### 3. Instalación de dependencias

Puedes instalar las dependencias automáticamente usando un archivo `requirements.txt` o manualmente una por una.

#### Instalación automática:

```bash
pip install -r requirements.txt
```

#### Instalación manual:

```bash
pip install python-telegram-bot==21.1.1
pip install python-dotenv
pip install -U google-generativeai
pip install prompt-toolkit==3.0.28
pip install ipython
etc
```

## Configuración

### 1. Crear algunas de tus API keys:

- [Google AI Studio](https://aistudio.google.com/app/apikey)
- [BotFather en Telegram](https://t.me/BotFather)
- [Consola Google Cloud](console.cloud.google.com)

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

Una vez configurado todo, puedes ejecutar tu proyecto con los comandos apropiados de tu aplicación.




