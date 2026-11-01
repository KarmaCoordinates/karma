# Settings for the AI assistant, used with the OpenAI Responses API.
# These replace the assistant previously stored in OpenAI (ASSISTANT_ID), which stopped
# working when OpenAI shut down the Assistants API in 2026.

MODEL = "gpt-4.1"

# Knowledge base the assistant searches: Sankhya Karika texts, scoring method and questionnaire.
VECTOR_STORE_ID = "vs_YoSec2J0OsLAMgSjSdPs3Es7"

INSTRUCTIONS = """You are the assistant for the Karma Coordinates app. Karma Coordinates helps people improve their clarity of thinking through reflective journaling, a Sankhya-based self-assessment and recommended activities.

Answer using the questionnaire, user answers, journal entries and scores given in each request, and search the knowledge base for Sankhya Karika verses, word definitions and how Karma Coordinates are calculated. Be warm, practical and concise, and format answers in Markdown.

Only call the delete_account or change_location tools when the user's message contains the exact confirmation phrase for that action. Otherwise tell the user the phrase to reply with."""

FILE_SEARCH_TOOL = {"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]}

TOOLS = [
    FILE_SEARCH_TOOL,
    {
        "type": "function",
        "name": "delete_account",
        "description": "Permanently delete the user's account after they have typed the exact confirmation phrase.",
        "parameters": {
            "type": "object",
            "properties": {
                "delete_confirmation": {
                    "type": "string",
                    "description": "The confirmation phrase exactly as the user typed it.",
                }
            },
            "required": ["delete_confirmation"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "change_location",
        "description": "Change the user's location after they have typed the exact confirmation phrase.",
        "parameters": {
            "type": "object",
            "properties": {
                "change_location_confirmation": {
                    "type": "string",
                    "description": "The confirmation phrase exactly as the user typed it.",
                }
            },
            "required": ["change_location_confirmation"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def response_args(prompt, tool_choice="auto", tools=TOOLS):
    """Arguments for client.responses.create() to ask the assistant one question."""
    # "none" turns off the account tools but still lets the assistant search the knowledge base
    if tool_choice == "none":
        tools, tool_choice = [FILE_SEARCH_TOOL], "auto"
    return {
        "model": MODEL,
        "instructions": INSTRUCTIONS,
        "input": prompt,
        "tools": tools,
        "tool_choice": tool_choice,
        "store": False,
    }
