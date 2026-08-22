import sqlite3
import json
from datetime import datetime


DB_NAME = "meetings.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(DB_NAME)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            file_name TEXT NOT NULL,

            transcript TEXT NOT NULL,

            speaker_transcript TEXT,

            summary TEXT,

            key_decisions TEXT,

            action_items TEXT,

            created_at TEXT NOT NULL

        )
    """)

    # --------------------------------------------------------
    # DATABASE MIGRATION
    # Add speaker_transcript column if using old database
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(meetings)"
    )

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "speaker_transcript" not in columns:

        cursor.execute("""
            ALTER TABLE meetings
            ADD COLUMN speaker_transcript TEXT
        """)

    conn.commit()

    conn.close()


# ============================================================
# SAVE MEETING
# ============================================================

def save_meeting(

    file_name,

    transcript,

    speaker_transcript,

    summary,

    key_decisions,

    action_items
):

    # --------------------------------------------------------
    # CONVERT ACTION ITEMS
    # --------------------------------------------------------

    action_items_data = []

    for item in action_items:

        if isinstance(item, dict):

            task = item.get(
                "task",
                "Not specified"
            )

            owner = item.get(
                "owner",
                "Not specified"
            )

            deadline = item.get(
                "deadline",
                "Not specified"
            )

        else:

            task = getattr(
                item,
                "task",
                "Not specified"
            )

            owner = getattr(
                item,
                "owner",
                "Not specified"
            )

            deadline = getattr(
                item,
                "deadline",
                "Not specified"
            )

        action_items_data.append({

            "task": str(task),

            "owner": str(owner),

            "deadline": str(deadline)

        })


    # --------------------------------------------------------
    # SAVE TO DATABASE
    # --------------------------------------------------------

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO meetings (

            file_name,

            transcript,

            speaker_transcript,

            summary,

            key_decisions,

            action_items,

            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        (

            file_name,

            transcript,

            json.dumps(
                speaker_transcript
            ),

            summary,

            json.dumps(
                key_decisions
            ),

            json.dumps(
                action_items_data
            ),

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        )
    )

    conn.commit()

    meeting_id = cursor.lastrowid

    conn.close()

    return meeting_id


# ============================================================
# GET ALL MEETINGS
# ============================================================

def get_all_meetings():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            id,

            file_name,

            summary,

            created_at

        FROM meetings

        ORDER BY id DESC
        """
    )

    meetings = cursor.fetchall()

    conn.close()

    return meetings


# ============================================================
# GET MEETING BY ID
# ============================================================

def get_meeting_by_id(meeting_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            id,

            file_name,

            transcript,

            speaker_transcript,

            summary,

            key_decisions,

            action_items,

            created_at

        FROM meetings

        WHERE id = ?
        """,

        (meeting_id,)
    )

    meeting = cursor.fetchone()

    conn.close()


    # --------------------------------------------------------
    # MEETING NOT FOUND
    # --------------------------------------------------------

    if meeting is None:

        return None


    # --------------------------------------------------------
    # LOAD SPEAKER TRANSCRIPT
    # --------------------------------------------------------

    try:

        speaker_transcript = json.loads(
            meeting[3]
        ) if meeting[3] else []

    except Exception:

        speaker_transcript = []


    # --------------------------------------------------------
    # LOAD KEY DECISIONS
    # --------------------------------------------------------

    try:

        key_decisions = json.loads(
            meeting[5]
        ) if meeting[5] else []

    except Exception:

        key_decisions = []


    # --------------------------------------------------------
    # LOAD ACTION ITEMS
    # --------------------------------------------------------

    try:

        action_items = json.loads(
            meeting[6]
        ) if meeting[6] else []

    except Exception:

        action_items = []


    # --------------------------------------------------------
    # RETURN MEETING
    # --------------------------------------------------------

    return {

        "id": meeting[0],

        "file_name": meeting[1],

        "transcript": meeting[2],

        "speaker_transcript": speaker_transcript,

        "summary": meeting[4],

        "key_decisions": key_decisions,

        "action_items": action_items,

        "created_at": meeting[7]

    }