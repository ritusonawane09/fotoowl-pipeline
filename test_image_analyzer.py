import os

from agents.image_analyzer import image_analyzer

def main() -> None:
    state = {
        "user_prompt": "Create a cinematic wedding reel.",
        "image_paths": [
            os.path.join("input_images", file)
            for file in os.listdir("input_images")
        ],
        "image_descriptions": None,
    }

    result = image_analyzer(state)

    print("\n===== IMAGE DESCRIPTIONS =====\n")

    for i, description in enumerate(result["image_descriptions"], start=1):
        print(f"Photo {i}:")
        print(description)
        print("-" * 50)


if __name__ == "__main__":
    main()
