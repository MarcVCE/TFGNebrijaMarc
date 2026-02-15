![Code Correct](https://img.shields.io/badge/code-correct-brightgreen) 
![Debugging Correct](https://img.shields.io/badge/debugging-correct-brightgreen)

# 🤖 AI-Powered Multilingual Scientific Text & Audio Pipeline

A comprehensive AI-driven system that integrates web scraping, natural language processing, and multimedia processing to process scientific content in multiple languages. This end-to-end pipeline automates data extraction from PubMed, analyzes text and audio inputs, and delivers outputs as text or audio through a Telegram bot interface.

---

## 🚀 Project Overview

![Image](https://github.com/user-attachments/assets/fbc284ac-d302-48af-9665-9ed63b9afa61)

This project combines multiple technologies to create a versatile tool that:

- Scrapes scientific articles and abstracts from PubMed.
- Processes audio and text inputs with language detection.
- Uses advanced AI models such as Google BERT for summarization of abstracts and APA-formatted articles.
- Generates JSON outputs with clean, non-repetitive information extracted from scientific texts.
- Selects and processes outputs as either audio or text using Google Gemini AI.
- Deploys the entire pipeline within Docker for easy setup and scalability.
- Provides a Telegram bot interface for user interaction.

---

## 🛠️ Technologies Used

- **Python** — Core programming language.
- **Web Scraping** — Extraction of scientific articles from PubMed.
- **Google BERT** — State-of-the-art NLP model for text summarization.
- **Google Gemini** — AI for generating audio or text outputs.
- **Docker** — Containerization for deployment and scalability.
- **Telegram Bot API** — User interface for command inputs and outputs.
- **Language Detection** — Automatically detects input language to route processing accordingly.

---

## 📦 Installation

> Note: Using Docker is highly recommended to simplify setup.

### Using Docker

1. Build and run the container for the first time:

```bash
docker compose up --build
```

2. For subsequent runs:

```bash
docker compose up
```

### Without Docker

1. Set up a Python virtual environment using Conda or venv.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure API keys in `.env` (see Configuration section).

4. Run the project:

```bash
python main.py
```

---

## ⚙️ Configuration

1. Obtain API keys for:

- [Google AI Studio](https://aistudio.google.com/app/apikey)
- [Telegram BotFather](https://t.me/BotFather)
- [Google Cloud Console](https://console.cloud.google.com)

2. Rename `.env.sample` to `.env` and add your API credentials:

```env
TELEGRAM_API_TOKEN=your_token_here
GOOGLE_API_KEY=your_key_here
CLOUD_API=your_cloud_api_here
```

---

## 🧪 Testing

- To run individual scripts from `testinggraphfiles` (non-test files), execute:

```bash
python filename.py
```

- For test coverage:

```bash
coverage run -m pytest
coverage report
coverage html
```

---

## 🔍 Usage

Interact with the project via Telegram commands.

- If running with Docker, follow the Docker usage instructions above.
- Without Docker, run `python main.py` after configuration.

---

## 💡 Additional Notes

- When using virtual environments with pip/venv, ensure to select the correct Python interpreter in your IDE (e.g., VSCode).
- The project intelligently routes input based on command usage to either web scraping or multimedia processing.
- Outputs can be audio or text, depending on user selection.
- For virtual environments with `venv` or `pip`, make sure the interpreter points to `.venv/Scripts/python.exe` (or `.env/Scripts/python.exe` depending on your folder name) in your IDE.

---
