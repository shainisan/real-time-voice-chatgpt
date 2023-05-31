import os
import speech_recognition as sr
from google.cloud import speech
from google.cloud import translate_v2 as translate
import openai
from gtts import gTTS
import html
from colorama import Fore, Style
from termcolor import cprint
from art import *

# Set environment variables
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r""
openai.api_key  = ''

# Initialize speech recognition engine
r = sr.Recognizer()

def clean_text(text):
    cleaned_text = html.unescape(text)
    return cleaned_text

def transcribe_and_translate_audio(audio_content):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="he-IL",  # Language code for Hebrew
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print_color("\nTranscript: ", Fore.GREEN)
        cprint(f"{result.alternatives[0].transcript}", 'white')
        
        translated_text = translate_text(result.alternatives[0].transcript)
        print_color("\nTranslated text: ", Fore.GREEN)
        cprint(f"{translated_text}", 'white')
        
        chatbot_response = chat_with_gpt(translated_text)
        print_color("\nChatbot response: ", Fore.GREEN)
        cprint(f"{chatbot_response}", 'white')
        
        translated_response = translate_text(chatbot_response, target_language="he")
        cleaned_translated_response = clean_text(translated_response)
        print_color("\nTranslated response: ", Fore.GREEN)
        cprint(f"{cleaned_translated_response}", 'white')
        
        text_to_speech(cleaned_translated_response)

def translate_text(text, target_language="en"):
    translate_client = translate.Client()

    result = translate_client.translate(
        text, target_language=target_language)

    return result['translatedText']

def chat_with_gpt(message):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",  # Make sure to use the model you have access to
      messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )
    return response['choices'][0]['message']['content']

from google.cloud import texttospeech

def text_to_speech(text):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="he-IL", 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, 
        voice=voice, 
        audio_config=audio_config
    )

    # Save the speech audio into a file
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    # Play the audio file
    os.system("ffplay -nodisp -autoexit output.mp3 >nul 2>&1")

# Print text in color
def print_color(text, color):
    print(color + text + Style.RESET_ALL)

# Loop to listen for audio input
while True:
    # Listen for input
    with sr.Microphone() as source:
        cprint("\nSpeak now:", 'yellow')
        audio = r.listen(source)

    # Try to recognize the audio
    try:
        print_color("\nTranscribing and translating audio...", Fore.CYAN)
        transcribe_and_translate_audio(audio.get_wav_data())
        cprint("\n--------------------------------------", 'blue')

    # Catch if recognition fails
    except:
        response_text = "Sorry, I didn't get that!"
        cprint(response_text, 'red')
        text_to_speech(response_text)
        cprint("\n--------------------------------------", 'blue')
