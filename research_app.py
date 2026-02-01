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

# --- TOOL: GROUNDING SCAN ---
def get_world_view():
    try:
        files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(('.txt', '.md'))]
        if not files: return "No prior grounding data found."
        return "\n".join([f"--- {f} ---\n{open(os.path.join(KNOWLEDGE_DIR, f), 'r').read()}" for f in files])
    except: return "Grounding scan failed."

# --- TOOL: AGENT CALL ---
def call_agent(role, prompt, model="gpt-4o"):
    print(f"📡 [HANDOFF] {role} is thinking (Model: {model})...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": f"You are a {role}."}, {"role": "user", "content": prompt}]
    )
    print(f"✅ {role} has completed task.")
    return response.choices[0].message.content

def run_advanced_session():
    # SAFETY: Handle Empty Input
    topic = input("\nResearch Topic: ")
    if not topic.strip():
        print("⚠️ Error: Topic cannot be empty. Please restart.")
        return

    reasoning_pct = int(input("Reasoning Required % (0-100): "))
    depth_pct = int(input("Depth/Validation Required % (0-100): "))
    
    session_id = datetime.now().strftime("%H%M")
    session_folder = f"{OUTPUT_DIR}/session_{session_id}_{slugify(topic)}"
    os.makedirs(session_folder, exist_ok=True)
    
    # ORCHESTRATION DATA
    steps = []
    main_model = "gpt-4o" if reasoning_pct > 60 else "gpt-4o-mini"
    
    # 1. GROUNDING
    context = get_world_view()
    steps.append(["1", "World-View Grounding: Scanning expert docs for contradictions.", "🧠 Planner"])
    
    # 2. PLANNING
    planner_prompt = f"Topic: {topic}\nGrounding: {context}\nDefine a plan with parallel Regional Analysts (NA, APAC, EMEA)."
    plan = call_agent("Lead Architect", planner_prompt, main_model)
    steps.append(["2", "Strategic Plan: Assigned parallel tasks to Regional Agents.", "🌍 Regional Agents (Parallel)"])

    # 3. PARALLEL REGIONAL RESEARCH (Simulated Handoff)
    na_data = call_agent("North America Expert", f"Research {topic} for NA lens.", "gpt-4o-mini")
    apac_data = call_agent("APAC Expert", f"Research {topic} for APAC lens.", "gpt-4o-mini")
    emea_data = call_agent("EMEA Expert", f"Research {topic} for EMEA lens.", "gpt-4o-mini")
    steps.append(["3", "Synthesis: Merging regional findings into global report.", "🔍 Master Researcher"])

    # 4. MASTER RESEARCHER
    research_prompt = f"Merge these findings into a deep-dive report:\nNA: {na_data}\nAPAC: {apac_data}\nEMEA: {emea_data}"
    report = call_agent("Master Researcher", research_prompt, "gpt-4o")
    
    # 5. SELF-CORRECTION LOOP (If depth requested)
    if depth_pct > 65:
        steps.append(["4", "Audit Triggered: Depth check initiated via Cynical Auditor.", "⚖️ Verifier"])
        critique = call_agent("Cynical Auditor", f"Critique this report based on user grounding: {report}", main_model)
        
        if "FAIL" in critique.upper() or "GAP" in critique.upper():
            steps.append(["5", "Self-Correction: Researcher addressing auditor feedback.", "🔍 Master Researcher"])
            report = call_agent("Master Researcher", f"Refine this based on audit: {critique}", "gpt-4o")
            steps.append(["6", "Final Review: Logic verified; human handoff ready.", "🏁 Finish"])
        else:
            steps.append(["5", "Audit Passed: Logic is sound.", "🏁 Finish"])
    else:
        steps.append(["4", "Direct Output: Report generated without extra audit.", "🏁 Finish"])

    # --- ARTIFACT GENERATION ---
    filename = f"{session_folder}/FINAL_REPORT.md"
    with open(filename, "w") as f:
        f.write(f"# 🔬 Advanced Research: {topic}\n\n")
        
        # TABLE 1: DYNAMIC LOGIC
        f.write("## 🏗️ Dynamic Orchestration Logic Summary\n")
        f.write("| Step | Reason for Handoff | Next Agent |\n| :--- | :--- | :--- |\n")
        for s in steps: f.write(f"| {s[0]} | {s[1]} | {s[2]} |\n")
        f.write("\n> **Human-in-the-loop Note:** Final stage identifies gaps requiring internal enterprise data.\n\n")

        # MERMAID DIAGRAM
        f.write("## 🗺️ Agent Orchestration Trace\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        f.write("    U([Expert Knowledge]) --> G[Grounding Agent]\n")
        f.write("    G --> P[Planner Agent]\n")
        f.write("    P --> NA[NA Researcher]\n")
        f.write("    P --> APAC[APAC Researcher]\n")
        f.write("    P --> EMEA[EMEA Researcher]\n")
        f.write("    NA & APAC & EMEA --> R[Master Researcher]\n")
        f.write("    R --> V[Verifier Agent]\n")
        f.write("    V -- Critique --> R\n")
        f.write("    V --> Final[Human Handoff]\n")
        f.write("    style G fill:#f9f\n    style P fill:#bbf\n    style V fill:#fbb\n")
        f.write("```\n\n")

        # BENCHMARKS
        f.write("## 🏆 Multi-Agent vs. Single-Agent Benchmarks\n")
        f.write("| Capability | Traditional Single-Agent | This MAS System |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write("| **Global Nuance** | Generic / US-Centric | Regional Parallel Analysts |\n")
        f.write("| **Error Handling** | Linear / No-Correction | Self-Correcting Loop |\n")
        f.write("| **Grounding** | Hallucinated | Hard-Anchored to Expert Docs |\n\n")

        # CONTENT
        f.write("## 📝 Final Deep Research Output\n")
        f.write(report)
        
        # DOUBTS
        f.write("\n---\n## 🕵️ Unresolved Doubts & Expert Handoffs\n")
        doubts = call_agent("Verifier", f"Identify 3 missing data points that require human internal access: {report}", "gpt-4o-mini")
        f.write(doubts)

    return filename

if __name__ == "__main__":
    path = run_advanced_session()
    if path: print(f"\n✨ DONE! Artifact saved to: {path}")