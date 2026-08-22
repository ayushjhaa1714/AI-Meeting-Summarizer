import streamlit as st
import os
import pandas as pd
from html import escape

from database import (
    initialize_database,
    save_meeting,
    get_all_meetings,
    get_meeting_by_id
)

from asr_processor import transcribe_audio
from gemini_processor import analyze_meeting


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()


# ============================================================
# SESSION STATE
# ============================================================

if "selected_meeting_id" not in st.session_state:
    st.session_state.selected_meeting_id = None

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if "current_meeting" not in st.session_state:
    st.session_state.current_meeting = None


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f6f8fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }

    /* HERO */

    .hero-box {
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        padding: 40px;
        border-radius: 22px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 30px rgba(37, 99, 235, 0.20);
    }

    .hero-box h1 {
        color: white !important;
    }

    .hero-box p {
        color: #dbeafe !important;
        font-size: 18px;
        line-height: 1.6;
    }

    /* METRIC CARDS */

    .metric-card {
        background-color: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.05);
        text-align: center;
    }

    .metric-number {
        font-size: 34px;
        font-weight: 700;
        color: #2563eb;
    }

    .metric-label {
        font-size: 15px;
        color: #6b7280;
        margin-top: 5px;
    }

    /* CONTENT CARD */

    .custom-card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.04);
        color: #374151;
        line-height: 1.7;
    }

    /* DECISION CARD */

    .decision-card {
        background: white;
        border-left: 5px solid #2563eb;
        padding: 18px 22px;
        border-radius: 12px;
        margin-bottom: 14px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        color: #1f2937;
        line-height: 1.6;
    }

    /* SPEAKER CARD */

    .speaker-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #2563eb;
        padding: 18px 22px;
        border-radius: 14px;
        margin-bottom: 14px;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.04);
    }

    .speaker-name {
        color: #2563eb;
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .speaker-text {
        color: #374151;
        font-size: 16px;
        line-height: 1.6;
    }

    /* FILE UPLOADER */

    [data-testid="stFileUploader"] {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 2px dashed #93c5fd;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: #f9fafb !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #374151;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background-color: #1f2937;
        color: white !important;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 12px;
        text-align: left;
        margin-bottom: 5px;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2563eb;
        border-color: #2563eb;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_item_value(item, field, default="Not specified"):

    if isinstance(item, dict):
        value = item.get(field, default)
    else:
        value = getattr(item, field, default)

    if value is None or str(value).strip() == "":
        return default

    return str(value)


# ============================================================
# DISPLAY MEETING RESULTS
# ============================================================

def show_meeting_results(meeting):

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "👥 Speakers",
        "📄 Transcript",
        "📌 Action Items"
    ])


    # ========================================================
    # OVERVIEW
    # ========================================================

    with tab1:

        st.subheader("📝 AI Generated Summary")

        summary = meeting.get(
            "summary",
            "No summary available."
        )

        st.info(summary)

        st.subheader("🎯 Key Decisions")

        decisions = meeting.get(
            "key_decisions",
            []
        )

        if decisions:

            for i, decision in enumerate(
                decisions,
                start=1
            ):

                st.markdown(
                    f"""
                    <div class="decision-card">
                        <b>Decision {i}</b>
                        <br><br>
                        {escape(str(decision))}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info("No key decisions found.")


    # ========================================================
    # SPEAKERS
    # ========================================================

    with tab2:

        st.subheader("👥 Speaker-wise Conversation")

        speaker_data = meeting.get(
            "speaker_transcript",
            []
        )

        if speaker_data:

            st.caption(
                "Speaker labels are generated using "
                "AssemblyAI speaker diarization."
            )

            for item in speaker_data:

                speaker = item.get(
                    "speaker",
                    "Unknown Speaker"
                )

                text = item.get(
                    "text",
                    ""
                )
                speaker_html=escape(str(speaker))
                text_html=escape(str(text))

                st.markdown(
                    f"""<div class="speaker-card">
                <div class="speaker-name">🎙️ {speaker_html}</div>
                <div class="speaker-text">{text_html}</div>
                </div>""",
                    
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "Speaker information is not available "
                "for this meeting."
            )

            st.caption(
                "Speaker diarization is available for newly "
                "analyzed meetings during the current session."
            )


    # ========================================================
    # TRANSCRIPT
    # ========================================================

    with tab3:

        st.subheader("📄 Complete Meeting Transcript")

        transcript = meeting.get(
            "transcript",
            "No transcript available."
        )

        st.text_area(
            "Transcript",
            value=str(transcript),
            height=500,
            disabled=True,
            label_visibility="collapsed"
        )

        st.download_button(
            label="⬇️ Download Transcript",
            data=str(transcript),
            file_name="meeting_transcript.txt",
            mime="text/plain",
            use_container_width=True
        )


    # ========================================================
    # ACTION ITEMS
    # ========================================================

    with tab4:

        st.subheader("📌 Action Items")

        action_items = meeting.get(
            "action_items",
            []
        )

        if action_items:

            action_data = []

            for i, item in enumerate(
                action_items,
                start=1
            ):

                action_data.append({
                    "No.": i,
                    "Task": get_item_value(
                        item,
                        "task"
                    ),
                    "Owner": get_item_value(
                        item,
                        "owner"
                    ),
                    "Deadline": get_item_value(
                        item,
                        "deadline"
                    )
                })

            df = pd.DataFrame(action_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No action items found.")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🎙️ Meeting AI")

    st.write(
        "Transform meeting conversations into "
        "summaries, decisions, speaker insights, "
        "and actionable tasks."
    )

    st.divider()

    if st.button(
        "🏠 New Meeting",
        use_container_width=True
    ):

        st.session_state.selected_meeting_id = None
        st.session_state.analysis_complete = False
        st.session_state.current_meeting = None

        st.rerun()


    st.subheader("📚 Recent Meetings")

    meetings = get_all_meetings()

    if meetings:

        for meeting in meetings[:10]:

            meeting_id = meeting[0]
            file_name = meeting[1]
            created_at = meeting[3]

            button_text = (
                f"📄 {file_name}\n"
                f"🕒 {created_at}"
            )

            if st.button(
                button_text,
                key=f"sidebar_meeting_{meeting_id}",
                use_container_width=True
            ):

                st.session_state.selected_meeting_id = meeting_id
                st.session_state.analysis_complete = False
                st.session_state.current_meeting = None

                st.rerun()

    else:

        st.caption("No meetings analyzed yet.")


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero-box">
        <h1>🎙️ AI Meeting Summarizer</h1>
        <p>
            Upload your meeting audio and automatically generate
            transcripts, speaker identification, intelligent summaries,
            key decisions, and actionable tasks.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE STATISTICS
# ============================================================

meetings = get_all_meetings()

total_meetings = len(meetings)
total_decisions = 0
total_actions = 0


for meeting_row in meetings:

    meeting_id = meeting_row[0]

    meeting_details = get_meeting_by_id(meeting_id)

    if meeting_details:

        total_decisions += len(
            meeting_details.get(
                "key_decisions",
                []
            )
        )

        total_actions += len(
            meeting_details.get(
                "action_items",
                []
            )
        )


# ============================================================
# METRICS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📁 Total Meetings",
        total_meetings
    )

with col2:
    st.metric(
        "🎯 Key Decisions",
        total_decisions
    )

with col3:
    st.metric(
        "📌 Action Items",
        total_actions
    )


st.divider()


# ============================================================
# SELECTED HISTORY MEETING
# ============================================================

if st.session_state.selected_meeting_id is not None:

    selected_meeting = get_meeting_by_id(
        st.session_state.selected_meeting_id
    )

    if selected_meeting:

        st.title(
            f"📂 {selected_meeting['file_name']}"
        )

        st.caption(
            f"Processed on "
            f"{selected_meeting['created_at']}"
        )

        if st.button(
            "← Back to Dashboard"
        ):

            st.session_state.selected_meeting_id = None

            st.rerun()

        st.divider()

        show_meeting_results(
            selected_meeting
        )

    else:

        st.error(
            "Meeting could not be found."
        )


# ============================================================
# MAIN DASHBOARD
# ============================================================

else:

    # ========================================================
    # SHOW ANALYSIS RESULT
    # ========================================================

    if (
        st.session_state.analysis_complete
        and
        st.session_state.current_meeting is not None
    ):

        st.title("📊 Analysis Results")

        st.caption(
            st.session_state.current_meeting.get(
                "file_name",
                ""
            )
        )

        st.divider()

        show_meeting_results(
            st.session_state.current_meeting
        )

        if st.button(
            "🏠 Analyze Another Meeting",
            use_container_width=True
        ):

            st.session_state.analysis_complete = False
            st.session_state.current_meeting = None

            st.rerun()


    # ========================================================
    # UPLOAD SECTION
    # ========================================================

    else:

        st.title("🎧 Upload a Meeting")

        st.subheader("How it works")

        st.write(
            "Upload your meeting recording and the AI will automatically:"
        )

        st.markdown(
            """
            - 🎧 Convert audio into text
            - 👥 Detect different speakers
            - 📝 Generate a concise meeting summary
            - 🎯 Extract important decisions
            - 📌 Identify action items
            - 👤 Assign task owners using speaker context
            - 📅 Extract deadlines
            """
        )


        # ====================================================
        # FILE UPLOADER
        # ====================================================

        uploaded_file = st.file_uploader(
            "Choose your meeting audio file",
            type=[
                "mp3",
                "wav",
                "m4a"
            ]
        )


        # ====================================================
        # FILE SELECTED
        # ====================================================

        if uploaded_file is not None:

            st.success(
                f"Ready to analyze: {uploaded_file.name}"
            )

            st.audio(uploaded_file)


            # =================================================
            # ANALYZE BUTTON
            # =================================================

            if st.button(
                "🚀 Analyze Meeting",
                use_container_width=True,
                type="primary"
            ):

                try:

                    os.makedirs(
                        "uploads",
                        exist_ok=True
                    )


                    # =========================================
                    # SAVE AUDIO
                    # =========================================

                    audio_path = os.path.join(
                        "uploads",
                        uploaded_file.name
                    )

                    with open(
                        audio_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_file.getbuffer()
                        )


                    # =========================================
                    # PROCESS
                    # =========================================

                    with st.status(
                        "Processing meeting...",
                        expanded=True
                    ) as status:


                        # =====================================
                        # TRANSCRIPTION
                        # =====================================

                        st.write(
                            "🎧 Transcribing audio using AssemblyAI..."
                        )

                        transcription_result = transcribe_audio(
                            audio_path
                        )


                        transcript = transcription_result.get(
                            "transcript",
                            ""
                        )


                        speaker_transcript = (
                            transcription_result.get(
                                "speaker_transcript",
                                []
                            )
                        )


                        formatted_transcript = (
                            transcription_result.get(
                                "formatted_transcript",
                                transcript
                            )
                        )


                        st.write(
                            "👥 Speaker diarization completed."
                        )

                        st.write(
                            "✅ Transcription completed."
                        )


                        # =====================================
                        # GEMINI ANALYSIS
                        # =====================================

                        st.write(
                            "🤖 Analyzing meeting using Gemini AI..."
                        )

                        meeting_data = analyze_meeting(
                            formatted_transcript
                        )

                        st.write(
                            "✅ AI analysis completed."
                        )


                        # =====================================
                        # SAVE TO DATABASE
                        # =====================================

                        st.write(
                            "💾 Saving meeting to database..."
                        )

                        meeting_id = save_meeting(

                            file_name=uploaded_file.name,

                            transcript=transcript,

                            speaker_transcript=speaker_transcript,
                            summary=meeting_data.summary,

                            key_decisions=(
                                meeting_data.key_decisions
                            ),

                            action_items=(
                                meeting_data.action_items
                            )
                        )

                        st.write(
                            "✅ Meeting saved successfully."
                        )


                        status.update(
                            label=(
                                "🎉 Meeting analysis completed!"
                            ),
                            state="complete",
                            expanded=False
                        )


                    # =========================================
                    # STORE CURRENT RESULT
                    # =========================================

                    st.session_state.current_meeting = {

                        "id": meeting_id,

                        "file_name": uploaded_file.name,

                        "transcript": transcript,

                        "speaker_transcript":
                            speaker_transcript,

                        "formatted_transcript":
                            formatted_transcript,

                        "summary":
                            meeting_data.summary,

                        "key_decisions":
                            meeting_data.key_decisions,

                        "action_items":
                            meeting_data.action_items
                    }


                    st.session_state.analysis_complete = True

                    st.rerun()


                except Exception as e:

                    st.error(
                        f"❌ An error occurred: {str(e)}"
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎙️ AI Meeting Summarizer • "
    "AssemblyAI Speaker Diarization • "
    "Gemini AI • SQLite"
)