import json
import base64
from pathlib import Path
from openai import OpenAI
from dotenv import dotenv_values

class Image_Generator():

    def __init__(self):
        config = dotenv_values(".env")
        self.client = OpenAI(api_key=config.get("API_KEY"), project=config.get("PROJECT_ID"))


    def generate_images(self, image_path, prompts, context):

        for i, prompt in enumerate(prompts):
            self.generate_image(f"{image_path}/image_{i}.png", prompt, context)
        

    def generate_image(self, image_path, prompt, context):
        full_prompt = f"{context} {prompt}"
        print(full_prompt)

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            response_format="b64_json",
            n=1
        )

        image_path = Path(image_path)

        image_data = base64.b64decode(response.data[0].b64_json)
        image_path.parent.mkdir(parents=True, exist_ok=True)  # Create directories if needed

        with open(image_path, "wb") as img_file:
            img_file.write(image_data)



