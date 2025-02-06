import time
from groq import Groq

def generate_answer(prompt, api_key, model_name="llama3-70b-8192", max_tokens=8000, temperature=0, top_p=1):
    client = Groq(api_key=api_key)  # Use the API key passed as an argument
    time.sleep(5)
    try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True,
                stop=None,
            )
            
            summary = ""
            for chunk in completion:
                summary += chunk.choices[0].delta.content or ""
                
            return summary
    except:
            try:
                time.sleep(15)
                completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True,
                stop=None,
            )
            
                summary = ""
                for chunk in completion:
                    summary += chunk.choices[0].delta.content or ""
                    
                return summary
            except Exception as e :
                return e