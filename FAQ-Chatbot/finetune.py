
import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)

MODEL_NAME = "google/flan-t5-small"

# Load FAQ dataset
with open("faq.json", "r", encoding="utf-8") as f:
    faq = json.load(f)

dataset = Dataset.from_list(faq)

# Load pretrained model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Prepare training data
def preprocess(example):
    inputs = tokenizer(
        "Answer this FAQ question: " + example["question"],
        max_length=128,
        truncation=True
    )

    labels = tokenizer(
        text_target=example["answer"],
        max_length=128,
        truncation=True
    )

    inputs["labels"] = labels["input_ids"]
    return inputs

tokenized_dataset = dataset.map(
    preprocess,
    remove_columns=dataset.column_names
)

# Configure training
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=10,
    per_device_train_batch_size=2,
    learning_rate=5e-5,
    logging_steps=1,
    save_strategy="no",
    report_to="none",
    use_cpu=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model
    )
)

print("Starting actual model fine-tuning...")
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

print("Fine-tuning completed!")
print("Model saved in ./fine_tuned_model")
