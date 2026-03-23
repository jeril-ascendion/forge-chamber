import os

from livekit.plugins import cartesia

VOICE_IDS: dict[str, str] = {
    "sre": "694f9389-aac1-45b6-b726-9d9369183238",  # Deep male
    "sys_arch": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Warm female
    "cloud_eng": "63ff761f-c1e8-414b-b969-d1833d1c870c",  # Neutral male
    "java_dev": "b7d50908-b17c-442d-ad8d-810c63997ed9",  # Crisp male
    "ui_dev": "156fb8d2-335b-4950-9cb3-a2d33befec77",  # Energetic
}

DEFAULT_AGENT_KEY = "sre"


def get_tts_for_agent(agent_key: str) -> cartesia.TTS:
    """Return a Cartesia TTS instance configured with the voice for the given agent."""
    voice_id = VOICE_IDS.get(agent_key, VOICE_IDS[DEFAULT_AGENT_KEY])
    return cartesia.TTS(
        voice=voice_id,
        api_key=os.environ.get("CARTESIA_API_KEY", ""),
    )
