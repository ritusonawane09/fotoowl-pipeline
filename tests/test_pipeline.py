"""
Test suite - runs entirely without API keys. Every LLM call is replaced with
a mock (a fake stand-in returning pre-written data), so these tests run in
milliseconds and never touch the network.

Run: pytest tests/ -v
"""

from unittest.mock import patch, MagicMock
import pytest

from schemas import VideoIntent, ImageAnalysis, Storyboard, StoryboardScene
from state import PipelineState


def test_intent_parser_cinematic_prompt():
    from agents.intent_parser import intent_parser

    fake_intent = VideoIntent(
        style="cinematic",
        tone="emotional",
        pacing="slow",
        transitions="fade",
    )

    with patch("agents.intent_parser.structured_llm") as mock_llm:
        mock_llm.invoke.return_value = fake_intent

        state: PipelineState = {
            "user_prompt": "Cinematic wedding reel, slow and emotional, warm tones"
        }
        result = intent_parser(state)

    assert result["video_intent"].style == "cinematic"
    assert result["video_intent"].pacing == "slow"
    mock_llm.invoke.assert_called_once()


def test_intent_parser_upbeat_prompt():
    from agents.intent_parser import intent_parser

    fake_intent = VideoIntent(
        style="upbeat",
        tone="energetic",
        pacing="fast",
        transitions="cut",
    )

    with patch("agents.intent_parser.structured_llm") as mock_llm:
        mock_llm.invoke.return_value = fake_intent

        state: PipelineState = {
            "user_prompt": "Upbeat birthday reel, fast cuts, bold captions, energetic"
        }
        result = intent_parser(state)

    assert result["video_intent"].style == "upbeat"
    assert result["video_intent"].pacing == "fast"
    assert result["video_intent"].style != "cinematic"


def test_storyboard_writer_selects_subset_and_uses_retrieval():
    from agents.storyboard_writer import storyboard_writer

    fake_intent = VideoIntent(style="cinematic", tone="emotional", pacing="slow", transitions="fade")

    fake_analyses = [
        ImageAnalysis(image_path=f"img{i}.jpg", description=f"photo {i}", quality_score=0.8, tags=["tag"])
        for i in range(5)
    ]

    fake_storyboard = Storyboard(
        scenes=[
            StoryboardScene(image_path="img0.jpg", order=1, duration_seconds=4.0, caption="", transition_in="fade"),
            StoryboardScene(image_path="img2.jpg", order=2, duration_seconds=4.0, caption="", transition_in="fade"),
        ],
        narrative_summary="A short emotional arc.",
    )

    fake_retrieved_doc = MagicMock()
    fake_retrieved_doc.metadata = {"source": "cinematic"}
    fake_retrieved_doc.page_content = "Cinematic style guide text."

    with patch("agents.storyboard_writer.structured_llm") as mock_llm, \
         patch("agents.storyboard_writer.style_store") as mock_store:

        mock_llm.invoke.return_value = fake_storyboard
        mock_store.similarity_search.return_value = [fake_retrieved_doc]

        state: PipelineState = {
            "video_intent": fake_intent,
            "image_descriptions": fake_analyses,
        }
        result = storyboard_writer(state)

    assert len(result["storyboard"].scenes) < len(fake_analyses)
    mock_store.similarity_search.assert_called_once()


def test_script_generator_falls_back_when_llm_is_unavailable():
    from agents.compiler_fixer import compiler_fixer
    from agents.script_generator import script_generator

    storyboard = Storyboard(
        scenes=[
            StoryboardScene(
                image_path="input_images/DSC_6588.jpg",
                order=1,
                duration_seconds=4.0,
                caption="A quiet bridal portrait",
                transition_in="fade",
            )
        ],
        narrative_summary="A short emotional bridal portrait.",
    )

    fake_doc = MagicMock()
    fake_doc.metadata = {"source": "sequence_basics"}
    fake_doc.page_content = "Use Sequence for timed scenes."

    with patch("agents.script_generator.remotion_store") as mock_store, \
         patch("agents.script_generator.llm") as mock_llm:

        mock_store.similarity_search.return_value = [fake_doc]
        mock_llm.invoke.side_effect = RuntimeError("quota exhausted")

        state: PipelineState = {"storyboard": storyboard}
        result = script_generator(state)

    assert "export const EventReel" in result["remotion_script"]
    assert "<Composition" in result["remotion_script"]
    assert "<Sequence" in result["remotion_script"]

    checked = compiler_fixer({
        "remotion_script": result["remotion_script"],
        "retry_count": 0,
        "max_retries": 3,
    })
    assert checked["compile_success"] is True


