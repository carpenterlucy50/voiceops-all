# VoiceOps 2026 — Project 6: Evaluation-Driven Adaptive RAG Agent

**Author:** PERSON 6  
**Institution:** Consulting & Analytics Club, IIT Guwahati × Gnani.ai  
**Domain:** ZentroMart AI Customer Support (Voice & Multimodal Agent)

---

## 1. Project Overview & Distinct Architecture

Project 6 implements an **Evaluation-Driven Adaptive Retrieval-Augmented Generation (RAG) System** designed to empirically measure, compare, and dynamically route customer queries across multiple retrieval paradigms rather than assuming a single static pipeline.

### Distinct Technical Features
1. **Dynamic Adaptive Routing:** Automatically detects query characteristics (exact SKUs, policy codes, short phrases vs conversational inquiries) and routes to BM25 lexical, Dense TF-IDF cosine, or Reciprocal Rank Fusion (RRF) hybrid search.
2. **Confidence-Guided Abstention:** Calculates an absolute confidence score combining dense cosine similarity and lexical token frequency. If the score falls below the abstention threshold (`0.22`), the agent safely abstains rather than hallucinating unsupported claims.
3. **Execution Tracing:** Every query produces a comprehensive `RetrievalTrace` recording latency (ms), candidates scored, strategy used, top score, confidence score, and abstention status.
4. **Parameter Grid Benchmark Suite:** Evaluates combinations of strategies (`lexical`, `dense`, `hybrid`, `adaptive`) across Top-K (3, 5, 7) on the official 52 practice questions, outputting both JSON analytics and an interactive HTML Dashboard (`sample_outputs/benchmark_dashboard.html`).
5. **Error Categorization:** Automatically classifies failure points during multi-turn conversations (`VERIFICATION_RETRY`, `VERIFICATION_FAILED`, `HIGH_VALUE_ESCALATION`, `UNSUPPORTED_OR_OUT_OF_DOMAIN`).
6. **Voice Integration with Gnani.ai:** Batch speech processing using `gnani-vachana` SDK with voice `Kaveri`, model `timbre-v2.5`, and language `en-IN`.

---

## 2. Directory Structure

```
PERSON 6/
├── 6ad64c83eae85_voiceops_2026_capstone_brief (1).pdf
├── Capstone_Project_Dataset_FTTT_2026/
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
├── generate_report.py
├── report.pdf
├── demo_instructions.md
├── README.md
├── src/
│   ├── knowledge_base.py
│   ├── retriever.py
│   ├── benchmark_suite.py
│   ├── llm_adapter.py
│   ├── baseline.py
│   ├── rag_agent.py
│   ├── tools_adapter.py
│   ├── conversation_agent.py
│   └── voice_adapter.py
├── evaluation/
│   ├── eval_questions.py
│   └── eval_conversations.py
├── tests/
│   └── test_person6.py
├── sample_outputs/
│   ├── benchmark_dashboard.html
│   ├── benchmark_summary.json
│   ├── step1_vs_step2_metrics.json
│   ├── conversations_eval_results.json
│   ├── test_audio/
│   └── audio_batch_results/
└── submission/
    └── person6_voiceops.zip
```

---

## 3. Setup and Installation

### 3.1 Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Configuration & Gnani.ai Credentials
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

#### Gnani.ai Speech Services Configuration (Step 4 Voice)
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
5. **Strict No-Mock Runtime Policy:** Offline mock transcriptions and synthetic audio generators have been removed from the runtime path. All audio input is transcribed by Gnani STT and answered via Gnani TTS while capturing adaptive `RetrievalTrace` metadata. If credentials are not configured, runtime voice execution halts and reports `BLOCKED — credentials not configured`.

---

## 4. Run Commands

### 4.1 Interactive CLI Support Chat
```bash
python3 run.py --mode chat --strategy adaptive --top-k 5
```
Commands during chat:
- `trace`: Shows the detailed `RetrievalTrace` for the last query.
- `reset`: Clears current session state.
- `exit`: Quits the chat.

### 4.2 Benchmark Grid Evaluation & HTML Dashboard
```bash
python3 run.py --mode benchmark
```
Outputs:
- Dashboard: `sample_outputs/benchmark_dashboard.html`
- Analytics: `sample_outputs/benchmark_summary.json`

### 4.3 Run Step 1 vs Step 2 and Step 3 Multi-Turn Evaluation
```bash
python3 run.py --mode evaluate
```

### 4.4 Batch Audio Processing Command (Official Step 4)
```bash
python3 run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/audio_batch_results
```

### 4.5 Run Automated Tests
```bash
python3 tests/test_person6.py
```

---

## 5. Benchmark & Evaluation Results

### Practice Questions (52 Cases)
- **Step 1 Baseline:** 88.5% Decision Accuracy, 0.0% Fact Coverage (ungrounded).
- **Step 2 Adaptive RAG:** 82.7% Decision Accuracy, 53.8% Gold Evidence Hit Rate, 20.0% Appropriate Abstention.
- **Top Retrieval Strategy:** Hybrid RRF (Top-K=7) achieved **67.3% precision** with ~3.4 ms latency.

### Multi-Turn Practice Conversations (23 Conversations, 96 Turns)
- **Decision Accuracy:** 87.5%
- **Tool-Call Compliance:** 94.8%
- **Error Categories Tracked:**
  - `VERIFICATION_RETRY`: 23
  - `VERIFICATION_FAILED`: 4
  - `HIGH_VALUE_ESCALATION`: 1
  - `UNSUPPORTED_OR_OUT_OF_DOMAIN`: 1

---

## 6. Known Limitations
- When running in offline mode without live Gnani credentials, ASR uses deterministic utterance parsing and TTS generates 16kHz synthetic sine waves.
- Grid experiments evaluate practice cases within the test set; expanding to live user queries will require online telemetry.
