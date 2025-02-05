import sys
import os
import shutil
from uuid import uuid4
from pathlib import Path
import json

import information_extraction as ie
import script_creation as sc
import image_generator as ig
import tts as tts
import video_assembler as va

# ---------------------------------------------------------------------------
# 1. Extraction Step
# ---------------------------------------------------------------------------
def extract_chapters(epub_path: str, model_name: str = "gpt-4o", display_info: bool = True):
    """
    Extract all chapters from the given EPUB and return them.
    """
    extraction = ie.Extract_Information(epub_path, model_name)
    
    if display_info:
        extraction.get_chapter_info(displayInfo=True)
    
    return extraction.get_chapters()

# ---------------------------------------------------------------------------
# 2. Script Creation
# ---------------------------------------------------------------------------
def create_scripts(chapters, script_generator=None):
    """
    Given a list of chapters, create a script file for each.
    """
    if script_generator is None:
        script_generator = sc.Script_Generator()
    
    for chapter in chapters:
        script_generator.create_script(chapter)

# ---------------------------------------------------------------------------
# 3. Process Scripts into JSON
# ---------------------------------------------------------------------------
def process_scripts(input_dir="data_output/scripts"):
    """
    Reads each raw script from `input_dir` and processes it into a standardized JSON structure.
    Returns a list of tuples: [(processed_json_path, original_script_path), ...].
    """
    script_processor = sc.Script_Processor()
    processed = []
    for script_file in os.listdir(input_dir):
        raw_path = os.path.join(input_dir, script_file)
        json_path = script_processor.process_script(raw_path)
        processed.append((json_path, raw_path))
    return processed

# ---------------------------------------------------------------------------
# 4. Generate Images
# ---------------------------------------------------------------------------
def generate_images_for_stories(package_path: str, story):
    image_generator = ig.Image_Generator()
    images_dir = os.path.join(package_path, "images")
    Path(images_dir).mkdir(parents=True, exist_ok=True)
    prompts = story["prompts"]
    general_prompt = story["general_prompt"]
    image_generator.generate_images(images_dir, prompts, general_prompt)

# ---------------------------------------------------------------------------
# 5. Generate TTS Audio
# ---------------------------------------------------------------------------
def generate_audio_for_stories(package_path: str, story):
    tts_generator = tts.Speech_Generator()
    audio_dir = os.path.join(package_path, "audio")
    Path(audio_dir).mkdir(parents=True, exist_ok=True)
    lines = story["lines"]
    tts_generator.generate_audio(audio_dir, lines)

# ---------------------------------------------------------------------------
# 6. Assemble Video
# ---------------------------------------------------------------------------
def assemble_video_from_package(package_path: str, story=None):
    """
    Uses the script, images, and audio in the `package_path` folder to assemble a final video.
    """
    video_assembler = va.Video_Editor()
    try:
        video_assembler.generate_video(package_path, story)
        os.rename(package_path, package_path.replace("packages", "ready"))
    except Exception as e:
        print(f"Error assembling video in {package_path}: {e}")

# ---------------------------------------------------------------------------
# Helper: Process a single script into package folders
# ---------------------------------------------------------------------------
def process_one_script(json_script_path: str, skip_video=False, subs=True):
    """
    Given one processed script JSON path, read it, create a unique package folder,
    generate images and audio for sub-stories, and optionally do video assembly.
    """
    with open(json_script_path, 'r', encoding='utf-8') as f:
        json_script = json.load(f)
    
    for story in json_script["substories"]:
        uid = str(uuid4())
        package_dir = f"data_output/packages/{uid}"
        Path(package_dir).mkdir(parents=True, exist_ok=True)

        # Copy the script
        shutil.copy(json_script_path, os.path.join(package_dir, "script.json"))
        
        # Generate images
        generate_images_for_stories(package_dir, story)
        
        # Generate TTS audio
        generate_audio_for_stories(package_dir, story)
        
        # Assemble video if not skipping
        if not skip_video:
            if subs:
                assemble_video_from_package(package_dir, story)
            else:
                assemble_video_from_package(package_dir)

# ---------------------------------------------------------------------------
# 7. Assemble videos for "ready" packages only
# ---------------------------------------------------------------------------
def assemble_ready_packages(packages_dir="data_output/packages"):
    """
    Scans packages_dir for all subfolders and assembles video if the folder contains script, images and audio.
    """
    all_packages = [os.path.join(packages_dir, p) for p in os.listdir(packages_dir)]
    all_packages = [p for p in all_packages if os.path.isdir(p)]

    for package_path in all_packages:
        if is_ready_for_video(package_path):
            print(f"Assembling video in: {package_path}")
            assemble_video_from_package(package_path)
        else:
            print(f"Skipping (not ready): {package_path}")

def is_ready_for_video(package_dir: str):
    """
    Placeholder readiness check logic.
    Checks for script.json, non-empty images and audio.
    """
    script_file = os.path.join(package_dir, "script.json")
    images_dir = os.path.join(package_dir, "images")
    audio_dir = os.path.join(package_dir, "audio")

    if not os.path.isfile(script_file):
        return False
    if not os.path.isdir(images_dir) or len(os.listdir(images_dir)) == 0:
        return False
    if not os.path.isdir(audio_dir) or len(os.listdir(audio_dir)) == 0:
        return False
    
    return True

# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def main():
    """
    Possible flags:
      -s     => only extract chapters and create script (no further processing)
      -si    => extract, create script, generate images
      -sit   => also generate TTS
      -sitv  => do everything including video assembly

    Additional flags:
      --skip-video  => skip final video assembly (if used with -sitv, it overrides the video step)
      --video-only  => only assemble videos for "ready" packages
    """
    
    epub_path = "./data_source/epdf.pub_priests-of-mars2630113e4568e40991a57be123f3e78049575.epub"
    model_name = "gpt-4o"
    args = sys.argv[1:]

    # Check for "video-only" mode
    if "--video-only" in args:
        print("Video-only mode: assembling videos for ready packages...")
        assemble_ready_packages("data_output/packages")
        return

    # Otherwise proceed with the normal pipeline
    do_scripts = any(flag in args for flag in ["-s", "-si", "-sit", "-sitv"])
    do_images = any(flag in args for flag in ["-si", "-sit", "-sitv"])
    do_tts = any(flag in args for flag in ["-sit", "-sitv"])
    do_video = "-sitv" in args
    
    # If user wants to skip video (overrides do_video)
    skip_video = "--skip-video" in args

    # 1) Extract chapters & create scripts if needed
    if do_scripts:
        chapters = extract_chapters(epub_path, model_name=model_name, display_info=True)
        create_scripts(chapters)
        if args == ["-s"]:
            print("Scripts generated. Exiting.")
            return
    
    # 2) Process scripts into JSON
    processed_script_paths = process_scripts(input_dir="data_output/scripts")
    
    # 3) For each processed script, create packages with images & audio
    #    If do_video is true AND skip_video is false => assemble videos too
    if do_images or do_tts or do_video:
        for (json_script_path, _) in processed_script_paths:
            process_one_script(json_script_path, skip_video=(skip_video or not do_video))
            # Explanation:
            #  - skip_video is True if user gave --skip-video
            #  - do_video is False if they didn't specify -sitv
            #  => so if the user never asked for video, that means skip it as well
    
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
