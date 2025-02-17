from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    # Pillow 10+ removed ANTIALIAS in favor of Resampling.LANCZOS.
    Image.ANTIALIAS = Image.Resampling.LANCZOS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import json
import sys
from math import ceil

class Video_Editor():

    def __init__(self):
        self.clips = []
        self.width = 1080
        self.height = 1920
    
    def add_captions(self, video, subs):
        generator = lambda txt: TextClip(txt, font='Arial', fontsize=70, color='white')
        subtitles = SubtitlesClip(subs, generator)
        
        result = CompositeVideoClip([video, subtitles.set_pos(('center','center'))])
        return result 

    def generate_video(self, path, story=None):


        clips = []
        durations = []
        image_files = [f"{path}/images/image_{i}.png" for i in range(0, 5)]
        audio_files = [f"{path}/audio/audio_{i}.mp3" for i in range(0, 5)]
    
        for img_path, aud_path in zip(image_files, audio_files):
            # Load the audio and determine its duration.
            audio = AudioFileClip(aud_path)
            duration = audio.duration
            durations.append(duration)
        
            # Create an ImageClip with the duration of the audio.
            clip = ImageClip(img_path).set_duration(duration)
            clip = clip.set_audio(audio)
        
            # Resize the image so its height fills the vertical frame.
            clip = clip.resize(height=self.height)
        
            if clip.w > self.width:
                # If the image is wider than the target width, we want to pan across it.
                max_shift = clip.w - self.width
        
                # Define a function that dynamically crops the frame based on time.
                def crop_func(get_frame, t):
                    frame = get_frame(t)
                    # Calculate how far to shift horizontally at time t.
                    current_x = int(max_shift * t / duration)
                    # Crop the frame: use the full height and a width of FINAL_WIDTH.
                    return frame[0:self.height, current_x:current_x+self.width]
        
                # Apply our dynamic crop function to the clip.
                clip = clip.fl(crop_func, apply_to=['mask'])
            else:
                # If the image is narrower than FINAL_WIDTH, center it on a background.
                clip = clip.on_color(size=(self.width, self.height),
                                     color=(0, 0, 0),  # black background; change as desired
                                     pos='center')
            clips.append(clip)
        
        # Concatenate all the clips into one final video.
        final_clip = concatenate_videoclips(clips)

        if story is not None:
            subtitles = self.prepare_subs(story['lines'], durations)
            final_clip = self.add_captions(final_clip, subtitles)
        
        # Export the final video.
        final_clip.write_videofile(f"{path}/video.mp4", fps=24)


    def prepare_subs(self, lines, durations):
       subs = []
       for i, lines in enumerate(lines):

           amount_lines = 1
           char_per_lines = 30
           if len(lines) > 0:
               amount_lines = ceil(len(lines)/char_per_lines) 

           if amount_lines > 1:
                new_duration_start = sum(durations[:i])
                new_duration_step = (sum(durations[:i+1]) - new_duration_start) /amount_lines 
                for i in range(amount_lines):
                    subs.append(((new_duration_start, new_duration_start+new_duration_step), lines[i*char_per_lines:(i+1)*char_per_lines]))
                    new_duration_start += new_duration_step
                continue

           subs.append(((sum(durations[:i]), sum(durations[:i+1])), lines))
       return subs

    
    
    
    def format_sub_per_line(self, line, amount_lines, char_per_lines, new_duration_start, new_duration_step):
        """
        Splits a string into subtitle lines without cutting words in half.
        - If the first word is incomplete, it is discarded (as it was part of the previous subtitle line).
        - If the last word is incomplete, it is expanded to the full word from the original text.
        - A newline character is added if the last word was cut off.
        """
        subs = []
        words = line.split()  # Split line into whole words
        word_index = 0        # Tracks our position in 'words'
    
        for i in range(amount_lines):
            start_idx = i * char_per_lines
            end_idx = (i + 1) * char_per_lines
            
            if start_idx >= len(line):
                break  # No more text to process
            
            line_range = line[start_idx:end_idx]
    
            # 1) Check if the first word in this chunk is incomplete
            range_words = line_range.split()
            if word_index < len(words) and range_words:
                # Compare first chunked word to what we expect from 'words'
                if words[word_index] != range_words[0]:
                    # It's truncated; remove that partial word from the chunk
                    line_range = line_range.split(None, 1)[-1]
    
            # Re-split after possibly dropping the first partial
            range_words = line_range.split()
    
            # 2) Update how many whole words we've used up
            word_index += len(range_words)
    
            # 3) Check if the last word is truncated
            if word_index < len(words) and range_words:
                if words[word_index] != range_words[-1]:
                    # We found a partial last word
                    line_parts = line_range.rsplit(None, 1)  # Remove it from the end
                    if len(line_parts) > 1:
                        line_range = line_parts[0] + f" {words[word_index]}\n"
                    # REMOVED EXTRA word_index += 1
    
            # 4) Add the line with its timestamps
            subs.append(((new_duration_start, new_duration_start + new_duration_step), line_range))
            new_duration_start += new_duration_step
    
        return subs





if sys.argv[1] == "-test":

    test_editor = Video_Editor()
    with open("data_output/packages/ec8425b2-3b98-4a00-83a8-ba0469aac8d5/script.json", 'r', encoding='utf-8') as f:
        json_script = json.load(f)

    test_editor.generate_video("data_output/packages/ec8425b2-3b98-4a00-83a8-ba0469aac8d5", json_script["substories"][0])

