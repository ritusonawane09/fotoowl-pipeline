"""
Agent 3: Storyboard Writer

Reads state["video_intent"] and state["image_descriptions"], RETRIEVES the most
relevant style guide from the Chroma vector store, then asks Gemini to select
and sequence images into a structured Storyboard.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from state import PipelineState
from schemas import Storyboard, StoryboardScene
from model_config import MODEL_ROUTING

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=MODEL_ROUTING["storyboard_writer"],
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
structured_llm = llm.with_structured_output(Storyboard)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

style_store = Chroma(
    collection_name="style_guides",
    embedding_function=embeddings,
    persist_directory="rag/chroma_db",
)


def _retrieve_style_guide(intent) -> str:
    query = f"{intent.style} {intent.tone} {intent.pacing} {intent.transitions}"
    try:
        results = style_store.similarity_search(query, k=1)
    except Exception as exc:
        print(f"  [RAG] Style guide retrieval unavailable ({type(exc).__name__}); using generic guidance.")
        return "Use the strongest images, keep the sequence coherent, and match the requested mood."

    if not results:
        return "No specific style guide found. Use general good judgement."

    top_match = results[0]
    print(f"  [RAG] Retrieved style guide: '{top_match.metadata['source']}' (query: '{query}')")
    return top_match.page_content


def _format_image_descriptions(image_descriptions) -> str:
    lines = []
    for img in image_descriptions:
        lines.append(
            f"- {img.image_path} | quality={img.quality_score} | tags={img.tags} | {img.description}"
        )
    return "\n".join(lines)


def _fallback_storyboard(intent, image_descriptions) -> Storyboard:
    selected = sorted(
        image_descriptions,
        key=lambda img: img.quality_score,
        reverse=True,
    )[: min(5, len(image_descriptions))]

    duration = 4.5 if intent.pacing == "slow" else 3.0 if intent.pacing == "fast" else 4.0
    scenes = []
    for index, image in enumerate(selected, start=1):
        scenes.append(
            StoryboardScene(
                image_path=image.image_path,
                order=index,
                duration_seconds=duration,
                caption="" if "minimal" in intent.transitions or intent.style == "cinematic" else image.tags[0],
                transition_in=intent.transitions or "fade",
            )
        )

    return Storyboard(
        scenes=scenes,
        narrative_summary=(
            f"A {intent.style} {intent.tone} highlight reel built from the strongest "
            "available event images."
        ),
    )


def storyboard_writer(state: PipelineState) -> PipelineState:
    intent = state["video_intent"]
    image_descriptions = state["image_descriptions"]

    style_guide_text = _retrieve_style_guide(intent)

    prompt = f"""
    You are creating a video storyboard for an event highlight reel.

    User's parsed intent:
    - style: {intent.style}
    - tone: {intent.tone}
    - pacing: {intent.pacing}
    - transitions: {intent.transitions}

    Relevant style guide (retrieved from knowledge base, follow this closely):
    {style_guide_text}

    Available photos (not all need to be used - select the best subset that
    tells a coherent story matching the style guide above):
    {_format_image_descriptions(image_descriptions)}

    Create a storyboard: select and order the best photos, assign a duration
    in seconds and a transition style to each, and write a short caption for
    each scene (empty string if the style guide says captions should be rare).
    Also write a one or two sentence narrative_summary describing the story arc.
    """

    try:
        result = structured_llm.invoke(prompt)
    except Exception as exc:
        print(f"  [StoryboardWriter] LLM unavailable ({type(exc).__name__}); using quality-based fallback.")
        result = _fallback_storyboard(intent, image_descriptions)

    state["storyboard"] = result
    return state


if __name__ == "__main__":
    import glob
    from agents.intent_parser import intent_parser
    from agents.image_analyzer import image_analyzer

    image_files = sorted(
        glob.glob("input_images/*.jpg") + glob.glob("input_images/*.jpeg") + glob.glob("input_images/*.png")
    )

    test_state: PipelineState = {
        "user_prompt": "Cinematic wedding reel, slow and emotional, warm tones, minimal text",
        "image_paths": image_files,
    }

    print("Running intent_parser...")
    test_state = intent_parser(test_state)
    print("Intent:", test_state["video_intent"])

    print("Loading cached image analyses...")
    from cache_utils import load_image_analyses
    test_state["image_descriptions"] = load_image_analyses()
    print(f"Analyzed {len(test_state['image_descriptions'])} images.")

    print("\nRunning storyboard_writer...")
    test_state = storyboard_writer(test_state)

    print("\n===== STORYBOARD =====")
    sb = test_state["storyboard"]
    print("Narrative:", sb.narrative_summary)
    for scene in sb.scenes:
        print(f"  #{scene.order} {scene.image_path} | {scene.duration_seconds}s | "
              f"{scene.transition_in} | caption: '{scene.caption}'")
