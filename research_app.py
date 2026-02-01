import os
import re
import asyncio
from openai import OpenAI
from datetime import datetime

# 1. SETUP
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OUTPUT_DIR = "research_outputs"
KNOWLEDGE_DIR = "pri_knowledge_final"

for folder in [OUTPUT_DIR, KNOWLEDGE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

def slugify(text): return re.sub(r'[^\w\-]', '_', text.strip())[:30]

# --- MODULAR TOOL: GROUNDING ---
def get_world_view():
    try:
        files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(('.txt', '.md'))]
        return "\n".join([open(os.path.join(KNOWLEDGE_DIR, f), "r").read() for f in files])
    except: return "No prior context."

# --- DYNAMIC AGENT ENGINE ---
def call_agent(role, prompt, model="gpt-4o"):
    print(f"📡 [HANDOFF] {role} is processing...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": f"You are a {role}."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def run_advanced_session():
    # INPUTS
    topic = input("Research Topic: ")
    reasoning_pct = int(input("Reasoning Required (0-100): "))
    depth_pct = int(input("Depth/Validation Required (0-100): "))
    
    session_id = datetime.now().strftime("%H%M")
    session_folder = f"{OUTPUT_DIR}/session_{session_id}_{slugify(topic)}"
    os.makedirs(session_folder, exist_ok=True)
    
    # 1. ORCHESTRATION LOG
    orchestration_steps = []
    
    # 2. MODELS
    # Logic: High reasoning uses flagship model; low uses mini to save credits.
    main_model = "gpt-4o" if reasoning_pct > 60 else "gpt-4o-mini"
    
    # --- STEP 1: GROUNDING ---
    context = get_world_view()
    orchestration_steps.append(["1", "Ingested expert world-view; preparing strategy.", "🧠 Planner"])
    
    # --- STEP 2: PLANNING ---
    planner_prompt = f"Topic: {topic}\nContext: {context}\nCreate a strategy with {depth_pct}% depth focus."
    plan = call_agent("Lead Architect", planner_prompt, main_model)
    orchestration_steps.append(["2", "Strategic plan defined; optimized for technical trade-offs.", "🔍 Researcher"])
    
    # --- STEP 3: RESEARCH (WITH SELF-CORRECTION LOOP) ---
    research_prompt = f"Execute this plan:\n{plan}"
    report = call_agent("Expert Researcher", research_prompt, "gpt-4o") # Always use 4o for data
    
    # LOOP: SELF-CORRECTION (Criteria 3 & 5)
    if depth_pct > 70:
        orchestration_steps.append(["3", "Initial draft ready; triggering self-correction loop.", "⚖️ Verifier"])
        verifier_prompt = f"Audit this report for gaps against the world-view:\n{report}"
        critique = call_agent("Cynical Auditor", verifier_prompt, main_model)
        
        if "FAIL" in critique.upper() or "GAP" in critique.upper():
            orchestration_steps.append(["4", "Audit failed; Researcher performing one-time revision.", "🔍 Researcher"])
            report = call_agent("Expert Researcher", f"Refine this report based on this audit: {critique}", "gpt-4o")
            orchestration_steps.append(["5", "Revision complete; final report polished.", "🏁 Finish"])
        else:
            orchestration_steps.append(["4", "Audit passed; report verified.", "🏁 Finish"])
    else:
        orchestration_steps.append(["3", "Research complete; direct output generated.", "🏁 Finish"])

    # --- FINAL ARTIFACT ---
    filename = f"{session_folder}/FINAL_REPORT.md"
    with open(filename, "w") as f:
        f.write(f"# 🔬 Advanced Research: {topic}\n\n")
        
        # 3-COLUMN ORCHESTRATION TABLE
        f.write("## 🏗️ Dynamic Orchestration Logic\n")
        f.write("| Step | Reason for Handoff | Next Agent |\n| :--- | :--- | :--- |\n")
        for step in orchestration_steps:
            f.write(f"| {step[0]} | {step[1]} | {step[2]} |\n")
        
        f.write("\n## 📜 Final Research Output\n")
        f.write(report)
        
        # DOUBTS GENERATOR
        f.write("\n---\n## 🕵️ Unresolved Doubts & Expert Handoffs\n")
        f.write("> These are questions the AI identified as needing human-expert intervention.\n\n")
        doubts = call_agent("Verifier", f"List 3 hard questions a human should ask after reading: {report}", "gpt-4o-mini")
        f.write(doubts)

    return filename

if __name__ == "__main__":
    path = run_advanced_session()
    print(f"\n✨ DONE! Artifact saved to: {path}")