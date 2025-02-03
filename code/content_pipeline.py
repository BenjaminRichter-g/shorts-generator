import information_extraction as ie
import os
import script_creation as sc
import image_generator as ig
import tts as tts
import video_assembler as va
import sys
from uuid import uuid4
import shutil
from pathlib import Path


def main(scriptOnly=False, process_only=True):


    # TODO ok so it works now, next step is to create a system which can process each chapter at a time
    """
    1. Find a way to determine number of short stories depeding on length of chapter 
    2. Find a way of creating a separate file for each response
    3. Find a way of consuming these for the next part (aka image generation, tts and editing) (maybe dump them in a folder and treat them like a stack)
    4. Find a way of batching this process eventually to drastically reduce costs

    btw we'll start by using Dall-e and tts-1 from OpenAi, we'll ask Sofian later for some good (locally run) tts alternatives and try and connect it to 
    the standard diffusion running locally too.

    Also make sure to Add warhammer in the context, or maybe even a general context variable, to add to the system prompt.
    So that the entire thing can be themed to the universe youre talking about. in this case warhammer 40k
    """
    #TODO add the name of the original work into the folder perhaps?
    #TODO maybe add an option so that instead of creating everything sequentially (for price reason) make a script, image, tts and video folder
    
    script_generator = sc.Script_Generator()
    json_scripts = []
    script_processor = sc.Script_Processor()
    image_generator = ig.Image_Generator()
    tts_generator = tts.Speech_Generator()
    video_assembler = va.Video_Editor()


    if not process_only:
        extraction = ie.Extract_Information("./data_source/epdf.pub_priests-of-mars2630113e4568e40991a57be123f3e78049575.epub", "gpt-4o")
        extraction.get_chapter_info(displayInfo=True)

        chapters = extraction.get_chapters()

        for chapter in chapters:
            script_generator.create_script(chapter)

        if scriptOnly:
            return

        # process the scripts into a json format 
        for generated_script_path in os.listdir("data_output/scripts"):
            json_scripts.append(script_processor.process_script(f"data_output/scripts/{generated_script_path}"))

    
    # gets the files from the processed_scripts folder and processes them into images
    dict_scripts = script_processor.get_all_processed_scripts()
    
    # data_output/packages/ is the path where packets for processing are created
    
    for individual_script in dict_scripts[-1]:

        json_script = individual_script[0]
        for stories in json_script["substories"]:
            uid = uuid4()
            path = f"data_output/packages/{uid}"
            Path(path).mkdir(parents=True, exist_ok=True)
            shutil.copy(individual_script[1], f"{path}/script.json")
            
            # generate all required images
            image_generator.generate_images(f"{path}/images", stories["prompts"], stories["general_prompt"])

            # generate all required audio clip
            tts_generator.generate_audio(f"{path}/audio", stories["lines"]) 
            #stories["lines"]
            
            video_assembler.generate_video(path)

        print(individual_script) 
        #image_generator(individual_script)


if __name__ == "__main__":
    """
    -s create script
    -si create script and images
    -sit create script and images
    -sitv do previous and edit video
    """
    
    if len(sys.argv) > 1:
        if "-s" in sys.argv:
            main(scriptOnly=True)
    else:
        main()
