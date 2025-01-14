import information_extraction as ie
import script_creation as sc
import sys


def main(scriptOnly=False):


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
    
    extraction = ie.Extract_Information("./data_source/epdf.pub_priests-of-mars2630113e4568e40991a57be123f3e78049575.epub")
    script_generator = sc.Script_Generator()

    print(extraction.get_chapter_info(displayInfo=True))

    chapters = extraction.get_chapters()

    for chapter in chapters:
        
        script_generator.create_script((chapter.get_text(), chapter.get_title()))


    if scriptOnly:
        return

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
