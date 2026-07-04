
from typing import TypedDict, List, Optional
from schemas import VideoIntent, ImageAnalysis, Storyboard 


class PipelineState(TypedDict):
    """
    Shared state that flows through every LangGraph node.
    Every agent reads from and writes to this object.
    """

    # Input
    user_prompt: str
    image_paths: List[str]

    # Intent Parser output
    video_intent: Optional[VideoIntent]

    # Image Analyzer output
    image_descriptions: Optional[List[ImageAnalysis]]

    # Storyboard Writer output
    storyboard: Optional[Storyboard]

    # Script Generator output
    remotion_script: Optional[str]

    # Compiler output
    compile_error: Optional[str]

    # Renderer output
    render_output: Optional[str]
    render_success: Optional[bool]
    output_video_path: Optional[str]
    
    # Compiler retry tracking
    compile_success: Optional[bool]
    retry_count: Optional[int]
    max_retries: Optional[int]

    # Terminal failure state
    pipeline_failed: Optional[bool]
    failure_reason: Optional[str]
