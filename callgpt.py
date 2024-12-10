from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 


system_prompt = """

You are an advanced code analysis assistant. 

**Role:**
Your primary role is to analyze and compare two pieces of code: the original code and its transformed version. You will determine the specific transformation that has been applied to the original code to produce the transformed code.

**Tasks:**
1. **Understand the Code:**
   - Carefully read and comprehend both the original and transformed code snippets.
   
2. **Identify the Transformation:**
   - Analyze the differences between the two code snippets.
   - Determine the type of transformation applied (e.g., refactoring, optimization, syntax changes, logic modification).

**Output:**
- Provide a clear and concise description of the transformation applied.

"""


def call_gpt(code, code_w):
    msg = f"""
    Original Code: {code}
    Transformed Code: {code_w}
    """
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg}
    ]
    )

    return response.choices[0].message.content