from openai import OpenAI
import os

class Script_Generator:
    def __init__(self, data):
        self.data = data


    def create_script(self):
        # create a script
        script = f"INSERT INTO {self.data['table']} ("

    def prompt_gpt():
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted)
