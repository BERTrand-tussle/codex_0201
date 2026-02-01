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
    print(f"📡 [ORCHESTRATION] {role} is active...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": f"You are a {role}."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- MAIN ENGINE ---
def run_dynamic_mas():
    # SAFETY: Handle Empty Input
    topic = input("\nEnter Research Topic: ")
    if not topic.strip(): return
    
    reasoning_pct = int(input("Reasoning & Conflict Required % (0-100): "))
    depth_pct = int(input("Depth & Verification Required % (0-100): "))
    
    session_id = datetime.now().strftime("%H%M")
    session_folder = f"{OUTPUT_DIR}/session_{session_id}_{slugify(topic)}"
    os.makedirs(session_folder, exist_ok=True)
    
    # 2. PATTERN SELECTION LOGIC (The "Self-Architecting" Step)
    if reasoning_pct > 80:
        pattern = "ADVERSARIAL_DEBATE"
        p_desc = "High-stakes conflict detected. Triggering Adversarial Debate to surface risks."
    elif depth_pct > 80:
        pattern = "PLANNER_EXECUTOR_VERIFIER"
        p_desc = "Extreme precision required. Triggering P-E-V with mandatory self-correction loops."
    else:
        pattern = "MANAGER_WORKER"
        p_desc = "Standard inquiry detected. Using Manager-Worker pattern for efficient throughput."

    print(f"🚀 {p_desc}")

    # 3. GROUNDING
    files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(('.txt', '.md'))]
    context = "\n".join([open(os.path.join(KNOWLEDGE_DIR, f), 'r').read() for f in files])
    
    steps = [["0", "Grounding Scan", "System initialized with expert world-view docs."]]
    eval_log = [f"✅ PATTERN_TRIGGER: {pattern} selected."]
    final_report = ""

    # --- PATTERN 1: ADVERSARIAL DEBATE ---
    if pattern == "ADVERSARIAL_DEBATE":
        pro = call_agent("Optimist Analyst", f"Argue FOR the long-term viability of {topic} based on: {context}")
        con = call_agent("Cynical Auditor", f"Find critical flaws and risks in {topic} based on: {context}")
        steps.append(["1", "Adversarial Turn", "Optimist and Auditor generated conflicting viewpoints."])
        final_report = call_agent("Lead Judge", f"Synthesize this debate into a risk-adjusted report:\nPRO: {pro}\nCON: {con}")
        steps.append(["2", "Synthesis", "Judge mediated debate into final artifact."])

    # --- PATTERN 2: P-E-V (PLANNER-EXECUTOR-VERIFIER) ---
    elif pattern == "PLANNER_EXECUTOR_VERIFIER":
        plan = call_agent("Lead Architect", f"Create a multi-step research strategy for {topic} using: {context}")
        steps.append(["1", "Planning", "Architect defined execution steps."])
        
        # Parallel Execution (Simulated)
        exec_output = call_agent("Executor", f"Follow this plan: {plan}")
        steps.append(["2", "Execution", "Executor processed plan into draft report."])
        
        # Mandatory Verification Loop
        v_prompt = f"Audit this report for goal drift and logical gaps:\n{exec_output}"
        critique = call_agent("Verifier", v_prompt)
        final_report = call_agent("Executor", f"Apply this critique to the report: {critique}\nOriginal: {exec_output}")
        steps.append(["3", "Verification Loop", "Verifier forced one round of self-correction."])
        eval_log.append("✅ VERIFIER_EVAL: Self-correction loop completed.")

    # --- PATTERN 3: MANAGER-WORKER ---
    else:
        worker_res = call_agent("Worker", f"Summarize {topic} research using context: {context}", model="gpt-4o-mini")
        steps.append(["1", "Task Assignment", "Manager assigned task to efficient worker agent."])
        final_report = call_agent("Manager", f"Review and format this worker output: {worker_res}")
        steps.append(["2", "Review", "Manager finalized output."])

    # --- ARTIFACT GENERATION ---
    filename = f"{session_folder}/FINAL_REPORT.md"
    with open(filename, "w") as f:
        f.write(f"# 🔬 DeepResearch-MAS: {topic}\n\n")
        f.write(f"> **Orchestration Pattern:** {pattern}\n\n")
        
        f.write("## 📉 System Evaluation & Metrics\n")
        for log in eval_log: f.write(f"* {log}\n")
        
        f.write("\n## 🏗️ Dynamic Orchestration Logic\n")
        f.write("| Step | Handoff Reason | Next Agent |\n| :--- | :--- | :--- |\n")
        for s in steps: f.write(f"| {s[0]} | {s[1]} | {s[2]} |\n")

        # MERMAID (Simplified to adapt to pattern)
        f.write("\n## 🗺️ Agent Orchestration Trace\n")
        f.write("```mermaid\n")
        if pattern == "ADVERSARIAL_DEBATE":
            f.write("graph TD\n    G[Grounding] --> P[Optimist]\n    G --> C[Auditor]\n    P & C --> J[Judge]\n    J --> F[Final Report]\n")
        elif pattern == "PLANNER_EXECUTOR_VERIFIER":
            f.write("graph TD\n    G[Grounding] --> Pl[Planner]\n    Pl --> E[Executor]\n    E --> V[Verifier]\n    V -->|Correction| E\n    E --> F[Final Report]\n")
        else:
            f.write("graph TD\n    G[Grounding] --> M[Manager]\n    M --> W[Worker]\n    W --> M\n    M --> F[Final Report]\n")
        f.write("```\n\n")

        f.write(f"## 🏆 Multi-Agent vs. Single-Agent Benchmarks\n")
        f.write("| Feature | Traditional LLM | This MAS System |\n| :--- | :--- | :--- |\n")
        f.write(f"| **Pattern** | Static / Linear | Dynamic {pattern} |\n| **Bias** | Highly Optimistic | { 'Adversarial Counter-weight' if pattern == 'ADVERSARIAL_DEBATE' else 'Verified Truths' } |\n\n")

        f.write(f"## 📝 Final Deep Research Output\n{final_report}\n\n")
        
        f.write("## 🕵️ Unresolved Doubts & Expert Handoffs\n")
        doubts = call_agent("Auditor", f"Identify 3 missing enterprise data points for: {final_report}", "gpt-4o-mini")
        f.write(doubts)
    
    return filename

if __name__ == "__main__":
    path = run_dynamic_mas()
    if path:
        print(f"\n✨ DONE! Artifact saved: {path}")
        # HITL Feedback
        fb = input("\n📝 Any corrections for the next turn? ")
        if fb.strip():
            with open(f"{KNOWLEDGE_DIR}/human_eval_{datetime.now().strftime('%H%M')}.txt", "w") as f:
                f.write(f"USER FEEDBACK: {fb}")