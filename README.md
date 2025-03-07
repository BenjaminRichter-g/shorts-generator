# shorts-generator
Creates a pipeline to automatically generate short form content of choice

Ideally, when given a piece of content such as a book transforms it into short form content for tiktok or youtube shorts.
Steps would be:

1. Provide text
2. Extract sub-stories
3. Generate script for short story
4. Generate prompts based on script
5. Generate images from prompts
6. Generate voice with tts from script
7. Generate video with images and voice

usage will evolve over time

To run the code follow the following steps:

1. Create venv and activate it

```
python3 -m venv shorts_venv
source shorts_venv/bin/activate
```
2. Install requirements
```
pip install -r requirements.txt
```
3. Put content into data_source (for now epubs)
4. To run script you have the following options:
Generate everything from extracting story, creating substories, generate and edit video
```
python3 content_pipeline.py
```
Or you have the following options:
-s to extract and create stories
-i to create images
-t to create audio 
-v to edit the videos

these can be called in any order such as 
```
python3 content_pipeline.py -i -t -v
```
which will consume all created to stories to create images, audio and edit the videos


