from openai import OpenAI
from dotenv import dotenv_values
import re
import tiktoken
import json


class Script_Processor:
    def __init__(self):
        self.unprossed_script = ""
        self.processed_script = ''
    
    def process_script(self, path, write_to_file=True):
        "If write to file is set to true it'll write to file and return json"
        self.text_to_dict(path)
        
        if write_to_file:
            path = path.replace("scripts", "processed_scripts")
            return self.to_json(path.replace(".txt", ".json"))
        return self.to_json()
    
    def extract_script(self, path):
        with open(path, "r") as file:
            return file.readlines()

   
    
    
    def text_to_dict(self, path):
        self.unprossed_script = self.extract_script(path)
        all_substories = []
        current_substory = {}
        mode = None  # Keeps track of the active section (e.g., lines, prompts)
    
        for line in self.unprossed_script:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
    
            # Check for the start of a new substory
            if line.startswith("**Substory Title**") or line.startswith("**Substory"):
                # If there's an existing substory, save it to the list
                if current_substory:
                    all_substories.append(current_substory)
                # Start a new substory
                current_substory = {"title": line.split(":", 1)[1].strip()}
                mode = None  # Reset mode for the new substory
    
            # Check for section markers
            elif "**Script**" in line:
                current_substory["lines"] = []
                mode = "lines"
            elif "**Image Prompts**" in line:
                current_substory["prompts"] = []
                mode = "prompts"
            elif line.startswith("**General Script Prompt**") or line.startswith("**General Image Prompt**"):
                current_substory["general_prompt"] = line.split(":", 1)[1].strip()
                mode = None  # General prompts don't have chunks
    
            # Process chunks based on the active mode
            elif line.startswith("- Chunk") or line.startswith("- **Chunk"):
                chunk_content = line.split(":", 1)[1].strip()
                if mode == "lines":
                    current_substory.setdefault("lines", []).append(chunk_content)
                elif mode == "prompts":
                    current_substory.setdefault("prompts", []).append(chunk_content)
    
        # Append the last substory
        if current_substory:
            all_substories.append(current_substory)
    
        self.processed_script = {"substories": all_substories}
        return self.processed_script




    def to_json(self, path=None):
        """Returns the processed script as a JSON string or saves to a file."""
        json_output = json.dumps(self.processed_script, indent=4)
        if path:
            with open(path, "w") as file:
                file.write(json_output)
        return json_output

class Script_Generator:
    def __init__(self):
        self.data = []
        config = dotenv_values(".env")
        self.client =  OpenAI(api_key=config.get("API_KEY"),project=config.get("PROJECT_ID"))

    def create_script(self, data, ignore_processed_data=True):
        self.data = data
        scripts = []

        cleaned_title = self.clean_title_name(self.data.title)
       
        # check if script file already exists
        if ignore_processed_data:
            #TODO reomve the {0} part and do a contain search 
            try:
                with open(f"data_output/scripts/{cleaned_title}_{0}.txt", "r") as _:
                    print("Script already exists for this data.")
                    return
            except FileNotFoundError:
                pass
        
        parts = self.token_format(self.data)
        for part in parts:
            scripts.append(self.generate_script(chapter=part, title=self.data.title, num_scripts=3))
        
        for i, script in enumerate(scripts):
            self.write_script(script, f"{cleaned_title}_{i}") 

    def write_script(self, script, title):
        if script != None:
            print("Writing script to file...")
            with open(f"data_output/scripts/{title}.txt", "w") as my_file:
                my_file.write(script)
        else:
            print("Error generating script.")

    
    def token_format(self, data):
        MAX_TOKENS = 8000  
        MIN_LAST_CHUNK = 2000
    
        encoding = tiktoken.encoding_for_model(data.model)  
        tokens = encoding.encode(data.text) 
    
        if len(tokens) > MAX_TOKENS:
            num_chunks = len(tokens) // MAX_TOKENS
            avg_chunk_size = len(tokens) // (num_chunks + 1)
    
            if len(tokens) % MAX_TOKENS < MIN_LAST_CHUNK:
                avg_chunk_size = len(tokens) // num_chunks
    
            avg_chunk_size = int(avg_chunk_size)
    
            token_chunks = [
                tokens[i:i+avg_chunk_size] 
                for i in range(0, len(tokens), avg_chunk_size)
            ]
    
            text_chunks = [encoding.decode(chunk) for chunk in token_chunks]
    
            return text_chunks
        else:
            return [data.text]


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
                model="gpt-4o",
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

