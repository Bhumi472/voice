import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


model_path = "./fine_tuned_model"
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
    
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

if __name__ == "__main__":
    print("=" * 50)
    print("FAQ Chatbot Initialized (Type 'exit' to quit)")
    print("=" * 50)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
            
        bot_response = generate_answer(user_input)
        print(f"Bot: {bot_response}")