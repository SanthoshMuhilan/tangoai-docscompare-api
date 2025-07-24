import openai

openai.api_type = "azure"
openai.api_base = "<your_openai_endpoint>"
openai.api_key = "<your_openai_key>"

def test_openai():
    response = openai.Completion.create(
        engine="gpt-4",
        prompt="Hello, how can I assist you?",
        max_tokens=50
    )
    print(response.choices[0].text.strip())

if __name__ == "__main__":
    test_openai()