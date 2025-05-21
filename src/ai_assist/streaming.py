import json
import __configs
from fastapi import Request
from pandas import DataFrame
import asyncio
import logging
from ai_assist.tools import handle_change_location, handle_delete_account
from assessment.utils import __update_ai_assessment

temp_folder = ".tmp"
logging.basicConfig(
    filename=f"{temp_folder}/kc-app.log", filemode="w", level=logging.INFO
)

async def stream_ai_assist_reflect_response(
    request: Request,
    user_answers,
    features_df: DataFrame,
    categories_df: DataFrame,
    features_df_stats,
    assistant_id,
    thread_id,
):
    async_client = __configs.get_config().openai_async_client

    # ✅ Start the assistant run with streaming enabled
    run = await async_client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread_id,
        stream=True,
    )

    complete_text = ""
    async with run as event_stream:
        async for event in event_stream:
            if event.event == "thread.message.delta":
                delta = event.data.delta
                if hasattr(delta, "content") and delta.content:
                    for part in delta.content:
                        if hasattr(part, "text") and part.text.value:
                            complete_text += part.text.value
                            yield part.text.value

            elif event.event in [
                "thread.run.failed",
                "thread.run.expired",
                "thread.run.cancelled",
            ]:
                yield "[Assistant run failed or was cancelled]"
                break

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
    assistant_id,
    thread_id,
):
    async_client = __configs.get_config().openai_async_client

    # Ensure no active run before starting a new one
    existing_runs = await async_client.beta.threads.runs.list(
        thread_id=thread_id, limit=1
    )
    if existing_runs.data and existing_runs.data[0].status in [
        "in_progress",
        "queued",
        "requires_action",
    ]:
        raise Exception("Thread already has an active run.")

    # Start new run with streaming
    stream = await async_client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread_id,
        tool_choice="auto",
        stream=True,
    )

    tool_call_ids_to_output = {}
    complete_text = ""
    tool_output_yielded = False

    try:
        async with stream as event_stream:
            async for event in event_stream:
                if event.event == "thread.message.delta":
                    delta = event.data.delta
                    if hasattr(delta, "content") and delta.content:
                        if isinstance(delta.content, list):
                            for part in delta.content:
                                if hasattr(part, "text") and part.text.value:
                                    complete_text += part.text.value
                                    yield part.text.value
                        elif isinstance(delta.content, str):
                            complete_text += delta.content
                            yield delta.content

                elif event.event == "thread.run.requires_action":
                    # Handle function/tool calls
                    async for text in __handleRequiresActions(
                        async_client, thread_id, event, request
                    ):
                        tool_output_yielded = True
                        yield text

                elif event.event == "thread.run.completed":
                    break

                elif event.event in [
                    "thread.run.failed",
                    "thread.run.expired",
                    "thread.run.cancelled",
                ]:
                    yield "[Assistant run failed or was cancelled]"
                    break

        if not complete_text and not tool_output_yielded:
            yield "[No response received from assistant]"

    except Exception as e:
        print(f'error:{e}{e.message}')
        logging.error(f"❌ Exception during assistant stream: {e}")
        yield "[Assistant stream crashed]"



async def __handleRequiresActions(async_client, thread_id, event, request):
    tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []

    for tool_call in tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        try:
            if name == "delete_account":
                tool_call_id, message, result = await handle_delete_account(tool_call, args, request)
                yield message
                tool_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps(result)})

            elif name == "change_location":
                tool_call_id, message, result = await handle_change_location(tool_call, args, request)
                yield message
                tool_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps(result)})

            else:
                # Unknown tool, send a fallback response
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({"message": f"Tool '{name}' not recognized."})
                })

        except Exception as e:
            # Handle exception so at least a response is sent back
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"message": f"Error handling tool '{name}': {str(e)}"})
            })
            yield f"❌ Error in tool `{name}`: {str(e)}"

    if tool_outputs:
        await async_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id, run_id=event.data.id, tool_outputs=tool_outputs
        )
    else:
        # Don't submit if we truly have nothing (should never happen now)
        print("⚠️ No tool outputs to submit. Skipping submission.")


