import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for index, voice in enumerate(voices):
    print(f"Voice {index}: {voice.name}")
    engine.setProperty('voice', voice.id)
    engine.say("Testing this voice. Do you like how it sounds?")
    engine.runAndWait()

