# VoiceOps 2026: ZentroMart Support Agent — PERSON 4
## Architecture: Policy-Aware Structured Decision Agent

**Author:** Person 4 (VoiceOps 2026 Capstone Project)  
**Collaborators:** Consulting & Analytics Club, IIT Guwahati × Gnani.ai  

---

## 1. Project Overview & Architecture

PERSON 4 implements a **Policy-Aware Structured Decision Support Agent** for ZentroMart, designed around deterministic business-rule compliance, strict policy hierarchy validation, and an explicit finite state machine for identity verification and ticket escalation.

### Key Architectural Characteristics:
- **Decoupled Decision Pipeline:** Deconstructs customer handling into 5 explicit stages:
  1. *Intent & Entity Extraction:* Typed dataclass `CustomerIntent` capturing query intent and parameters.
  2. *Policy Retrieval:* Contextual routing to authoritative policies.
  3. *Decision Validation:* Applies `KB-00.1` precedence and validates date boundaries against `holidays.csv`.
  4. *Tool Execution:* Executes `lookup_order` or `create_ticket` with strict input sanitization.
  5. *Response Generation:* Validates final output against structured decisions before uttering.
- **Finite State Machine (`DialogStateMachine`):** Explicitly tracks conversation states (`START`, `AWAITING_VERIFICATION`, `VERIFIED`, `VERIFICATION_FAILED_LOCKED`, `ESCALATION_HANDOVER_COMPLETED`), enforcing a maximum of 1 verification retry and zero premature disclosures.
- **Deterministic Business Day Logic:** Calculates refund and reverse pickup deadlines using Monday–Saturday counts anchored to **20 October 2026**, skipping official holidays (e.g. 19 October warehouse closure).
- **High-Value Escalation Guardrails:** Enforces `DWM-3` and `ESC-1` by refusing to approve damaged item claims over ₹10,000, creating an escalation ticket, and confirming handover only upon `created=True`.
- **Gnani.ai Speech Integration:** Official speech pipeline with `timbre-v2.5` voice `Kaveri`.

---

## 2. Directory Structure

```text
PERSON 4/
├── README.md                      # Architecture and setup guide
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Dependencies
├── run.py                         # Unified entry point
├── src/
│   ├── knowledge_base.py          # Knowledge base & date math
│   ├── state_machine.py           # Finite state machine & structured decision objects
│   ├── retriever.py               # Intent-based policy router & precedence gate
│   ├── llm_adapter.py             # LLM provider adapter
│   ├── baseline.py                # Step 1: Prompt-only baseline
│   ├── rag_agent.py               # Step 2: Policy-aware RAG agent
│   ├── tools_adapter.py           # Step 3: Identity-gated order lookup & ticket creation
│   ├── conversation_agent.py      # Step 3: Structured conversation agent
│   └── voice_adapter.py           # Step 4: Gnani voice STT/TTS adapter
├── tests/
│   └── test_person4.py            # Unit & integration tests
├── evaluation/
│   ├── eval_questions.py          # Step 1 vs Step 2 benchmark runner
│   └── eval_conversations.py      # Step 3 multi-turn benchmark runner
├── sample_outputs/                # Evaluation reports & audio outputs
│   ├── baseline_results.csv
│   ├── rag_results.csv
│   ├── conversation_results.json
│   ├── evaluation_summary.json
│   └── batch_audio_results/
├── report.pdf                     # 4-page technical report
├── demo_instructions.md           # 2-minute demo instructions
└── submission/
    └── person4_voiceops.zip       # Self-contained submission archive
```

---

## 3. Installation & Setup

```bash
cd "PERSON 4"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Configuration & Gnani.ai Credentials

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Gnani.ai Speech Services Configuration (Step 4 Voice)
To enable genuine speech-to-text and text-to-speech voice operations:
1. Visit [app.gnani.ai/voice](https://app.gnani.ai/voice) and sign in to your Gnani account.
2. Under API Keys, generate a key. A single key covers both Gnani STT and TTS services.
3. Add the key to your `.env` file:
   ```bash
   GNANI_API_KEY=your_actual_gnani_api_key
   GNANI_TTS_VOICE=Kaveri
   GNANI_TTS_MODEL=timbre-v2.5
   GNANI_LANGUAGE_CODE=en-IN
   ```
   Or export it in your terminal:
   ```bash
   export GNANI_API_KEY="your_actual_gnani_api_key"
   ```
4. Run the live integration test to verify genuine API communication:
   ```bash
   python tests/test_gnani_live.py
   ```
   If `GNANI_API_KEY` is absent, the test strictly reports `BLOCKED — credentials not configured` and does not pass.
5. **Strict No-Mock Runtime Policy:** Offline mock transcriptions and synthetic audio generators have been removed from the runtime path. All audio input is transcribed by Gnani STT and answered via Gnani TTS. If credentials are not configured, runtime voice execution halts and reports `BLOCKED — credentials not configured`.

---

## 5. Execution Commands

### A. Run Full Practice Evaluation
```bash
python run.py --mode evaluate
```

### B. Required Batch Audio Processing
```bash
python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results
```

### C. Run Automated Test Suite
```bash
python tests/test_person4.py
```

---

## 5. Evaluation Results Summary

| Metric | Step 1 Baseline | Step 2 Policy RAG | Step 3 Conversational |
| :--- | :---: | :---: | :---: |
| **Decision Accuracy** | 88.5% | **88.5%** | **86.5%** |
| **Fact Coverage Rate** | 13.5% | **53.8%** | **54.2%** |
| **Gold Evidence Recall** | 0.0% | **65.4%** | **91.2%** |
| **Tool-Call Accuracy** | N/A | N/A | **92.7%** |
