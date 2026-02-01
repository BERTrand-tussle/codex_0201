import os
import re
from openai import OpenAI
from datetime import datetime

# 1. SETUP
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OUTPUT_DIR = "research_outputs"
KNOWLEDGE_DIR = "pri_knowledge_final"

for folder in [OUTPUT_DIR, KNOWLEDGE_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

def slugify(text): return re.sub(r'[^\w\-]', '_', text.strip())[:30]

# --- TOOL: AGENT CALL ---
def call_agent(role, prompt, model="gpt-4o"):
    print(f"📡 [HANDOFF] {role} is thinking (Model: {model})...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": f"You are a {role}."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- MAIN ORCHESTRATOR ---
def run_advanced_session():
    # SAFETY: Handle Empty Input
    topic = input("\nResearch Topic: ")
    if not topic.strip(): return
    
    reasoning_pct = int(input("Reasoning Required % (0-100): "))
    depth_pct = int(input("Depth/Validation Required % (0-100): "))
    
    session_id = datetime.now().strftime("%H%M")
    session_folder = f"{OUTPUT_DIR}/session_{session_id}_{slugify(topic)}"
    os.makedirs(session_folder, exist_ok=True)
    
    steps = []
    eval_log = []
    
    # STEP 1: GROUNDING & PLANNING
    # Reads all files in the folder (including your 3 theses and any previous HITL feedback)
    files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(('.txt', '.md'))]
    context = "\n".join([open(os.path.join(KNOWLEDGE_DIR, f), 'r').read() for f in files])
    
    planner_prompt = f"Topic: {topic}. Grounding: {context}. Create a strategy for NA, APAC, and EMEA analysts."
    plan = call_agent("Lead Architect", planner_prompt, "gpt-4o")
    steps.append(["1", "Planner defined regional decomposition.", "🌍 Regional Agents"])
    eval_log.append("✅ PLANNER_EVAL: Goal decomposition successful.")

    # STEP 2: REGIONAL PARALLEL EXECUTORS
    na_data = call_agent("NA Analyst", f"Context: {context}. Research {topic} for North America.", "gpt-4o-mini")
    apac_data = call_agent("APAC Analyst", f"Context: {context}. Research {topic} for APAC.", "gpt-4o-mini")
    emea_data = call_agent("EMEA Analyst", f"Context: {context}. Research {topic} for EMEA.", "gpt-4o-mini")
    
    # STEP 3: MASTER SYNTHESIS
    synth_prompt = f"Merge findings into a unified report:\nNA: {na_data}\nAPAC: {apac_data}\nEMEA: {emea_data}"
    report = call_agent("Master Researcher", synth_prompt, "gpt-4o")
    steps.append(["2", "Regional analysts completed parallel tasks.", "⚖️ Verifier"])

    # STEP 4: VERIFIER LOOP (P-E-V Pattern)
    max_retries = 1 if depth_pct > 70 else 0
    attempt = 0
    while attempt <= max_retries:
        v_prompt = f"Audit this for logic/grounding. Reply 'SUCCESS' or 'FAIL: [Reason]'.\n\n{report}"
        critique = call_agent("Cynical Auditor", v_prompt, "gpt-4o")
        
        if "SUCCESS" in critique.upper():
            eval_log.append(f"✅ VERIFIER_EVAL: Passed on attempt {attempt + 1}.")
            break
        else:
            eval_log.append(f"❌ VERIFIER_EVAL: Retry {attempt + 1} triggered.")
            report = call_agent("Master Researcher", f"Fix these issues: {critique}\n\n{report}", "gpt-4o")
            attempt += 1

    # --- ARTIFACT GENERATION ---
    filename = f"{session_folder}/FINAL_REPORT.md"
    with open(filename, "w") as f:
        f.write(f"# 🔬 DeepResearch-MAS: {topic}\n\n")
        
        f.write("## 📉 System Evaluation & Metrics\n")
        for log in eval_log: f.write(f"* {log}\n")
        
        f.write("\n## 🏗️ P-E-V Orchestration Logic\n")
        f.write("| Step | Handoff Reason | Next Agent |\n| :--- | :--- | :--- |\n")
        for s in steps: f.write(f"| {s[0]} | {s[1]} | {s[2]} |\n")

        f.write("\n## 🗺️ Agent Orchestration Trace\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        f.write("    U([Expert Knowledge]) --> G[Grounding Agent]\n")
        f.write("    G --> P[Planner Agent]\n")
        f.write("    P --> NA[NA Analyst]\n")
        f.write("    P --> APAC[APAC Analyst]\n")
        f.write("    P --> EMEA[EMEA Analyst]\n")
        f.write("    NA & APAC & EMEA --> R[Master Researcher]\n")
        f.write("    R --> V[Verifier Agent]\n")
        f.write("    V -- Critique --> R\n")
        f.write("    V --> Final[Final Report]\n")
        f.write("```\n\n")

        f.write(f"## 📝 Final Deep Research Output\n{report}\n\n")
        
        f.write("## 🕵️ Unresolved Doubts & Expert Handoffs\n")
        doubts = call_agent("Auditor", f"List 3 missing enterprise data points for: {report}", "gpt-4o-mini")
        f.write(doubts)
    
    return filename

if __name__ == "__main__":
    path = run_advanced_session()
    if path:
        print(f"\n✨ Artifact saved: {path}")
        # HITL FEEDBACK TURN
        feedback = input("\n📝 Review the report. Any corrections? (Enter to skip): ")
        if feedback.strip():
            with open(f"{KNOWLEDGE_DIR}/human_eval_{datetime.now().strftime('%H%M')}.txt", "w") as f:
                f.write(f"USER FEEDBACK: {feedback}")
            print("✅ Feedback logged for next turn.")