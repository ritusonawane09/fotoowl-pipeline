from agents.intent_parser import intent_parser

def main() -> None:
    state = {
        "user_prompt": "Create a cinematic wedding reel with warm tones, slow pacing and fade transitions.",
        "image_paths": [],
        "video_intent": None,
        "image_descriptions": None,
        "storyboard": None,
        "remotion_script": None,
        "compile_error": None,
        "render_output": None,
    }

    result = intent_parser(state)

    print("\n===== RESULT =====")
    print(result["video_intent"])


if __name__ == "__main__":
    main()
