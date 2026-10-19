import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import speech_recognition as sr
from gtts import gTTS
import os
import platform
import pygame
from googletrans import Translator

pygame.mixer.init()
translator = Translator()

model_path = "./fine_tuned_model"
print("Loading fine-tuned model...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

def generate_answer(question):
    input_text = "Answer this FAQ question: " + question
    inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True)
    
    outputs = model.generate(
        inputs["input_ids"],
        max_length=128,
        num_beams=2,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def speak(text, lang_choice='en'):
    if lang_choice in ['hi', 'mr']:
        try:
            translated = translator.translate(text, dest=lang_choice)
            if translated and translated.text:
                text = translated.text
        except Exception as e:
            print(f"Translation notice: Using fallback text due to network limit ({e})")
            
        tts = gTTS(text=text, lang=lang_choice, slow=False)
    else:
        tts = gTTS(text=text, lang='en', tld='co.in', slow=False)

    print(f"Bot (Voice): {text}")
    
    audio_file = "response.mp3"
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except Exception:
        pass
    
    tts.save(audio_file)
    
    try:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Audio playback error: {e}")

def listen(lang_code='en-IN'):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening... (Speak now, or press Enter to type instead)")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=4, phrase_time_limit=6)
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out. Switching to text input.")
            return input("You (Type your question): ")
            
    try:
        query = r.recognize_google(audio, language=lang_code)
        print(f"You (Recognized Voice): {query}")
        return query
    except (sr.UnknownValueError, sr.RequestError):
        print("⚠️ Could not clearly capture audio. Type your question below:")
        return input("You (Type your question): ")

if __name__ == "__main__":
    print("=" * 60)
    print("Select Language / Voice Output:")
    print("1. Indian English Accent (en)")
    print("2. Hindi (hi)")
    print("3. Marathi (mr)")
    print("=" * 60)
    
    choice = input("Enter choice (1, 2, 3 or type english/hindi/marathi): ").strip().lower()
    
    if choice in ['2', 'hindi', 'hi']:
        selected_lang = 'hi'
        speech_lang_code = 'hi-IN'
        print("-> Hindi mode selected.")
    elif choice in ['3', 'marathi', 'mr']:
        selected_lang = 'mr'
        speech_lang_code = 'mr-IN'
        print("-> Marathi mode selected.")
    else:
        selected_lang = 'en'
        speech_lang_code = 'en-IN'
        print("-> Indian English mode selected.")

    print("=" * 60)
    print("Voice FAQ Chatbot Active! Say or type 'exit' to stop.")
    print("=" * 60)
    
    while True:
        user_query = listen(speech_lang_code)
        
        if not user_query or not user_query.strip():
            continue
            
        if user_query.lower() in ["exit", "quit"]:
            speak("Goodbye!", lang_choice=selected_lang)
            break
            
        if selected_lang in ['hi', 'mr']:
            try:
                translated_query = translator.translate(user_query, dest='en').text
                print(f"Translated query for model: {translated_query}")
                bot_response = generate_answer(translated_query)
            except:
                bot_response = generate_answer(user_query)
        else:
            bot_response = generate_answer(user_query)
        
        speak(bot_response, lang_choice=selected_lang)