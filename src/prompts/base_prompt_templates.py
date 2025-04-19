POPULAR_QUESTIONS = {
    "popular_questions": [
        "Based on my latest journal entry, how can I get better?",
        "How can I improve my current Karma Coordinates score?",
        "What are the Sankrit shloka or karika relevant to my latest journal entry?",
    ]
}
QUESTIONS_TO_PROMPT = {
    "Based on my latest journal entry, how can I get better?": "question_and_activities",
    "How can I improve my current Karma Coordinates score?": "question_and_activities",
    "What are the Sankrit shloka or karika relevant to my latest journal entry?": "question_within_context",
    "Reflect on the journal entry" : "reflect"
}

PROMPT_TEMPLATES = {
    "question_and_activities": """Answer the question={{question}}
                    Within the context of
                        questionnaire={{features_df}}, 
                        user answers={{user_answers_rows}}, 
                        and journal entry={{journal_entry}}. 
                    In addition, provide specific activities, events and volunteering opportunities with dates and within the location={{client_ip_details}} to improve Karma Coordinates score.""",
    "question_within_context": """Answer the question={{question}}
                    Within the context of
                        questionnaire={{features_df}}, 
                        user answers={{user_answers_rows}}, 
                        and journal entry={{journal_entry}}.""",
    "question": """Answer the question={{question}}""",
    "reflect": """
        You are an assistant generating a structured response.

        Your response must include **exactly two sections**, with the following headers — and **only** the headers (no numbering, no "Title:"):

        ### Advice on Journal Entry  
        ### Questions Impacted by the Journal Entry

        Instructions:

        1. Start with the header: Advice on Journal Entry  
        Then, provide advice based on the journal entry: "{{journal_entry}}"

        2. Next, include the header: Questions Impacted by the Journal Entry
        Then, based on the questionnaire:
        {features_df.to_csv(index=False)}

        And the user's original answers:
        {{user_answers}}

        Identify which answers would change due to the journal entry: "{{journal_entry}}".
        Only include the impacted questions and their new valid answers in a Python dictionary.

        ⚠️ Do not number the sections.  
        ⚠️ Do not include "Title:" anywhere in the response.  
        ⚠️ Use **only the exact section headers as written** above.
      """
}
