import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from state import PipelineState
from schemas import VideoIntent
from model_config import MODEL_ROUTING

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=MODEL_ROUTING["intent_parser"],
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


structured_llm = llm.with_structured_output(VideoIntent)


def _fallback_intent(user_prompt: str) -> VideoIntent:
    prompt = user_prompt.lower()

    style = "cinematic" if "cinematic" in prompt else "upbeat" if "upbeat" in prompt else "minimal"
    tone = "emotional" if any(word in prompt for word in ["emotional", "warm", "romantic"]) else "energetic"
    pacing = "slow" if any(word in prompt for word in ["slow", "calm", "emotional"]) else "fast" if "fast" in prompt else "medium"
    transitions = "fade" if "fade" in prompt or pacing == "slow" else "cut"

    return VideoIntent(
        style=style,
        tone=tone,
        pacing=pacing,
        transitions=transitions,
    )


def intent_parser(state: PipelineState) -> PipelineState:
    """
    Reads the user's prompt and converts it into
    a structured VideoIntent object.
    """

    prompt = f"""
    Extract the user's video editing preferences.

    User prompt:
    {state["user_prompt"]}
    """

    try:
        result = structured_llm.invoke(prompt)
    except Exception as exc:
        print(f"  [IntentParser] LLM unavailable ({type(exc).__name__}); using keyword fallback.")
        result = _fallback_intent(state["user_prompt"])

    state["video_intent"] = result

    return state