def test_compiler_fixer_retry_cap_triggers_graceful_failure():
    from agents.compiler_fixer import compiler_fixer

    bad_script = "const X = () => { return <div>no remotion stuff here</div> };"

    state: PipelineState = {"remotion_script": bad_script, "retry_count": 0, "max_retries": 3}
    for _ in range(3):
        state = compiler_fixer(state)

    assert state["pipeline_failed"] is True
    assert state["compile_success"] is False
    assert "failure_reason" in state
    assert state["retry_count"] == 3


def test_compiler_fixer_passes_valid_script():
    from agents.compiler_fixer import compiler_fixer

    good_script = """
    import { Composition, Sequence } from 'remotion';
    export const EventReel = () => { return <Sequence from={0} durationInFrames={90}></Sequence>; };
    export const RemotionRoot = () => { return <Composition id="x" component={EventReel} durationInFrames={90} fps={30} width={1080} height={1920} />; };
    """
    state: PipelineState = {"remotion_script": good_script, "retry_count": 0, "max_retries": 3}
    result = compiler_fixer(state)

    assert result["compile_success"] is True
    assert result.get("pipeline_failed") is not True


def test_compiler_fixer_accepts_typed_react_component_export():
    from agents.compiler_fixer import compiler_fixer

    good_script = """
    import React from 'react';
    import { Composition, Sequence } from 'remotion';
    export const EventReel: React.FC = () => { return <Sequence from={0} durationInFrames={90}></Sequence>; };
    export const RemotionRoot: React.FC = () => { return <Composition id="x" component={EventReel} durationInFrames={90} fps={30} width={1080} height={1920} />; };
    """
    state: PipelineState = {"remotion_script": good_script, "retry_count": 0, "max_retries": 3}
    result = compiler_fixer(state)

    assert result["compile_success"] is True
    assert result.get("pipeline_failed") is not True


class CoherenceJudgment(pytest.importorskip("pydantic").BaseModel):
    coherence_score: float
    reasoning: str


def _judge_narrative_coherence(storyboard: Storyboard, judge_llm) -> "CoherenceJudgment":
    prompt = (
        f"Rate the narrative coherence (0-1) of this storyboard: "
        f"{storyboard.narrative_summary}. Scenes: {[s.image_path for s in storyboard.scenes]}"
    )
    return judge_llm.invoke(prompt)


def test_llm_as_judge_narrative_coherence():
    coherent_storyboard = Storyboard(
        scenes=[
            StoryboardScene(image_path="bride_solo.jpg", order=1, duration_seconds=5.0, caption="", transition_in="fade"),
            StoryboardScene(image_path="couple_walking.jpg", order=2, duration_seconds=5.0, caption="", transition_in="fade"),
            StoryboardScene(image_path="couple_embrace.jpg", order=3, duration_seconds=5.0, caption="", transition_in="fade"),
        ],
        narrative_summary="Bride's solo portrait transitions into the couple's growing intimacy.",
    )

    mock_judge = MagicMock()
    mock_judge.invoke.return_value = CoherenceJudgment(
        coherence_score=0.9,
        reasoning="Clear emotional progression from individual to couple moments.",
    )

    result = _judge_narrative_coherence(coherent_storyboard, mock_judge)

    assert result.coherence_score >= 0.7
    assert isinstance(result.reasoning, str) and len(result.reasoning) > 0
    mock_judge.invoke.assert_called_once()
