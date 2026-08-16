import sys
import asyncio
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import google, openai

# Custom modules
from Jarvis_prompts import load_prompts
from memory_loop import MemoryExtractor
import os
from mem0 import AsyncMemoryClient
import logging

from config_manager import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = ConfigManager()
load_dotenv()


class Assistant(Agent):
    def __init__(self, chat_ctx, llm_instance, instructions_text) -> None:
        super().__init__(
            instructions=instructions_text,
            chat_ctx=chat_ctx,
            llm=llm_instance
        )


async def entrypoint(ctx: agents.JobContext):
    config.load_config()

    # Load prompts
    instructions_prompt, reply_prompt = await load_prompts()

    user_id = config.get_user_id()
    full_name = config.get_full_name()
    mem0_key = config.get_mem0_key()

    logger.info(f"Starting agent for user: {user_id} ({full_name})")

    # =========================
    # MEMORY (SAFE VERSION)
    # =========================
    memory_str = "\n(Memory disabled)"

    try:
        if mem0_key:
            mem0_client = AsyncMemoryClient(api_key=mem0_key)

            all_memories = await mem0_client.get_all(filters={"user_id": user_id})

            memory_str = "\n".join([
                m.get('memory', '') or m.get('text', '')
                for m in all_memories
            ])

            if memory_str:
                memory_str = f"\n\nKNOWN USER HISTORY:\n{memory_str}"
            else:
                memory_str = "\n(No previous history found.)"

    except Exception as e:
        logger.warning(f"Memory disabled due to error: {e}")

    # =========================
    # LLM CONFIG
    # =========================
    llm_config = config.get_llm_config()
    provider = llm_config.get("provider", "google")
    model_name = llm_config.get("model", "gemini-2.5-flash-native-audio-preview-09-2025")
    voice_name = llm_config.get("voice", "Puck")

    logger.info(f"Using LLM: {provider} | Model: {model_name}")

    # Create LLM
    if provider == "google":
        api_key = config.get_api_key("google")
        llm_instance = google.beta.realtime.RealtimeModel(
            model=model_name,
            api_key=api_key,
            voice=voice_name
        )
    else:
        api_key = config.get_api_key("openai")
        llm_instance = openai.realtime.RealtimeModel(
            model=model_name,
            api_key=api_key,
            voice=voice_name
        )

    # =========================
    # SESSION START
    # =========================
    session = AgentSession()
     
   

    initial_ctx = ChatContext()
    initial_ctx.add_message(
        role="assistant",
        content=f"The user's name is {full_name}.{memory_str}"
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(
            chat_ctx=initial_ctx,
            llm_instance=llm_instance,
            instructions_text=instructions_prompt
        ),
        room_input_options=RoomInputOptions()
    )

    await asyncio.sleep(2)

    # Initial reply
    await session.generate_reply(
        instructions=reply_prompt
    )
    

    # Initial reply
    await session.generate_reply(
        instructions=reply_prompt
    )

    # Memory loop
    conv_ctx = MemoryExtractor()
    await conv_ctx.run(session.history.items)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    import asyncio
    import time

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    print("Agent starting...")

    while True:
        config.load_config()

        lk_url = config.get_api_key("livekit_url")
        lk_key = config.get_api_key("livekit_api_key")
        lk_secret = config.get_api_key("livekit_api_secret")

        if lk_url and lk_key and lk_secret:
            print(f"Connecting to LiveKit: {lk_url}")

            os.environ["LIVEKIT_URL"] = lk_url
            os.environ["LIVEKIT_API_KEY"] = lk_key
            os.environ["LIVEKIT_API_SECRET"] = lk_secret

            if config.get_api_key("google"):
                os.environ["GOOGLE_API_KEY"] = config.get_api_key("google")

            if config.get_api_key("openai"):
                os.environ["OPENAI_API_KEY"] = config.get_api_key("openai")

            break
        else:
            print("Waiting for setup...")
            time.sleep(2)

    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name="jarvis-agent")
    )