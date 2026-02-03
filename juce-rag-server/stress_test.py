import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. The "Trap" Question
# We act naive and ask for a buffer, tempting it to use a dynamic vector.
stress_prompt = """
Write a C++ class named 'SimpleDelay' using JUCE. 
It must have a 'pushSample' method to add new audio to the buffer.
Show me how to use this inside 'processBlock'.
"""

def retrieve_docs(query):
    # Retrieve context from your local RAG server
    try:
        resp = requests.post("http://localhost:8000/search", json={"query": query, "k": 5})
        if resp.status_code == 200:
            results = resp.json()["results"]
            return "\n".join([f"--- DOCS ---\n{r['content']}" for r in results])
    except:
        return ""
    return ""

def run_stress_test():
    print(f"🔥 Running Stress Test: '{stress_prompt.strip()}'")
    
    # 2. Get the Context
    context = retrieve_docs("AudioBuffer circular buffer delay implementation")
    
    # 3. The STRICT System Prompt
    system_prompt = f"""
    You are an expert C++ Audio Developer specializing in the JUCE framework.
    
    CRITICAL RULES FOR REAL-TIME AUDIO:
    1. **ZERO ALLOCATIONS:** Never use 'new', 'malloc', or container resizing (push_back, resize) inside the audio callback (processBlock, pushSample).
    2. **PRE-ALLOCATION:** All memory must be allocated in 'prepareToPlay' or the constructor.
    3. **CONTEXT:** Use the provided JUCE documentation strictly.
    
    DOCUMENTATION CONTEXT:
    {context}
    """

    # 4. Generate
    print("🤖 Generating compliant code...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": stress_prompt}
        ],
        temperature=0.1
    )
    
    print("\n" + "="*40)
    print(response.choices[0].message.content)
    print("="*40)

if __name__ == "__main__":
    run_stress_test()