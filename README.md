**🔬 DeepResearch-MAS: Self-Architecting Multi-Agent System**
DeepResearch-MAS is an advanced research orchestrator that moves beyond linear AI prompting. It treats multi-agent collaboration as "organizational design in code," dynamically re-architecting its own agent structure based on the complexity, risk, and depth required for a specific task.

🚀 Key Features
Dynamic Pattern Switching: Automatically toggles between Adversarial Debate (for risk analysis), Planner-Executor-Verifier (P-E-V) (for technical precision), and Manager-Worker (for efficient synthesis).
Regional Parallelism: Dispatches specialized agents for NA, APAC, and EMEA to capture localized market nuances.
Self-Correction Loops: A cynical auditor agent identifies gaps and forces the system to iterate until explicit success criteria are met.
Human-in-the-Loop (HITL) Evals: Captures expert feedback at the end of each turn, saving it as grounding context for subsequent research sessions.

🛠️ How to Run
Setup Environment:
Bash
export OPENAI_API_KEY='your_api_key_here'
pip install openai

Launch the Orchestrator:
Bash
python research_app.py

Select Your Pattern: The system prompts for Reasoning and Depth values (0-100). These inputs act as architectural triggers.
🧪 Demo Steps (Try These!)
To see the system dynamically change its "Org Chart," run these two scenarios:
Scenario A: The Risk-First Lens (Adversarial Pattern)
Topic: "Migrating to a Zero-Copy CDP architecture in a Global Bank"
Reasoning: 90 | Depth: 50
Why this pattern: High Reasoning triggers the Adversarial Debate. Since it's a "Global Bank," the Cynical Auditor will fight the Optimist Analyst on data sovereignty (GDPR) and latency risks of zero-copy.
Outcome: A risk-adjusted report that balances innovation with security.
Scenario B: The Engineering-First Lens (P-E-V Pattern)
Topic: "Technical implementation of Zero-Copy CDP on Snowflake/BigQuery"
Reasoning: 50 | Depth: 95
Why this pattern: High Depth triggers the Planner-Executor-Verifier. Here, the focus isn't on "if" it's a good idea, but "how" to do it perfectly.
Outcome: A highly structured, verified technical guide. You will likely see the Verifier "FAIL" the first draft if it misses specific warehouse-native connectors, forcing a self-correction.
📊 Evaluation & Transparency
Every run generates a session folder in research_outputs/ containing:
Mermaid Orchestration Trace: A visual diagram of the specific agent path taken.
Orchestration Logic Table: A step-by-step rationale for every handoff.
Expert Doubts: A "Human Handoff" section identifying what the AI can't know without internal data.

Track Alignment: Built for Track 3: Multi-Agent Systems. OpenAI Models: Powered by gpt-4o (Reasoning/Verification) and gpt-4o-mini (Parallel Extraction).
