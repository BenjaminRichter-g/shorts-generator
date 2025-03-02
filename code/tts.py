import json
import base64
from pathlib import Path
from openai import OpenAI
from dotenv import dotenv_values
import random as rd
import script_creation

class Speech_Generator():

    def __init__(self):
        config = dotenv_values(".env")
        self.client = OpenAI(api_key=config.get("API_KEY"), project=config.get("PROJECT_ID"))
        self.sc = script_creation.Script_Generator()


    def generate_audio(self, audio_path, prompts):
        Path(audio_path).mkdir(parents=True, exist_ok=True)
        
        voices = ["fable", "shimmer", "echo", "onyx"]
        voice = rd.choice(voices)

        for i, prompt in enumerate(prompts):
            try:
                self.generate_line(f"{audio_path}/audio_{i}.mp3", prompt, voice)
            except Exception as e:
                new_prompt = self.sc.regenerate_script_line(prompt)
                self.generate_line(f"{audio_path}/audio_{i}.mp3", new_prompt, voice)

        print("Audio files generated successfully!")
        

    def generate_line(self, audio_path, prompt, voice= 'Onyx'):
        response = self.client.audio.speech.create(model="tts-1",
                                              voice=voice,
                                              input=prompt,
                                            )

        with open(audio_path, "wb") as audio_file:
            audio_file.write(response.content)
       

