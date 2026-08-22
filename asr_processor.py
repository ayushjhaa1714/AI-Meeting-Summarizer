import os
import assemblyai as aai
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ASSEMBLYAI API KEY
# ============================================================

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not ASSEMBLYAI_API_KEY:
    raise ValueError(
        "ASSEMBLYAI_API_KEY is not set. "
        "Please add your AssemblyAI API key."
    )


# ============================================================
# CONFIGURE ASSEMBLYAI
# ============================================================

aai.settings.api_key = ASSEMBLYAI_API_KEY


# ============================================================
# TRANSCRIBE AUDIO WITH SPEAKER DIARIZATION
# ============================================================

def transcribe_audio(audio_path):

    # Enable speaker diarization
    config = aai.TranscriptionConfig(
        speaker_labels=True
    )

    # Create transcriber
    transcriber = aai.Transcriber()

    # Transcribe audio
    transcript = transcriber.transcribe(
        audio_path,
        config
    )


    # ========================================================
    # CHECK FOR ERRORS
    # ========================================================

    if transcript.status == aai.TranscriptStatus.error:

        raise RuntimeError(
            f"AssemblyAI Error: {transcript.error}"
        )


    # ========================================================
    # NORMAL TRANSCRIPT
    # ========================================================

    full_transcript = transcript.text or ""


    # ========================================================
    # SPEAKER-WISE TRANSCRIPT
    # ========================================================

    speaker_transcript = []

    if transcript.utterances:

        for utterance in transcript.utterances:

            speaker = f"Speaker {utterance.speaker}"

            text = utterance.text

            speaker_transcript.append(
                {
                    "speaker": speaker,
                    "text": text
                }
            )


    # ========================================================
    # CREATE FORMATTED TRANSCRIPT FOR GEMINI
    # ========================================================

    formatted_transcript = ""

    for item in speaker_transcript:

        formatted_transcript += (
            f'{item["speaker"]}: '
            f'{item["text"]}\n\n'
        )


    # ========================================================
    # FALLBACK IF SPEAKER DATA IS NOT AVAILABLE
    # ========================================================

    if not formatted_transcript.strip():

        formatted_transcript = full_transcript


    # ========================================================
    # RETURN COMPLETE DATA
    # ========================================================

    return {
        "transcript": full_transcript,

        "speaker_transcript": speaker_transcript,

        "formatted_transcript": formatted_transcript
    }