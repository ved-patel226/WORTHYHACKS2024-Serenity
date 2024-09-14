import google.generativeai as genai
from langchain_groq import ChatGroq



class GenAi:
    def __init__(self):
        genai.configure(api_key="AIzaSyBjfK1cC6okqitG07TfOn5jHdjH1n4_Ctc")

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 2048,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        self.chat_session = model.start_chat(history=[])

    def send_message(self, message: str) -> str:
        response = self.chat_session.send_message(message)
        return response.text

class groq:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=8000,
            groq_api_key = "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"
        )
        
    def send_message(self, messages):
        messages = [
        (
            "system",
            "",
        ),
        ("human", messages),
        ]
        
        ai_msg = self.llm.invoke(messages)
        
        return ai_msg.content

if __name__ == "__main__":
    ai = groq()
    print(ai.send_msg("test", "I am good, how are you?"))