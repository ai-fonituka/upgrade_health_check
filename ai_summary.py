from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
import difflib
import os

USE_AI = os.getenv("USE_AI", "false").lower() == "true"

if USE_AI:
    from langchain_ollama import ChatOllama
    from langchain.schema import SystemMessage, HumanMessage
    llm = ChatOllama(model="mistral", temperature=0.2)

def summarize_changes(name, diffs):
    prompt = (
        f"Summarize only the meaningful modifications made to the record '{name}'. "
        "Focus especially on code fields by describing only what was changed.\n"
    )
    for field, values in diffs.items():
        before_lines = values['before'].splitlines()
        after_lines = values['after'].splitlines()
        diff = difflib.unified_diff(before_lines, after_lines, fromfile='before', tofile='after', lineterm='')
        diff_text = '\n'.join(diff)
        prompt += f"\n[{field.upper()}] DIFF:\n{diff_text}\n"
    messages = [
        SystemMessage(content="You are a ServiceNow expert. Focus on describing only the modified parts of each field, especially large code blocks."),
        HumanMessage(content=prompt)
    ]

    if not USE_AI:
        return "🧠 AI summary disabled in cloud environment."
    response = llm(messages)
    return response.content
