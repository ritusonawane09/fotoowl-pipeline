import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from model_config import MODEL_ROUTING
from state import PipelineState

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=MODEL_ROUTING["script_generator"],
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

remotion_store = Chroma(
    collection_name="remotion_docs",
    embedding_function=embeddings,
    persist_directory="rag/chroma_db",
)


def _retrieve_remotion_docs(storyboard) -> str:
    query = "Remotion sequence timing transitions image display captions"
    try:
        results = remotion_store.similarity_search(query, k=4)
    except Exception as exc:
        print(f"  [RAG] Remotion doc retrieval unavailable ({type(exc).__name__}); using generic Remotion guidance.")
        return "Use Composition, Sequence, AbsoluteFill, Img, interpolate, and staticFile from Remotion."

    print(f"  [RAG] Retrieved {len(results)} Remotion doc snippets: "
          f"{[r.metadata['source'] for r in results]}")

    return "\n\n".join(f"# {r.metadata['source']}\n{r.page_content}" for r in results)


def _format_storyboard(storyboard) -> str:
    lines = [f"Narrative: {storyboard.narrative_summary}", ""]
    for scene in storyboard.scenes:
        lines.append(
            f"Scene {scene.order}: image={scene.image_path}, "
            f"duration={scene.duration_seconds}s, transition={scene.transition_in}, "
            f"caption='{scene.caption}'"
        )
    return "\n".join(lines)


def _clean_llm_code(script_text: str) -> str:
    script_text = script_text.strip()
    if script_text.startswith("```"):
        lines = script_text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        script_text = "\n".join(lines)
    return script_text


def _fallback_remotion_script(storyboard) -> str:
    scene_blocks = []
    current_frame = 0
    total_frames = 0

    for scene in storyboard.scenes:
        duration_frames = max(30, int(round(scene.duration_seconds * 30)))
        total_frames += duration_frames

        image_path = json.dumps(scene.image_path.replace("\\", "/"))
        caption = json.dumps(scene.caption or "")

        scene_blocks.append(
            f"""      <Sequence from={current_frame} durationInFrames={duration_frames}>
        <AbsoluteFill style={{{{backgroundColor: 'black'}}}}>
          <Img
            src={{staticFile({image_path})}}
            style={{{{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - {current_frame}, [0, 20], [0, 1], {{extrapolateRight: 'clamp'}}),
            }}}}
          />
          {{{caption} && (
            <AbsoluteFill
              style={{{{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}}}
            >
              <div>{{{caption}}}</div>
            </AbsoluteFill>
          )}}
        </AbsoluteFill>
      </Sequence>"""
        )
        current_frame += duration_frames

    total_frames = max(total_frames, 30)
    scenes_code = "\n".join(scene_blocks)

    return f"""import React from 'react';
import {{AbsoluteFill, Composition, Img, Sequence, interpolate, staticFile, useCurrentFrame}} from 'remotion';

export const EventReel: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{{{backgroundColor: 'black'}}}}>
{scenes_code}
    </AbsoluteFill>
  );
}};

export const RemotionRoot: React.FC = () => {{
  return (
    <Composition
      id="EventReel"
      component={{EventReel}}
      durationInFrames={total_frames}
      fps={{30}}
      width={{1080}}
      height={{1920}}
    />
  );
}};
"""


def script_generator(state: PipelineState) -> PipelineState:
    storyboard = state["storyboard"]

    remotion_docs_text = _retrieve_remotion_docs(storyboard)
    storyboard_text = _format_storyboard(storyboard)

    error_context = ""
    if state.get("compile_error"):
        error_context = f"""
        IMPORTANT: a previous version of this script failed to compile with
        this error - fix it:
        {state["compile_error"]}
        """

    prompt = f"""
    Write a complete Remotion composition in TypeScript/React named
    "EventReel" that implements the storyboard below.

    Reference Remotion API patterns you can use (from our knowledge base):
    {remotion_docs_text}

    Storyboard to implement:
    {storyboard_text}

    Requirements:
    - Use 30fps. Convert each scene's duration_seconds to frames (seconds * 30).
    - Wrap each scene in a <Sequence from={{...}} durationInFrames={{...}}>.
    - Use Remotion's <Img> component for images, objectFit 'cover'.
    - Apply the specified transition_in style using interpolate/opacity where
      the style is 'fade'; for other styles, use a reasonable simple approach.
    - If a caption is non-empty, render it using AbsoluteFill as shown in the
      reference patterns.
    - Export a functional component and register it via <Composition> from
      'remotion', with a totalDurationInFrames matching the sum of all scenes.
    - Output ONLY the raw code, no markdown fences, no explanation text.

    {error_context}
    """

    try:
        response = llm.invoke(prompt)
        script_text = _clean_llm_code(response.content)
    except Exception as exc:
        print(f"  [ScriptGenerator] LLM unavailable ({type(exc).__name__}); using deterministic fallback.")
        script_text = _fallback_remotion_script(storyboard)

    state["remotion_script"] = script_text
    return state


if __name__ == "__main__":
    from agents.intent_parser import intent_parser
    from cache_utils import load_image_analyses

    test_state: PipelineState = {
        "user_prompt": "Cinematic wedding reel, slow and emotional, warm tones, minimal text",
    }

    print("Running intent_parser...")
    test_state = intent_parser(test_state)

    print("Loading cached image analyses...")
    test_state["image_descriptions"] = load_image_analyses()

    print("Running storyboard_writer...")
    from agents.storyboard_writer import storyboard_writer
    test_state = storyboard_writer(test_state)

    print("Running script_generator...")
    test_state = script_generator(test_state)

    print("\n===== GENERATED REMOTION SCRIPT =====")
    print(test_state["remotion_script"])

    os.makedirs("output", exist_ok=True)
    with open("output/EventReel.tsx", "w", encoding="utf-8") as f:
        f.write(test_state["remotion_script"])
    print("\nSaved to output/EventReel.tsx")
