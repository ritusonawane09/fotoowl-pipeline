from pydantic import BaseModel, Field


class VideoIntent(BaseModel):
    style: str = Field(description="Overall visual style")
    tone: str = Field(description="Emotional tone")
    pacing: str = Field(description="Video pacing")
    transitions: str = Field(description="Preferred transition style")


class ImageAnalysis(BaseModel):
    image_path: str = Field(description="Path to the analysed image file")
    description: str = Field(description="What is happening in this photo, specific to its content")
    quality_score: float = Field(description="Estimated technical/compositional quality, 0 to 1")
    tags: list[str] = Field(description="3-5 short keyword tags, e.g. 'group shot', 'candid', 'outdoor'")

class StoryboardScene(BaseModel):
    image_path: str = Field(description="Path to the image used in this scene")
    order: int = Field(description="Position of this scene in the sequence, starting at 1")
    duration_seconds: float = Field(description="How long this scene stays on screen")
    caption: str = Field(description="Caption text for this scene, empty string if none")
    transition_in: str = Field(description="Transition style entering this scene, e.g. fade, cut, slide, zoom")


class Storyboard(BaseModel):
    scenes: list[StoryboardScene] = Field(description="Ordered list of scenes making up the video")
    narrative_summary: str = Field(description="One or two sentence description of the story arc chosen")    