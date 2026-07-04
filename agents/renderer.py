import os
import subprocess
import shutil
from state import PipelineState

OUTPUT_DIR = "output"
REMOTION_PROJECT_DIR = "remotion_project"


def _remotion_project_exists() -> bool:
    return os.path.isdir(REMOTION_PROJECT_DIR) and os.path.isfile(
        os.path.join(REMOTION_PROJECT_DIR, "package.json")
    )


def renderer(state: PipelineState) -> PipelineState:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    script_path = os.path.join(OUTPUT_DIR, "EventReel.tsx")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(state.get("remotion_script", ""))

    if os.getenv("ENABLE_REMOTION_RENDER") != "1":
        message = (
            f"Render skipped by default. The compiled/validated script has been saved to "
            f"'{script_path}'. Set ENABLE_REMOTION_RENDER=1 to attempt MP4 rendering."
        )
        print(f"  [Renderer] {message}")
        state["render_success"] = False
        state["output_video_path"] = None
        state["render_output"] = message
        return state

    if not _remotion_project_exists():
        message = (
            "Remotion project not set up in this environment (no "
            f"'{REMOTION_PROJECT_DIR}/package.json' found) - render skipped. "
            "The compiled/validated script has been saved to "
            f"'{script_path}' for manual inspection or rendering. "
            "See README 'Known limitations' for what would be needed to "
            "complete this step (Node.js + `npx remotion render`)."
        )
        print(f"  [Renderer] {message}")
        state["render_success"] = False
        state["output_video_path"] = None
        state["render_output"] = message
        return state

    print("  [Renderer] Remotion project found - attempting real render...")
    try:
        output_video_path = os.path.join(OUTPUT_DIR, "event_reel.mp4")
        npx_command = shutil.which("npx.cmd") or shutil.which("npx")
        if not npx_command:
            raise FileNotFoundError("npx was not found on PATH")

        result = subprocess.run(
            [npx_command, "remotion", "render", "EventReel", output_video_path],
            cwd=REMOTION_PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            print(f"  [Renderer] SUCCESS -> {output_video_path}")
            state["render_success"] = True
            state["output_video_path"] = output_video_path
            state["render_output"] = result.stdout
        else:
            print(f"  [Renderer] FAILED: {result.stderr[:500]}")
            state["render_success"] = False
            state["output_video_path"] = None
            state["render_output"] = result.stderr

    except Exception as e:
        print(f"  [Renderer] EXCEPTION during render: {e}")
        state["render_success"] = False
        state["output_video_path"] = None
        state["render_output"] = str(e)

    return state


if __name__ == "__main__":
    test_state: PipelineState = {
        "remotion_script": "// dummy script for testing renderer fallback\nconsole.log('hello');",
    }
    result = renderer(test_state)
    print("\nrender_success:", result["render_success"])
    print("output_video_path:", result["output_video_path"])
    print("render_output:", result["render_output"])
