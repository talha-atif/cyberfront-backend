# Code optimization by ensuring models are loaded only once if possible
import os
import fitz  # PyMuPDF
import sys
import json
from transformers import pipeline, DistilBertTokenizer, DistilBertForQuestionAnswering

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page in document:
        text += page.get_text("text")  # Specify the output format directly
    document.close()
    return text

def load_qa_pipeline(model_path="distilbert_qa4", tokenizer_path="distilbert_qa_tokenizer4", max_length=512):
    tokenizer = DistilBertTokenizer.from_pretrained(model_path if os.path.exists(model_path) else "distilbert-base-uncased-distilled-squad", model_max_length=max_length)
    model = DistilBertForQuestionAnswering.from_pretrained(model_path if os.path.exists(model_path) else "distilbert-base-uncased-distilled-squad")
    return pipeline("question-answering", model=model, tokenizer=tokenizer)

def get_answer(question, context, qa_pipeline):
    result = qa_pipeline(question=question, context=context)
    return result['answer']

if __name__ == '__main__':

    question = sys.argv[1]

    # current working directory
    cwd = os.getcwd()
    pdf_path = os.path.join(cwd, "Chatbot/optimizedLogs.pdf")

    pdf_text = extract_text_from_pdf(pdf_path)
    qa_pipeline = load_qa_pipeline(max_length=1024)  # Load once and use many times

    answer = get_answer(question, pdf_text, qa_pipeline)
    print(json.dumps({"answer": answer, "question": question}))
