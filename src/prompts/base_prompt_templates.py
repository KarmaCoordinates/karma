PROMPT_TEMPLATES = {
    "default_prompt": """Answer the question={{question}}
                    If and only if asked or required, 
                        use assessment scores={{assessment_scores}}, 
                        compare and analyze the assessment scores,
                        use assessment questions={{user_answers_rows}}
                        and present data it text tabular summary format.""",
}
