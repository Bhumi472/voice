from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gTTS import gTTS
import os
import urllib.request
import json

app = FastAPI()

# Enable CORS so React (running on localhost:5173 or 3000) can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model & tokenizer on startup
model_path = "./fine_tuned_model"
print("Loading fine-tuned model into FastAPI...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

class QueryRequest(BaseModel):
    question: str
    language: str = "en" # 'en', 'hi', or 'mr'

def translate_text(text, target_lang='en', source_lang='auto'):
    if target_lang == 'en' and source_lang == 'en':
        return text
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return ''.join([item[0] for item in result[0]])
    except:
        return text

@app.post("/api/chat")
def chat_endpoint(req: QueryRequest):
    user_q = req.question
    lang = req.language
    
    # Small talk fallback or translation
    clean_q = user_q.lower().strip()
    if clean_q in ["hi", "hello", "hey", "good morning"]:
        bot_response = "Hello! Welcome to our FAQ chatbot. How can I help you today?"
    else:
        # Translate to English if user typed in Hindi/Marathi
        model_input_q = translate_text(user_q, target_lang='en', source_lang=lang) if lang != 'en' else user_q
        
        # Generate answer from Flan-T5
        input_text = "Answer this FAQ question: " + model_input_q
        inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True)
        outputs = model.generate(inputs["input_ids"], max_length=128, num_beams=2, no_repeat_ngram_size=2, early_stopping=True)
        bot_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Translate final response back to Hindi/Marathi if needed
    final_response = translate_text(bot_response, target_lang=lang, source_lang='en') if lang != 'en' else bot_response
    
    # Generate audio file for voice playback
    audio_filename = "static_response.mp3"
    tld_val = 'co.in' if lang == 'en' else 'com'
    tts = gTTS(text=final_response, lang=lang, tld=tld_val, slow=False)
    tts.save(audio_filename)
    
    return {
        "response": final_response,
        "audio_url": f"http://127.0.0.1:8000/audio"
    }

from fastapi.responses import FileResponse
@app.get("/audio")
def get_audio():
    return FileResponse("static_response.mp3", media_type="audio/mp3")