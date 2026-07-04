# FotoOwl AI Engineer Take-Home: Image-to-Video Multiagent Pipeline

A LangGraph-orchestrated multiagent pipeline that takes a folder of event
photos plus a free-text creative prompt and produces a Remotion video
composition script. If Node.js and Remotion are available, the final renderer
can attempt to render an MP4.

This project is intentionally assessment-sized: it demonstrates architecture,
agent boundaries, structured outputs, RAG usage, retry/failure handling, and a
Remotion handoff without needing to be a polished end-to-end product.

## What It Does

1. Parses the user's creative prompt into a structured `VideoIntent`.
2. Analyzes each event image into descriptions, quality scores, and tags.
3. Retrieves a relevant style guide from the local Chroma vector store.
4. Builds a storyboard from the best subset of images.
5. Retrieves Remotion docs from the local knowledge base.
6. Generates a TypeScript/React Remotion composition.
7. Structurally validates the generated script and retries if needed.
8. Saves the generated script and optionally attempts Remotion rendering.

## Main Files

- `graph.py` wires the LangGraph flow.
- `state.py` defines the shared pipeline state.
- `schemas.py` defines structured Pydantic outputs.
- `model_config.py` centralizes model routing.
- `agents/intent_parser.py` extracts video intent.
- `agents/image_analyzer.py` analyzes images with Gemini vision.
- `agents/storyboard_writer.py` uses RAG and creates the storyboard.
- `agents/script_generator.py` uses RAG and creates Remotion code.
- `agents/compiler_fixer.py` validates generated code and manages retries.
- `agents/renderer.py` saves the script and attempts Remotion rendering.
- `tests/test_pipeline.py` contains offline mocked tests.
- `rag/knowledge/` contains style guides and Remotion reference snippets.
- `remotion_project/` contains the Remotion TypeScript project.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with:

```bash
GOOGLE_API_KEY=your_key_here
```

## Safe Checks

These commands should not call Gemini:

```bash
venv\Scripts\python.exe -m pytest tests -q
cmd /c npm run lint
```

`npm run lint` is invoked through `cmd` on Windows because PowerShell may block
`npm.ps1` depending on the machine's execution policy.

## Manual Gemini Checks

These scripts make real Gemini API calls, so run them only when you have a valid
API key, internet access, and quota:

```bash
venv\Scripts\python.exe test_setup.py
venv\Scripts\python.exe test_intent_parser.py
venv\Scripts\python.exe test_image_analyzer.py
```

They are guarded with `if __name__ == "__main__"` so pytest can safely collect
the project without accidentally making network calls.

## Run The Pipeline

```bash
venv\Scripts\python.exe graph.py
```

This performs real LLM calls. If rendering is unavailable, the renderer still
saves the generated Remotion script to `output/EventReel.tsx`.

## Known Limitations

- The full pipeline depends on Gemini availability, API key validity, and quota.
- The compiler step is a structural validator, not a full TypeScript compiler.
- Rendering depends on the local Node/Remotion setup.
- The project is designed to demonstrate the pipeline architecture rather than
  production deployment, job queues, uploaded assets, auth, or a web UI.

## Interview Explanation

The important design choice is that each agent owns one clear responsibility and
passes structured state forward. The pipeline uses Pydantic schemas to make LLM
outputs predictable, Chroma-based RAG to ground creative/style/code generation,
and a retry loop after validation so script generation can self-correct instead
of failing immediately.

For assessment purposes, the safe mocked tests prove the orchestration logic
without burning API quota, while the manual scripts prove the real Gemini
integration when the environment allows it.
