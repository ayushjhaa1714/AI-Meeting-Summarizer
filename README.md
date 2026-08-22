# 🎙️ AI Meeting Summarizer

An AI-powered meeting summarization system that automatically transcribes meeting audio, identifies speakers, generates intelligent summaries, extracts key decisions, and identifies actionable tasks.

The application uses **AssemblyAI** for audio transcription and speaker diarization, **Google Gemini AI** for meeting analysis, **Streamlit** for the user interface, and **SQLite** for storing meeting history.

---

## ✨ Features

- 🎧 Upload meeting audio files
- 📝 Convert audio into text
- 👥 Detect and separate different speakers
- 🤖 Generate AI-powered meeting summaries
- 🎯 Extract key decisions
- 📌 Identify action items
- 👤 Assign task owners based on speaker context
- 📅 Extract deadlines from the conversation
- 💾 Store meeting history using SQLite
- 📄 View complete meeting transcripts
- 📥 Download meeting transcripts
- 📊 View meeting statistics

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit**
- **AssemblyAI**
- **Google Gemini AI**
- **SQLite**
- **Pandas**
- **Pydantic**

---

## 📂 Project Structure

```text
AI-Meeting-Summarizer/
│
├── app.py
├── asr_processor.py
├── gemini_processor.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

### File Description

| File | Description |
|------|-------------|
| `app.py` | Main Streamlit application and user interface |
| `asr_processor.py` | Handles audio transcription and speaker diarization using AssemblyAI |
| `gemini_processor.py` | Analyzes meeting transcripts using Gemini AI |
| `database.py` | Handles SQLite database operations |
| `requirements.txt` | Contains required Python dependencies |

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/ayushjhaa174/AI-Meeting-Summarizer.git
```

### 2. Navigate to the project directory

```bash
cd AI-Meeting-Summarizer
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS/Linux

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Configuration

This project requires API keys from:

- **AssemblyAI**
- **Google Gemini API**

Create a `.env` file in the project root directory:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

⚠️ **Important:** Never upload your `.env` file to GitHub.

Make sure your `.gitignore` contains:

```text
.env
meetings.db
uploads/
__pycache__/
```

---

## ▶️ Running the Application

Run the Streamlit application using:

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🔄 How It Works

```text
Meeting Audio
      │
      ▼
AssemblyAI
(Audio Transcription + Speaker Diarization)
      │
      ▼
Speaker-Labeled Transcript
      │
      ▼
Google Gemini AI
      │
      ├── Meeting Summary
      ├── Key Decisions
      └── Action Items
              │
              ▼
         SQLite Database
              │
              ▼
        Streamlit Dashboard
```

---

## 📊 Application Workflow

1. Upload a meeting audio file.
2. AssemblyAI converts the audio into text.
3. Speaker diarization identifies different speakers.
4. A speaker-labelled transcript is generated.
5. Gemini AI analyzes the transcript.
6. The system generates:
   - Meeting Summary
   - Key Decisions
   - Action Items
   - Task Owners
   - Deadlines
7. Meeting data is stored in an SQLite database.
8. Users can view previous meetings from the dashboard.

---

## 🎯 Supported Audio Formats

Currently supported formats include:

- MP3
- WAV
- M4A

---

## 📸 Application Output

The application provides the following results:

### AI Generated Summary

A concise summary of the important points discussed during the meeting.

### Key Decisions

Important decisions identified from the meeting conversation.

### Action Items

Tasks extracted from the meeting along with:

- Task description
- Responsible person
- Deadline

### Speaker-wise Conversation

The transcript is separated according to detected speakers.

### Meeting History

Previously analyzed meetings are stored and can be accessed from the sidebar.

---

## 🔮 Future Improvements

- Real-time meeting transcription
- Support for additional audio and video formats
- User authentication
- Cloud database integration
- Meeting analytics dashboard
- Automatic email summaries
- Calendar integration
- Improved speaker name identification

---

## 👨‍💻 Author

**Ayush KUMAR**

GitHub: [@ayushjhaa174](https://github.com/ayushjhaa174)

---

## 📄 License

This project is licensed under the MIT License.

---

⭐ If you found this project useful, consider giving it a star!

