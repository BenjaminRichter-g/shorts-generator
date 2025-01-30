import json
import base64
from pathlib import Path
from openai import OpenAI
from dotenv import dotenv_values

class Speech_Generator():

    def __init__(self):
        config = dotenv_values(".env")
        self.client = OpenAI(api_key=config.get("API_KEY"), project=config.get("PROJECT_ID"))


    def generate_audio(self, audio_path, prompts):
        Path(audio_path).mkdir(parents=True, exist_ok=True)

        for i, prompt in enumerate(prompts):
            self.generate_line(f"{audio_path}/audio_{i}.mp3", prompt)

        print("Audio files generated successfully!")
        

    def generate_line(self, audio_path, prompt):

        response = self.client.audio.speech.create(model="tts-1",
                                              voice="alloy",
                                              input=prompt,
                                            )

        with open(audio_path, "wb") as audio_file:
            audio_file.write(response.content)
       

