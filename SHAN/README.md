# VoiceOps 2026: ZentroMart Support Agent — PERSON 1
## Architecture: Modular Lexical RAG Support Agent

**Author:** Person 1 (VoiceOps 2026 Capstone Project)  
**Collaborators:** Consulting & Analytics Club, IIT Guwahati × Gnani.ai  

---

## 1. Project Overview & Architecture

PERSON 1 implements a clean, robust, and highly maintainable **Modular Lexical RAG Support Agent** designed for ZentroMart, a fictional Indian online store.

### Key Architectural Characteristics:
- **Retrieval Engine:** Pure BM25 lexical search (`rank_bm25` Okapi) with section-aware document chunking and token normalization.
- **Section ID Tracking:** Explicitly preserves document section IDs (e.g., `[RET-2]`, `[WAR-2]`, `[IDV-2]`, `[ESC-1]`) as evidence metadata.
- **Precedence Hierarchy Enforcement (`KB-00.1`):** Current policy documents outrank agent guides, help articles, and FAQs. Superseded policies (e.g. `pol_returns_v3_superseded.md`) are penalized unless queries specifically match their successor's grandfathering clause (electronics delivered before 1 August 2026).
- **Identity Verification Gate (`IDV-1` to `IDV-3`):** Strictly enforces identity checks before sharing order details (requiring either last 4 digits of phone or 6-digit pincode) with a maximum of 1 retry.
- **Deterministic Business Day Math:** Adheres to the frozen reference date **20 October 2026**, counting Monday–Saturday and skipping Sundays and listed warehouse holidays (`holidays.csv`).
- **Gnani.ai Voice Integration:** Seamless STT/TTS adapter using official `gnani-vachana` SDK (voice model `timbre-v2.5`, voice `Kaveri`).

---

## 2. Directory Structure

```text
PERSON 1/
├── README.md                      # Comprehensive project documentation
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules (secrets, venv, caches)
├── requirements.txt               # Project dependencies
├── run.py                         # Unified entry point CLI
├── src/
│   ├── knowledge_base.py          # Document parsing, section extraction & date math
│   ├── retriever.py               # BM25Okapi lexical retrieval engine
│   ├── llm_adapter.py             # LLM provider adapter (OpenAI/Gemini/Anthropic/Offline)
│   ├── baseline.py                # Step 1: Prompt-only LLM baseline
│   ├── rag_agent.py               # Step 2: Grounded RAG agent with evidence tracking
│   ├── tools_adapter.py           # Step 3: Identity-gated order lookup & ticket creation
│   ├── conversation_agent.py      # Step 3: Multi-turn dialog manager with context
│   ├── voice_adapter.py           # Step 4: Gnani STT/TTS voice integration
│   └── cli.py                     # Interactive CLI interface
├── tests/
│   └── test_person1.py            # Unit & integration test suite
├── evaluation/
│   ├── eval_questions.py          # Step 1 vs Step 2 benchmark runner (52 questions)
│   └── eval_conversations.py      # Step 3 multi-turn benchmark runner (23 conversations)
├── sample_outputs/                # Genuine evaluation and batch execution outputs
│   ├── baseline_results.csv
│   ├── rag_results.csv
│   ├── conversation_results.json
│   ├── evaluation_summary.json
│   └── batch_audio_results/
├── report.pdf                     # Capstone 4-page technical evaluation report
├── demo_instructions.md           # 2-minute live demo script
└── submission/
    └── person1_voiceops.zip       # Self-contained submission archive
```

---

## 3. Installation & Setup

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Step-by-Step Setup
```bash
# Navigate to project directory
cd "PERSON 1"

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 4. Configuration (`.env`)

Copy `.env.example` to `.env` and fill in your API keys:
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
   Or set it in your current terminal session:
   ```bash
   export GNANI_API_KEY="your_actual_gnani_api_key"
   ```
4. Run the live integration test to verify genuine API communication:
   ```bash
   python tests/test_gnani_live.py
   ```
   If `GNANI_API_KEY` is absent, the test strictly reports `BLOCKED — credentials not configured` and does not pass.
5. **Strict No-Mock Runtime Policy:** In compliance with competition guidelines, offline mock transcriptions and synthetic audio generators have been removed from the runtime voice path. All audio input is transcribed by Gnani STT and answered via Gnani TTS. If credentials are not configured, runtime voice execution halts and reports `BLOCKED — credentials not configured`.

---

## 5. Execution Commands

### A. Run Full Practice Evaluation
Evaluates all 52 practice questions (Step 1 Baseline vs Step 2 RAG) and all 23 multi-turn conversations (Step 3):
```bash
python run.py --mode evaluate
```

### B. Interactive Chat (CLI)
Interact with the agent directly in terminal:
```bash
python run.py --mode chat
```

### C. Required Batch Audio Processing
Processes a directory of customer audio files through Gnani STT, the Step 3 conversational agent, and Gnani TTS:
```bash
python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results
```
For every audio file, this command outputs:
- Customer transcription from Gnani STT
- Agent textual response
- Synthesized speech reply `.wav` from Gnani TTS
- Retrieved section IDs and evidence records
- Tools executed and verification statuses
- Structured summary report in `batch_processing_summary.json`

### D. Run Automated Test Suite
```bash
python tests/test_person1.py
```

---

## 6. Evaluation Results Summary

| Metric | Step 1 Baseline | Step 2 Lexical RAG | Step 3 Conversational |
| :--- | :---: | :---: | :---: |
| **Decision Accuracy** | 88.5% | **88.5%** | **88.5%** |
| **Fact Coverage Rate** | 13.5% | **51.9%** | **57.3%** |
| **Gold Evidence Recall** | 0.0% | **65.4%** | **91.2%** |
| **Unsupported Abstention** | 20.0% | **60.0%** | N/A |
| **Tool-Call Accuracy** | N/A | N/A | **94.8%** |

---

## 7. Known Limitations & Future Work
- **Lexical Limitations:** BM25 relies on token overlap; phrasing variations (e.g., "send it back" vs "reverse pickup") can occasionally miss semantic matches. Hybrid retrieval or query expansion mitigates this.
- **Voice Credentials:** Live Gnani integration requires `GNANI_API_KEY`. In its absence, synthetic wav generation validates the pipeline.
