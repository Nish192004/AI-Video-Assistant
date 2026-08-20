# 🎥 AI Video Assistant

An AI-powered video assistant that can process videos, extract audio, transcribe speech, summarize content, and provide intelligent answers using **Retrieval-Augmented Generation (RAG)**.

The project combines **speech-to-text, AI summarization, vector search, and LLM-based question answering** to turn long videos into searchable and understandable information.

---

## 🚀 Features

* 🎬 **Video Processing** — Extract and process audio from video content.
* 🎙️ **Speech Transcription** — Convert spoken content into text.
* 📝 **AI Summarization** — Generate concise summaries from video transcripts.
* 🔎 **Semantic Search** — Search video content using vector embeddings.
* 🤖 **RAG-based Question Answering** — Ask questions about the processed video and receive context-aware answers.
* 🧠 **Vector Database** — Store and retrieve document embeddings for semantic retrieval.
* 🔊 **Audio Processing** — Process and split extracted audio into manageable chunks.
* 🧩 **Modular Architecture** — Separate components for transcription, extraction, summarization, RAG, and vector storage.

---

## 🏗️ Project Architecture

```text
AI-Video-Assistant/
│
├── app.py
├── main.py
├── test.py
├── requirements.txt
├── .gitignore
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
└── utils/
    └── audio_processor.py
```

### Core Modules

| Module               | Purpose                                        |
| -------------------- | ---------------------------------------------- |
| `extractor.py`       | Handles content/audio extraction               |
| `transcriber.py`     | Converts speech into text                      |
| `summarizer.py`      | Generates summaries                            |
| `rag_engine.py`      | Handles retrieval-augmented question answering |
| `vector_store.py`    | Manages vector storage and retrieval           |
| `audio_processor.py` | Processes extracted audio                      |
| `app.py`             | Main application interface                     |
| `main.py`            | Application/processing entry point             |
| `test.py`            | Testing and experimentation                    |

---

## 🔄 How It Works

```text
                ┌─────────────────┐
                │   Video Input   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Audio Extraction│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Audio Processing│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   Transcription │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Transcript Text │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       ┌─────────────┐       ┌─────────────┐
       │ Summarizer  │       │ Vector Store│
       └─────────────┘       └──────┬──────┘
                                    │
                                    ▼
                              ┌─────────────┐
                              │ RAG Engine  │
                              └──────┬──────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │ AI Response │
                              └─────────────┘
```

---

## 🛠️ Tech Stack

### Programming Language

* Python

### AI / Machine Learning

* Speech-to-Text
* Large Language Models (LLMs)
* Text Embeddings
* Retrieval-Augmented Generation (RAG)

### Data & Retrieval

* Vector Database
* ChromaDB
* Semantic Search

### Video & Audio

* Video processing
* Audio extraction
* Audio chunking
* Speech transcription

### Development Tools

* Python Virtual Environment
* Git
* GitHub

---

## 📋 Requirements

* Python 3.10+
* Git
* Required API keys configured locally
* FFmpeg if required by your video/audio processing pipeline

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nish192004/AI-Video-Assistant.git
```

### 2. Navigate to the project

```bash
cd AI-Video-Assistant
```

### 3. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a local `.env` file in the project root.

```env
# Add your required API keys here
# Example:
# OPENAI_API_KEY=your_api_key
# MISTRAL_API_KEY=your_api_key
# TAVILY_API_KEY=your_api_key
```

**Never commit your `.env` file to GitHub.**

The repository already uses `.gitignore` to keep sensitive environment variables out of version control.

---

## ▶️ Running the Application

Activate your virtual environment first:

```powershell
.venv\Scripts\activate
```

Then run the application using the appropriate entry point:

```bash
python app.py
```

If your application uses Streamlit:

```bash
streamlit run app.py
```

---

## 💡 Example Use Cases

### 🎓 Education

Upload a long lecture and quickly obtain:

* Lecture summary
* Important concepts
* Searchable transcript
* Answers to questions

### 📰 News Analysis

Process news videos and ask questions about:

* Events
* People
* Locations
* Important statements
* Key developments

### 💼 Meetings

Convert meeting recordings into:

* Transcripts
* Summaries
* Important discussion points
* Searchable information

### 📚 Research

Process long educational or research videos and retrieve specific information without watching the entire video.

---

## 🧠 RAG Pipeline

The project uses a Retrieval-Augmented Generation approach:

```text
Video
  ↓
Audio
  ↓
Transcription
  ↓
Text Chunking
  ↓
Embeddings
  ↓
Vector Database
  ↓
User Question
  ↓
Semantic Retrieval
  ↓
Relevant Context
  ↓
LLM
  ↓
Final Answer
```

This allows the assistant to answer questions using information retrieved from the processed video content.

---

## 🔒 Security

The following files/directories are intentionally excluded from Git:

```text
.env
.venv/
downloades/
vector_db/
__pycache__/
```

API keys and other sensitive credentials should always remain in environment variables or secure secret-management systems.

---

## 📌 Future Improvements

* [ ] Multi-video knowledge base
* [ ] Timestamp-based answers
* [ ] Automatic chapter generation
* [ ] Speaker identification
* [ ] Multilingual transcription
* [ ] Multilingual question answering
* [ ] Video highlight generation
* [ ] Chat history
* [ ] Improved UI/UX
* [ ] Cloud deployment
* [ ] Authentication and user accounts

---

## 🎯 Project Goal

The goal of **AI Video Assistant** is to make long-form video content easier to understand, search, and interact with by combining video processing, speech recognition, vector search, RAG, and generative AI.

Instead of watching an entire video to find one piece of information, users can interact with the video through natural-language questions.

---

## 👨‍💻 Author

**Nishant Ojha**

GitHub:
https://github.com/Nish192004

Project:
https://github.com/Nish192004/AI-Video-Assistant

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
