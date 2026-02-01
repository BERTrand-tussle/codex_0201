import os
import re
from openai import OpenAI
from datetime import datetime

# 1. Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_DIR = "research_outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def slugify(text):
    """Converts topic into a filename-friendly string."""
    return re.sub(r'[^\w\-]', '_', text)[:30]

def deep_research_v4(topic):
    traces = []
    print(f"\n--- 🚀 Starting Multi-Agent Research: {topic} ---")
    
    # --- STEP 1: PLANNER ---
    traces.append("### [SYSTEM] Handoff to PLANNER_AGENT")
    planner_prompt = f"Break down the topic '{topic}' into 3 specific research questions."
    
    plan_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": planner_prompt}]
    )
    plan = plan_response.choices[0].message.content
    traces.append(f"**PLANNER_AGENT Decision:** Created strategy.\n\n**Plan:**\n{plan}")

    # --- STEP 2: RESEARCHER ---
    traces.append("\n### [SYSTEM] Handoff to RESEARCHER_AGENT")
    researcher_prompt = f"Provide a detailed report based on this plan:\n{plan}"
    
    report_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": researcher_prompt}]
    )
    initial_report = report_response.choices[0].message.content
    traces.append("**RESEARCHER_AGENT Decision:** Generated initial content.")

    # --- STEP 3: VERIFIER (PHASE 3) ---
    traces.append("\n### [SYSTEM] Handoff to VERIFIER_AGENT")
    verifier_prompt = f"Review this research report for clarity and potential gaps. Provide a brief critique:\n\n{initial_report}"
    
    verifier_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": verifier_prompt}]
    )
    critique = verifier_response.choices[0].message.content
    traces.append(f"**VERIFIER_AGENT Critique:**\n{critique}")
    print("✅ Verification complete.")

    # --- STEP 4: NAMING & SAVING ---
    # New Format: Timestamp_Topic_Date.md
    time_str = datetime.now().strftime("%H%M")     # e.g., 1430
    date_str = datetime.now().strftime("%Y-%m-%d") # e.g., 2026-02-01
    clean_topic = slugify(topic)                   # e.g., AI_Impact
    
    filename = f"{OUTPUT_DIR}/{time_str}_{clean_topic}_{date_str}.md"
    
    with open(filename, "w") as f:
        f.write(f"# Deep Research Report: {topic}\n\n")
        f.write("## 1. Multi-Agent Coordination Traces\n")
        for trace in traces:
            f.write(f"{trace}\n\n")
        f.write("----- \n")
        f.write("## 2. Final Research Output\n")
        f.write(initial_report)
    
    return filename

if __name__ == "__main__":
    query = input("What do you want to research? ")
    file_path = deep_research_v4(query)
    print(f"\n--- ✨ DONE! ✨ ---")
    print(f"File Saved: {file_path}")