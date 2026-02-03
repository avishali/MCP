import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # Ensure OPENAI_API_KEY is in your .env

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def retrieve_docs(query, k=5):
    """Asks your local RAG server for context"""
    try:
        resp = requests.post(
            "http://localhost:8000/search",
            json={"query": query, "k": k}
        )
        if resp.status_code == 200:
            results = resp.json()["results"]
            # Format the context for the LLM
            context_text = "\n\n".join([
                f"--- DOCUMENTATION SEGMENT ---\n{r['content']}" 
                for r in results
            ])
            return context_text
    except Exception as e:
        print(f"RAG Connection Error: {e}")
    return ""

def generate_code(user_query):
    # 1. Get the Context
    print(f"🔍 Searching docs for: '{user_query}'...")
    context = retrieve_docs(user_query)
    
    if not context:
        print("⚠️ Warning: No documentation found. LLM might hallucinate.")

    system_prompt = f"""   
    You are an expert C++ Audio Developer specializing in the JUCE framework.
    Your goal is to write production-ready, real-time safe C++ code using the provided context.

    ### CRITICAL INSTRUCTION: STRICT CONTEXT ADHERENCE
    You must ONLY use classes, functions, and method signatures found in the "DOCUMENTATION CONTEXT" provided below.
    - If a function is not in the context, DO NOT assume it exists.
    - DO NOT use deprecated classes (e.g., ScopedPointer, AudioProcessorGraph::Node).
    - If the context is insufficient to answer the request, state exactly what is missing rather than inventing code.

    ### CODING STANDARDS (Real-Time Audio)
    1. **No Allocations in ProcessBlock:** Never use `new`, `malloc`, or standard library containers that resize (std::vector, std::string) inside `processBlock`.
    2. **Modern C++:** Use C++17/20 standards (e.g., `auto`, `if constexpr`, `std::unique_ptr`).
    3. **Safety:** Always use `jassert` to check for null pointers or invalid buffer sizes.
    4. **Member Layout:** Follow standard JUCE layout:
    - Header: `private` members at the bottom, `public` methods at top.
    - Separate `.h` and `.cpp` logic unless writing a template.
    ...
    DOCUMENTATION CONTEXT (Immutable Truth):
    {context}
    """

    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": system_prompt}, 
            # Note: We don't need to pass context again if it's in system, 
            # but keeping the user query separate helps the model focus.
            {"role": "user", "content": user_query}
        ],
        temperature=0.1 # Lower temp = Less creativity, More strictness
    )
    
# --- TEST THE AGENT ---
if __name__ == "__main__":
    prompt = "Write a C++ function that takes a juce::AudioBuffer<float> and applies a simple gain volume of 0.5 to all samples."
    code = generate_code(prompt)
    print("\n" + "="*40)
    print(code)
    print("="*40)
    
    