# 🧠 Wikipedia Voice Assistant (Flask + MySQL)

This is a **Flask web application** that allows registered users to search Wikipedia articles, listen to summaries using **text-to-speech (TTS)**, and download content as **PDF** or **audio files**. It also includes user authentication and search history features using a **MySQL database**.

---

## 🚀 Features

- 🔐 User Registration & Login (with password hashing)
- 🔎 Wikipedia Search (summary + full content)
- 🗣️ Text-to-Speech summary with `pyttsx3`
- 📄 PDF generation using `reportlab`
- 📥 Download & stream audio or PDF files
- 📊 Dashboard to view recent searches
- ✅ Session-based authentication

---

## 🛠️ Tech Stack

- **Backend:** Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS (Jinja Templates)
- **TTS Engine:** pyttsx3
- **PDF Generator:** ReportLab
- **External API:** Wikipedia Python API

---

## 🏗️ Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/Surya-Mathivanan/wikipedia-voice-assistant.git
cd wikipedia-voice-assistant
```


## 📁 Folder Structure:

```📦 wikipedia-voice-assistant
├── app.py
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── results.html
│   ├── result.html
│   ├── dashboard.html
│   └── disambiguation.html
├── static/
│   ├── audio/
│   └── pdf/
├── requirements.txt
└── README.md
```

## ✅ Requirements:
```
Flask
mysql-connector-python
wikipedia
pyttsx3
reportlab

```

## 🔒 Security Notes:
 - Passwords are stored using hashing (werkzeug.security)

 - CSRF protection and email validation can be added for production

 - Use environment variables for DB credentials in production

## 📬 Contact

- **Surya M**  
- 📧 [msuryamsurya2003@gmail.com](mailto:msuryamsurya2003@gmail.com)  
- 🔗 [GitHub: Surya-Mathivanan](https://github.com/Surya-Mathivanan)


