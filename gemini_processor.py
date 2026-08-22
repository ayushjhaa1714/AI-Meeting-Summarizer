import os
import json
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI API KEY
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. "
        "Please add your Gemini API key in the .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# ACTION ITEM MODEL
# ============================================================

class ActionItem(BaseModel):

    task: str
    owner: str
    deadline: str


# ============================================================
# MEETING ANALYSIS MODEL
# ============================================================

class MeetingAnalysis(BaseModel):

    summary: str
    key_decisions: List[str]
    action_items: List[ActionItem]


# ============================================================
# ANALYZE MEETING
# ============================================================

def analyze_meeting(formatted_transcript):

    prompt = f"""
You are an intelligent AI meeting analyzer.

The following meeting transcript contains speaker labels generated
using speaker diarization.

Your task is to carefully analyze the meeting.

IMPORTANT RULES:

1. Generate a clear and concise meeting summary.

2. Extract all important decisions made during the meeting.

3. Extract all action items.

4. For each action item, identify the person responsible.

5. Determine the owner based on the speaker who:
   - accepted the task,
   - volunteered for the task,
   - was assigned the task,
   - or explicitly agreed to complete the task.

6. If the real name of a speaker is mentioned in the conversation,
   use that real name.

7. If the real name is not available, use the speaker label exactly
   as provided in the transcript, for example:
   "Speaker A", "Speaker B", etc.

8. Do NOT invent an owner.

9. If the task owner cannot be identified, use:
   "Not specified"

10. Extract deadlines only when explicitly mentioned.

11. If no deadline is mentioned, use:
    "Not specified"

12. Do not create action items that were not discussed.

Return ONLY valid JSON.
Do not include explanations.
Do not include markdown.

The JSON format must be exactly:

{{
    "summary": "string",

    "key_decisions": [
        "decision 1",
        "decision 2"
    ],

    "action_items": [
        {{
            "task": "string",
            "owner": "string",
            "deadline": "string"
        }}
    ]
}}


MEETING TRANSCRIPT:

{formatted_transcript}
"""


    # ========================================================
    # SEND TO GEMINI
    # ========================================================

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    # ========================================================
    # GET RESPONSE TEXT
    # ========================================================

    response_text = response.text.strip()


    # ========================================================
    # REMOVE MARKDOWN CODE BLOCKS
    # ========================================================

    if response_text.startswith("```"):

        lines = response_text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response_text = "\n".join(lines).strip()


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        data = json.loads(response_text)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Gemini returned invalid JSON.\n\n"
            f"Response received:\n{response_text}"
        ) from e


    # ========================================================
    # CONVERT ACTION ITEMS TO PYDANTIC OBJECTS
    # ========================================================

    action_items = []

    for item in data.get("action_items", []):

        action_items.append(

            ActionItem(

                task=item.get(
                    "task",
                    "Not specified"
                ),

                owner=item.get(
                    "owner",
                    "Not specified"
                ),

                deadline=item.get(
                    "deadline",
                    "Not specified"
                )
            )
        )


    # ========================================================
    # RETURN STRUCTURED RESULT
    # ========================================================

    return MeetingAnalysis(

        summary=data.get(
            "summary",
            ""
        ),

        key_decisions=data.get(
            "key_decisions",
            []
        ),

        action_items=action_items
    )