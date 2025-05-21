import aiohttp
from urllib.parse import urljoin
import re
from typing import Optional

# Refactor helper for delete_account
async def handle_delete_account(tool_call, args, request):
    confirm_text = args.get("delete_confirmation")
    required_text = f"I, {request.user.display_name}, hereby confirm my request to delete my account permanently. I understand that all my journal entries, AI assessments, and scores will be lost forever."

    if confirm_text != required_text:
        return (
            tool_call.id,
            "\n❌ Invalid confirmation string. Please type the exact phrase to proceed.\n",
            {"message": "Invalid confirmation string."},
        )

    delete_url = urljoin(str(request.base_url), "delete-account")
    token = request.headers.get("authorization")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{delete_url}",
            json={"delete_confirmation": confirm_text},
            headers={"Authorization": token},
        ) as resp:
            result = await resp.json()
            if resp.status == 200:
                return (
                    tool_call.id,
                    "\n✅ Account successfully deleted.\n",
                    {"message": "Account successfully deleted."},
                )
            else:
                return (
                    tool_call.id,
                    f"\n❌ Deletion failed: {result.get('message')}\n",
                    {"message": "Account deletion failed."},
                )

def extract_location(confirm_text: str, user_email: str) -> Optional[str]:
    prefix = f"I, {user_email}, hereby confirm my request to change my location to "

    if not confirm_text.startswith(prefix):
        return None

    location = confirm_text[len(prefix):].strip()
    if location.endswith('.'):
        location = location[:-1].strip()
    if not location or "{" in location or "}" in location or location == 'new-location':
        return None
    
    return location

# Refactor helper for change_location
async def handle_change_location(tool_call, args, request):
    # print(tool_call.function.arguments)
    confirm_text = args.get("change_location_confirmation")
    location = extract_location(confirm_text=confirm_text, user_email=request.user.display_name)
    # print(f"location:{location}")

    # required_text = f"I, {request.user.display_name}, hereby confirm my request to change my location to Cleveland, Ohio."

    if not location:
        return (
            tool_call.id,
            "\n❌ Invalid confirmation string. Please type the exact phrase to proceed.\n",
            {"message": "Invalid confirmation string."},
        )

    save_preferences_url = urljoin(str(request.base_url), "save-preferences")
    token = request.headers.get("authorization")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{save_preferences_url}",
            json={"location": f"{location}"},
            headers={"Authorization": token},
        ) as resp:
            result = await resp.json()
            if resp.status == 200:
                return (
                    tool_call.id,
                    "\n✅ Location successfully changed.\n",
                    {"message": "Location successfully changed."},
                )
            else:
                return (
                    tool_call.id,
                    f"\n❌ Change failed: {result.get('message')}\n",
                    {"message": "Location change failed."},
                )
