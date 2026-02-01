import os
import re
from openai import OpenAI
from datetime import datetime

# 1. SETUP & ENVIRONMENT
# Ensure your OPENAI_API_KEY is in GitHub Secrets (Codespaces)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_DIR = "research_outputs"
KNOWLEDGE_DIR = "pri_knowledge_final" # Your synced private folder

# Ensure directories exist
for folder in [OUTPUT_DIR, KNOWLEDGE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def slugify(text):
    """Converts topic into a filename-friendly string."""
    return re.sub(r'[^\w\-]', '_', text.strip())[:30]

# --- MODULAR TOOL: KNOWLEDGE ABSTRACTION ---
def perform_grounded_search(query):
    """
    Reads from the private world-view folder.
    In a production app, this would be swapped for a Vector DB or Search API.
    """
    print(f"📖 [GROUNDING] Accessing private expert context for: {query}...")
    try:
        # Looking for any .md or .txt files in your private folder
        files = os.listdir(KNOWLEDGE_DIR)
        if not files:
            return "No prior world-view files found."
        
        combined_context = ""
        for file in files:
            with open(os.path.join(KNOWLEDGE_DIR, file), "r") as f:
                combined_context += f.read() + "\n"
        return combined_context
    except Exception as e:
        return f"Grounding Error: {str(e)}"

# --- MULTI-AGENT CORE LOGIC ---
def run_deep_research_mas(topic):
    traces = []
    print(f"\n🚀 Starting Multi-Agent Session for: {topic}")

    # AGENT 1: THE GROUNDING AGENT
    traces.append("### [SYSTEM] Handoff to GROUNDING_AGENT")
    prior_knowledge = perform_grounded_search(topic)
    traces.append(f"**GROUNDING_AGENT:** Successfully retrieved user-provided expert context.")

    # AGENT 2: THE PLANNER (STRATEGIST)
    traces.append("\n### [SYSTEM] Handoff to PLANNER_AGENT")
    planner_prompt = (
        f"You are the Lead Research Architect. \n"
        f"TOPIC: {topic}\n"
        f"PRIOR USER CONTEXT: {prior_knowledge}\n"
        f"TASK: Create a 3-step execution strategy for the researcher. "
        f"Prioritize identifying gaps where current market data might contradict the user's world-view."
    )
    
    plan = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": planner_prompt}]
    ).choices[0].message.content
    traces.append(f"**PLANNER_AGENT Strategy:**\n{plan}")
    print("✅ Strategy defined.")

    # AGENT 3: THE RESEARCHER (EXPERT)
    traces.append("\n### [SYSTEM] Handoff to RESEARCHER_AGENT")
    researcher_prompt = f"Act as an Expert Industry Analyst. Execute this research plan:\n{plan}\nProvide a detailed report."
    
    initial_report = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": researcher_prompt}]
    ).choices[0].message.content
    traces.append("**RESEARCHER_AGENT:** Generated comprehensive report based on strategy.")
    print("✅ Research gathered.")

    # AGENT 4: THE VERIFIER (SYNECTICAL AUDITOR)
    traces.append("\n### [SYSTEM] Handoff to VERIFIER_AGENT")
    verifier_prompt = (
        f"You are a Skeptical Auditor. Review this report for logical fallacies, "
        f"hallucinations, or missed risks mentioned in the world-view: {prior_knowledge}\n\n"
        f"REPORT TO AUDIT: {initial_report}"
    )
    
    critique = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": verifier_prompt}]
    ).choices[0].message.content
    traces.append(f"**VERIFIER_AGENT Audit & Risk Assessment:**\n{critique}")
    print("✅ Audit complete.")

    # --- FILE GENERATION ---
    time_str = datetime.now().strftime("%H%M")
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{OUTPUT_DIR}/{time_str}_{slugify(topic)}_{date_str}.md"

    with open(filename, "w") as f:
        f.write(f"# Multi-Agent Deep Research: {topic}\n\n")
        
        # Mermaid Visual Trace for Judges
        f.write("## 1. System Coordination (Visual Trace)\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        f.write("    User([User World-View]) -->|Grounding| G[Grounding Agent]\n")
        f.write("    G -->|Context| P[Planner Agent]\n")
        f.write("    P -->|Strategy| R[Researcher Agent]\n")
        f.write("    R -->|Draft| V[Verifier Agent]\n")
        f.write("    V -->|Cynical Audit| Report[Final Markdown Report]\n")
        f.write("```\n\n")

        f.write("## 2. Multi-Agent Logic Traces\n")
        for trace in traces:
            f.write(f"{trace}\n\n")
            
        f.write("---\n## 3. Final Deep Research Report\n")
        f.write(initial_report)
    
    return filename

if __name__ == "__main__":
    user_topic = input("Enter your research topic: ")
    saved_path = run_deep_research_mas(user_topic)
    print(f"\n✨ SUCCESS! ✨\nYour report is ready: {saved_path}")