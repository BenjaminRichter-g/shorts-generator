from openai import OpenAI
from dotenv import dotenv_values
import re


class Script_Generator:
    def __init__(self):
        self.data = []
        config = dotenv_values(".env")
        self.client =  OpenAI(api_key=config.get("API_KEY"),project=config.get("PROJECT_ID"))

    def create_script(self, data, ignore_processed_data=False):
        self.data = data

        cleaned_title = self.clean_title_name(self.data[1])
        
        if ignore_processed_data == False:
            try:
                with open(f"data_output/scripts/{cleaned_title}.txt", "r") as my_file:
                    print("Script already exists for this data.")
                    return
            except FileNotFoundError:
                pass
        
        script = self.generate_script(chapter=self.data[0], title=self.data[1], num_scripts=3)
       
        if script != None:
            print("Writing script to file...")
            with open(f"data_output/scripts/{cleaned_title}.txt", "w") as my_file:
                my_file.write(script)
        else:
            print("Error generating script.")


    def clean_title_name(self, title):
        cleaned_title = title.replace(" ", "_")
        cleaned_title = re.sub(r'[\/:*?"<>|]', '', cleaned_title)
        cleaned_title = cleaned_title.strip("_")

        return cleaned_title

    def generate_script(self, chapter="", title="", num_scripts=1, prompt="Generate a script the script for the following chapter.", system_message=None):
        """
        Generate scripts for a chapter using GPT.
        
        Args:
            chapter (Chapter): The chapter object.
            num_scripts (int): Number of scripts to generate.
            style (str): Desired script style (e.g., 'dialogue', 'narrative', etc.).
        
        Returns:
            List of generated scripts.
        """
        print('Generating script...')

        if system_message == None:
            system_message = """You are a professional scriptwriter specializing in short-form content creation. 
                                
                                Your task is to:
                                1. Receive a chapter from a book.
                                2. Identify a given number, x, of substories from the chapter.
                                3. Write a short script for each substory. 
                                
                                Requirements for each script:
                                - Each script should narrate a story in a clear and engaging style suitable for a single narrator.
                                - The narration should be concise, designed to be read aloud in 60 seconds.
                                - Give a minimum of 5 chunks of narration for each script.
                                - Divide the script into chunks of 5 to 10 seconds each. Each chunk should contain a single cohesive idea or scene that aligns with the story.
                                - For each chunk, provide a detailed and imaginative prompt for an image generation model to create a relevant background image.
                                - Add a general prompt to be applied the entire script to ensure consistency in the image generation.
                                
                                Output format for each script:
                                - **Substory Title**: [Title of the substory]
                                - **Script**:
                                  - Chunk 1: [Narration text for 5–10 seconds]
                                  - Chunk 2: [Narration text for 5–10 seconds]
                                  - ...
                                - **Image Prompts**:
                                  - Chunk 1 Prompt: [Prompt describing the scene for chunk 1]
                                  - Chunk 2 Prompt: [Prompt describing the scene for chunk 2]
                                  - ...
                                
                                Ensure the output is well-structured and easy to process programmatically.
                                """

        built_prompt = f"""
                        Give me {num_scripts} amount of scripts.
                        {prompt}
                        Title:
                        {title}
                        Chapter:
                        {chapter}
                        """ 
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": built_prompt}
                ],
                max_tokens=2000  # Adjust based on GPT's token limits
            )
            scripts = response.choices[0].message.content
            return scripts
        except Exception as e:
            print(f"Error generating script: {e}")
            return 

