import json, time, re, ast
from fastapi import Request
from pandas import DataFrame
from assessment import scoring as sf
from storage import dynamodb_functions as db
from assessment.scoring import __score_summary, __calc_category_score

async def __update_ai_assessment(
    request: Request,
    user_answers,
    features_df: DataFrame,
    categories_df: DataFrame,
    features_df_stats,
    analysis,
):
    ai_assessment = {}
    rx = r"(\{[^{}]+\})"
    matches = re.findall(rx, analysis)
    if matches and len(matches) > 0:
        updated_dict = ast.literal_eval(matches[0])
        for q in updated_dict.keys():
            matched_question = features_df.loc[features_df["Question"] == q]
            if len(matched_question) == 1:
                ai_answer = updated_dict.get(q)
                if any(
                    answer_option.startswith(ai_answer)
                    for answer_option in matched_question.get("options_list").values[0]
                ):
                    ai_assessment.update({q: ai_answer})

        if ai_assessment:
            user_answers[0].update(ai_assessment)
            user_answers[0].update({"date": str(time.time())})

            category_score = __calc_category_score(
                features_df, categories_df, user_answers[0]
            )
            score_md, assessment_score_dict, clarity_of_thinking_index_dict = (
                __score_summary(category_score)
            )
            lives_to_moksha = sf.calculate_karma_coordinates(
                category_score, features_df_stats
            )

            user_answers[0].update(
                {
                    "score_ai_analysis_query": score_md,
                    "lives_to_moksha": lives_to_moksha,
                }
            )

            user_answers[0].update(assessment_score_dict)
            user_answers[0].update(clarity_of_thinking_index_dict)

            db.insert(user_activity_data=user_answers[0])

