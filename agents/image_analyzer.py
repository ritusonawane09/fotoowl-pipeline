import os
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from state import PipelineState
from schemas import ImageAnalysis
from model_config import MODEL_ROUTING
from cache_utils import load_image_analysis_cache, normalize_image_path, save_image_analyses

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=MODEL_ROUTING["image_analyser"],
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

structured_llm = llm.with_structured_output(ImageAnalysis)


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _analyse_single_image(image_path: str) -> ImageAnalysis:
    b64_image = _encode_image(image_path)

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Analyse this event photo. Describe what is happening in one or two "
                    "sentences, estimate its technical/compositional quality from 0 to 1, "
                    "and give 3-5 short keyword tags. Be specific to what you actually see "
                    "in THIS photo, not a generic description."
                ),
            },
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{b64_image}",
            },
        ]
    )

    result: ImageAnalysis = structured_llm.invoke([message])
    result.image_path = image_path
    return result


def image_analyzer(state: PipelineState) -> PipelineState:
    image_paths = state["image_paths"]
    cached_analyses = load_image_analysis_cache()

    analyses = []
    for image_path in image_paths:
        cache_key = normalize_image_path(image_path)
        if cache_key in cached_analyses:
            analysis = cached_analyses[cache_key]
            analysis.image_path = image_path
            print(f"Using cached analysis: {image_path}")
            analyses.append(analysis)
            continue

        print(f"Analyzing: {image_path}")
        analysis = _analyse_single_image(image_path)
        analyses.append(analysis)
        cached_analyses[cache_key] = analysis
        save_image_analyses(list(cached_analyses.values()))
        print(f"  -> {analysis.description}  [tags: {analysis.tags}]")

    state["image_descriptions"] = analyses
    return state


if __name__ == "__main__":
    import glob
    from cache_utils import save_image_analyses

    image_files = sorted(
        glob.glob("input_images/*.jpg") + glob.glob("input_images/*.jpeg") + glob.glob("input_images/*.png")
    )

    test_state: PipelineState = {
        "user_prompt": "",
        "image_paths": image_files,
    }
    result = image_analyzer(test_state)

    print("\n===== IMAGE ANALYSES =====")
    for a in result["image_descriptions"]:
        print(a.image_path)
        print(f"  description : {a.description}")
        print(f"  quality     : {a.quality_score}")
        print(f"  tags        : {a.tags}")
        print("-" * 50)

    save_image_analyses(result["image_descriptions"])
