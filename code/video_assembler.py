from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

image_files = [
    "data_output/packages/d8498acc-a632-4d1b-8938-2448fc4fd17c/images/image_0.png",
    "data_output/packages/d8498acc-a632-4d1b-8938-2448fc4fd17c/images/image_1.png",
    # Add more image paths here
]

audio_files = [
    "data_output/packages/d8498acc-a632-4d1b-8938-2448fc4fd17c/audio/audio_0.mp3",
    "data_output/packages/d8498acc-a632-4d1b-8938-2448fc4fd17c/audio/audio_1.mp3",
    # Add more audio paths here
]

clips = []

for img_path, aud_path in zip(image_files, audio_files):
    # Load the audio clip
    audio = AudioFileClip(aud_path)
    # Create an image clip with the duration set to the duration of the audio
    clip = ImageClip(img_path).set_duration(audio.duration)
    # Set the audio for the image clip
    clip = clip.set_audio(audio)
    # Optionally, you can add some transition effects here
    clips.append(clip)

# Concatenate all the clips together
final_clip = concatenate_videoclips(clips)

# Write the final video file
final_clip.write_videofile("video.mp4", fps=24)








