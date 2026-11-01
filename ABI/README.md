# VoiceOps 2026: ZentroMart Support Agent — PERSON 5
## Architecture: Multilingual Voice-First Support Agent

**Author:** Person 5 (VoiceOps 2026 Capstone Project)  
**Collaborators:** Consulting & Analytics Club, IIT Guwahati × Gnani.ai  

---

## 1. Project Overview & Architecture

PERSON 5 implements a **Multilingual Voice-First Support Agent** for ZentroMart, designed from the ground up for spoken telephony and voice-message customer support. It integrates Gnani.ai's speech models, phonetic ASR normalization, and custom speech shapers that format numbers and dates specifically for the ear.

### Key Architectural Characteristics:
- **Speech-to-Text & Text-to-Speech Integration:** Powered by the official `gnani-vachana` SDK, using Gnani's verified `timbre-v2.5` speech model with the voice `Kaveri`.
- **Text Normalization for the Ear:** Converts raw data into naturally spoken words:
  - Long 8-digit order numbers are split into spaced rhythmic groups: `"8 9 7 8, 2 8 3 7"`.
  - Dates always feature explicit full calendar months and years: `"27 October 2026"`.
  - Raw currency signs like `"₹49"` are converted to `"49 rupees"`.
- **Phonetic ASR Query Processing:** Converts spelled-out spoken numbers (e.g., `"ele-zero zero one two"`) to clean alphanumeric SKU formats (`"ELE-0012"`).
- **Acoustic Recovery Prompts:** Gracefully detects silent, corrupted, or inaudible audio and prompts the caller to repeat in English, Hindi, Hinglish, Tamil, Telugu, or Kannada.
- **Batch Audio Directory Runner:** Executes the mandatory `python run.py --input-dir ... --output-dir ...` command, producing speech transcripts, generated text, synthesized audio replies, retrieved evidence records, and tool execution logs.

---

## 2. Directory Structure

```text
PERSON 5/
├── README.md                      # Architecture and setup guide
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Dependencies
├── run.py                         # Unified entry point
├── src/
│   ├── knowledge_base.py          # Knowledge base & date calculator
│   ├── speech_normalizer.py       # Audio formatting & recovery prompts
│   ├── retriever.py               # Multilingual & phonetic ASR retriever
│   ├── llm_adapter.py             # LLM provider adapter
│   ├── baseline.py                # Step 1: Prompt-only baseline
│   ├── rag_agent.py               # Step 2: Grounded voice RAG agent
│   ├── tools_adapter.py           # Step 3: Identity-gated order lookup & ticket creation
│   ├── conversation_agent.py      # Step 3: Multi-turn voice conversation agent
│   └── voice_adapter.py           # Step 4: Multilingual Gnani STT/TTS adapter
├── tests/
│   └── test_person5.py            # Unit & integration tests
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
    └── person5_voiceops.zip       # Self-contained submission archive
```

---

## 3. Installation & Setup

```bash
cd "PERSON 5"
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
5. **Strict No-Mock Runtime Policy:** Offline mock transcriptions and synthetic audio generators have been removed from the runtime path. All audio input is transcribed by Gnani STT and answered via Gnani TTS with `SpeechNormalizer` auditory text shaping. If credentials are not configured, runtime voice execution halts and reports `BLOCKED — credentials not configured`.

---

## 5. Execution Commands

### A. Run Full Practice Evaluation
```bash
python run.py --mode evaluate
```

### B. Required Batch Audio Processing
```bash
python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results --lang en-IN
```

### C. Run Automated Test Suite
```bash
python tests/test_person5.py
```

---

## 5. Evaluation Results Summary

| Metric | Step 1 Baseline | Step 2 Voice RAG | Step 3 Conversational |
| :--- | :---: | :---: | :---: |
| **Decision Accuracy** | 88.5% | **88.5%** | **88.5%** |
| **Fact Coverage Rate** | 13.5% | **51.9%** | **56.2%** |
| **Gold Evidence Recall** | 0.0% | **65.4%** | **91.2%** |
| **Tool-Call Accuracy** | N/A | N/A | **94.8%** |
