import json
import __configs
from fastapi import Request
from pandas import DataFrame
import asyncio
import logging
import time
from ai_assist import assistant, guna
import storage.dynamodb_functions as db
from ai_assist.tools import handle_change_location, handle_delete_account
from assessment.utils import __update_ai_assessment

temp_folder = ".tmp"
logging.basicConfig(
    filename=f"{temp_folder}/kc-app.log", filemode="w", level=logging.INFO
)

FAILED_EVENTS = ["response.failed", "response.incomplete", "error"]


async def stream_ai_assist_reflect_response(
    request: Request,
    user_answers,
    features_df: DataFrame,
    categories_df: DataFrame,
    features_df_stats,
    prompt,
    is_tool="auto",
    include_guna=False,
):
    async_client = __configs.get_config().openai_async_client

    # ✅ Ask the assistant with streaming enabled
    stream = await async_client.responses.create(
        **assistant.response_args(prompt + guna.INSTRUCTIONS, is_tool), stream=True
    )

    splitter = guna.StreamSplitter()
    async for event in stream:
        if event.type == "response.output_text.delta":
            # Only app versions that ask for it get the Guna Balance section
            visible = splitter.feed(event.delta)
            yield event.delta if include_guna else visible

        elif event.type in FAILED_EVENTS:
            logging.error(f"❌ Assistant response failed: {event}")
            yield "[Assistant run failed or was cancelled]"
            break

    final = splitter.finish()
    if final and not include_guna:
        yield final
    complete_text = splitter.visible

    guna_balance = guna.parse(splitter.guna_text)
    if guna_balance:
        try:
            db.put({
                "email": request.user.display_name,
                "date": f"guna#{time.time()}",
                "journal_entry_date": user_answers[0].get("date"),
                **guna_balance,
            })
        except Exception as e:
            logging.error(f"❌ Couldn't save guna balance: {e}")

    # ✅ Kick off async background task with complete text
    asyncio.create_task(
        __update_ai_assessment(
            request,
            user_answers,
            features_df,
            categories_df,
            features_df_stats,
            complete_text,
        )
    )

async def stream_ai_assist_explore_response(
    request: Request,
    features_df,
    categories_df,
    features_df_stats,
    prompt,
    is_tool="auto"
):
    async_client = __configs.get_config().openai_async_client

    complete_text = ""
    tool_output_yielded = False

    try:
        stream = await async_client.responses.create(
            **assistant.response_args(prompt, is_tool), stream=True
        )
        async for event in stream:
            if event.type == "response.output_text.delta":
                complete_text += event.delta
                yield event.delta

            elif event.type == "response.output_item.done" and event.item.type == "function_call":
                # Handle function/tool calls
                async for text in __handle_function_call(event.item, request):
                    tool_output_yielded = True
                    yield text

            elif event.type in FAILED_EVENTS:
                logging.error(f"❌ Assistant response failed: {event}")
                yield "[Assistant run failed or was cancelled]"
                break

        if not complete_text and not tool_output_yielded:
            yield "[No response received from assistant]"

    except Exception as e:
        print(f'error:{e}')
        logging.error(f"❌ Exception during assistant stream: {e}")
        yield "[Assistant stream crashed]"


# The tool's message is shown to the user; the conversation isn't continued afterwards.
async def __handle_function_call(tool_call, request):
    name = tool_call.name
    args = json.loads(tool_call.arguments)

    try:
        if name == "delete_account":
            _, message, _ = await handle_delete_account(tool_call, args, request)
            yield message

        elif name == "change_location":
            _, message, _ = await handle_change_location(tool_call, args, request)
            yield message

        else:
            logging.error(f"❌ Tool '{name}' not recognized.")

    except Exception as e:
        yield f"❌ Error in tool `{name}`: {str(e)}"
