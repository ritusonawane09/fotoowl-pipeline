"""
Main pipeline graph: wires all 6 nodes together using LangGraph's StateGraph.

Flow:
    intent_parser -> image_analyzer -> storyboard_writer -> script_generator
        -> compiler_fixer --(success)--> renderer -> END
                          --(failure, retries left)--> back to script_generator
                          --(failure, retry cap hit)--> END (pipeline_failed=True)
"""

from langgraph.graph import StateGraph, END

from state import PipelineState
from agents.intent_parser import intent_parser
from agents.image_analyzer import image_analyzer
from agents.storyboard_writer import storyboard_writer
from agents.script_generator import script_generator
from agents.compiler_fixer import compiler_fixer
from agents.renderer import renderer


def _route_after_compile(state: PipelineState) -> str:
    """
    Conditional edge function. LangGraph calls this after compiler_fixer runs,
    and the STRING it returns picks which node runs next.
    """
    if state.get("compile_success"):
        return "render"
    if state.get("pipeline_failed"):
        return "give_up"
    return "retry"


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("intent_parser", intent_parser)
    graph.add_node("image_analyzer", image_analyzer)
    graph.add_node("storyboard_writer", storyboard_writer)
    graph.add_node("script_generator", script_generator)
    graph.add_node("compiler_fixer", compiler_fixer)
    graph.add_node("renderer", renderer)

    graph.set_entry_point("intent_parser")
    graph.add_edge("intent_parser", "image_analyzer")
    graph.add_edge("image_analyzer", "storyboard_writer")
    graph.add_edge("storyboard_writer", "script_generator")
    graph.add_edge("script_generator", "compiler_fixer")

    graph.add_conditional_edges(
        "compiler_fixer",
        _route_after_compile,
        {
            "render": "renderer",
            "retry": "script_generator",
            "give_up": END,
        },
    )

    graph.add_edge("renderer", END)

    return graph.compile()


if __name__ == "__main__":
    # Full end-to-end run. This WILL make real API calls (image analysis +
    # intent + storyboard + script generation), so only run this once
    # quota is available.
    app = build_graph()

    initial_state: PipelineState = {
        "user_prompt": "Cinematic wedding reel, slow and emotional, warm tones, minimal text",
        "image_paths": [
            "input_images/DSC_6588.jpg",
            "input_images/DSC_6596.jpg",
            "input_images/DSC_6605.jpg",
        ],
        "retry_count": 0,
        "max_retries": 3,
    }

    final_state = app.invoke(initial_state)

    print("\n===== FINAL PIPELINE STATE SUMMARY =====")
    print("pipeline_failed:", final_state.get("pipeline_failed"))
    print("compile_success:", final_state.get("compile_success"))
    print("render_success:", final_state.get("render_success"))
    print("retry_count:", final_state.get("retry_count"))
    print("render_output:", final_state.get("render_output"))
    