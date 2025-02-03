from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    # Pillow 10+ removed ANTIALIAS in favor of Resampling.LANCZOS.
    Image.ANTIALIAS = Image.Resampling.LANCZOS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

class Video_Editor():

    def __init__(self):
        self.clips = []
        self.width = 1080
        self.height = 1920
    

    def generate_video(self, path):
    
        clips = []
        image_files = [f"{path}/images/image_{i}.png" for i in range(0, 5)]
        audio_files = [f"{path}/audio/audio_{i}.mp3" for i in range(0, 5)]
    
        for img_path, aud_path in zip(image_files, audio_files):
            # Load the audio and determine its duration.
            audio = AudioFileClip(aud_path)
            duration = audio.duration
        
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
        
        # Export the final video.
        final_clip.write_videofile(f"{path}/video.mp4", fps=24)

