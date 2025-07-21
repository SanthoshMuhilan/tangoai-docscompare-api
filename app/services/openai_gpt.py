import openai

# Azure OpenAI Config
openai.api_type = "azure"
openai.api_base = "https://codeblackgenaigenerator.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "b2fd66194c56425ca3282391aeb3702f"
# For comparing two documents
def compare_texts(text1: str, text2: str, prompt: str) -> str:
    response = openai.ChatCompletion.create(
       engine="gpt-4",  # Replace with your Azure OpenAI deployment name
       messages=[
           {"role": "system", "content": "You are an AI that compares two documents."},
           {"role": "user", "content": combined_prompt}
       ],
       temperature=0.2,
       max_tokens=2500
   )
return response['choices'][0]['message']['content']


def analyze_single_text(text: str, prompt: str) -> str:
    response = openai.ChatCompletion.create(
       engine="gpt-4",  # Replace with your Azure OpenAI deployment name
       messages=[
           {"role": "system", "content": "You are an AI assistant that processes and analyzes documents."},
           {"role": "user", "content": combined_prompt}
       ],
       temperature=0.2,
       max_tokens=2000
    )
    return response['choices'][0]['message']['content']