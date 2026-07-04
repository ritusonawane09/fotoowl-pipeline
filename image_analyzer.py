from PIL import Image

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from state import PipelineState

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


def image_analyzer(state: PipelineState):
    """
    Reads every image and generates descriptions using Gemini.
    """

    image_paths = state["image_paths"]

    descriptions = []

    for image_path in image_paths:
        print("Analyzing: {image_path}")

        image = Image.open(image_path)

        response = llm.invoke(
            [
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": (
                                "Describe this wedding photo in 2-3 sentences. "
                                "Mention the people, actions, emotions, and setting."
                            ),
                        },
                        {
                            "type": "image",
                            "image": image,
                        },
                    ]
                )
            ]
        )

        print(response.content)
        descriptions.append(response.content)

    state["image_descriptions"] = descriptions

    return state