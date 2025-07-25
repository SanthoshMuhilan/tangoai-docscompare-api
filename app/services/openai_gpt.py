import os
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL_NAME_CHAT, AZURE_OPENAI_MODEL_NAME_EMBEDDING, AZURE_OPENAI_SUBSCRIPTION_KEY, AZURE_OPENAI_API_VERSION
from openai import AzureOpenAI

endpoint = AZURE_OPENAI_ENDPOINT
model_name_chat = AZURE_OPENAI_MODEL_NAME_CHAT
subscription_key = AZURE_OPENAI_SUBSCRIPTION_KEY
api_version = AZURE_OPENAI_API_VERSION
model_name_embedding = AZURE_OPENAI_MODEL_NAME_EMBEDDING

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)
# For comparing two documents
def compare_texts(text1: str, text2: str, prompt: str) -> str:
    full_prompt = f"""
    Compare the following two documents.
    Document 1:
    {text1}
    Document 2:
    {text2}
    Instructions:
    {prompt}
    """
    response = client.chat.completions.create(
    messages=[
           {"role": "system", "content": "You are an AI that compares two documents."},
           {"role": "user", "content": full_prompt}
       ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=model_name_chat
    )
    return response.choices[0].message.content.strip()

def analyze_single_text(text: str, prompt: str) -> str:
    full_prompt = f"""
    Document 1:
    {text1}
    Instructions:
    {prompt}
    """
    response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are an AI assistant that processes and analyzes documents."},
        {"role": "user", "content": full_prompt}
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=model_name_chat
    )
    return response.choices[0].message.content

def create_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=[text],       
        model=model_name_embedding      
    )
    return response.data[0].embedding