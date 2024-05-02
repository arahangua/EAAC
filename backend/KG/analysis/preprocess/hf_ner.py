import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer
from torch.nn.functional import softmax

def load_model_and_tokenizer(model_name="dslim/bert-base-NER"):
    # Load the pre-trained model and tokenizer
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

def predict_ner(text, model, tokenizer):
    # Encode the text and create a tensor
    inputs = tokenizer.encode_plus(text, return_tensors="pt")
    
    # Predict the entities
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Process the prediction results
    predictions = softmax(outputs.logits, dim=-1)
    entities = predictions.argmax(dim=-1)[0]

    # Extract and print the detected entities along with their labels
    results = []
    tokens = inputs.tokens()
    for token, prediction in zip(tokens, entities):
        entity = model.config.id2label[prediction.item()]
        if entity != 'O':  # Only consider non-'O' labels
            results.append((token, entity))
    return results

def main():
    text = "The capital of France, Paris, is known for its art, culture, and gastronomy."
    model, tokenizer = load_model_and_tokenizer()
    results = predict_ner(text, model, tokenizer)
    for token, entity in results:
        print(f"{token}: {entity}")

if __name__ == "__main__":
    main()
