import os
from gtts import gTTS

def generate_voice_commands():
    # Audio folder in frontend
    audio_dir = "/home/jack/Documents/projects/ballers085/frontend/public/audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    commands = {
        "drible": "Drible",
        "pernada": "Pernada",
        "raquetada": "Raquetada",
        "hesitacao": "Hesitação"
    }
    
    print("Generating TTS voice command files...")
    for filename, text in commands.items():
        filepath = os.path.join(audio_dir, f"{filename}.mp3")
        print(f"Generating: {text} -> {filepath}")
        
        # Generate audio using Google Text-to-Speech in Brazilian Portuguese
        tts = gTTS(text=text, lang="pt", tld="com.br")
        tts.save(filepath)
        
    print("All voice commands generated successfully!")

if __name__ == "__main__":
    generate_voice_commands()
