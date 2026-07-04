import json
import os
from schemas import ImageAnalysis

CACHE_PATH = "output/image_analysis_cache.json"


def normalize_image_path(image_path: str) -> str:
    return os.path.normcase(os.path.normpath(image_path))


def save_image_analyses(analyses: list[ImageAnalysis]):
    os.makedirs("output", exist_ok=True)
    data = [a.model_dump() for a in analyses]
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Cached {len(analyses)} image analyses to {CACHE_PATH}")


def load_image_analyses() -> list[ImageAnalysis]:
    if not os.path.exists(CACHE_PATH):
        raise FileNotFoundError(
            f"No cache found at {CACHE_PATH}. Run 'python -m agents.image_analyzer' once first."
        )
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ImageAnalysis(**item) for item in data]


def load_image_analysis_cache() -> dict[str, ImageAnalysis]:
    if not os.path.exists(CACHE_PATH):
        return {}
    analyses = load_image_analyses()
    return {normalize_image_path(item.image_path): item for item in analyses}
