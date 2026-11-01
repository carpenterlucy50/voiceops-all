# VoiceOps 2026 — Project 6 Demo Instructions

This script provides a precise 2-minute demonstration plan showcasing the distinct features of **Project 6 (Evaluation-Driven Adaptive RAG Agent)**.

---

## 2-Minute Demo Flow

### 0:00 - 0:30: Scene 1 — Adaptive Grid Benchmark & Dashboard
- **Action:** Open terminal and run:
  ```bash
  python3 run.py --mode benchmark
  ```
- **Show:** The terminal logs showing the grid execution over `lexical`, `dense`, `hybrid`, and `adaptive` retrieval across Top-K 3, 5, 7.
- **Show UI:** Open `sample_outputs/benchmark_dashboard.html` in a web browser to display the comparative matrix, latency (ms), and hit rate metrics.
- **Talking Point:** "In Project 6, rather than assuming a single static RAG pipeline, we empirically benchmark multiple retrieval paradigms, measuring precision, latency, and abstention across the parameter space."

---

### 0:30 - 1:00: Scene 2 — Document-Grounded Policy Query with Execution Trace
- **Action:** In terminal, run:
  ```bash
  python3 run.py --query "What is the return window for clothing purchased during the festive sale?"
  ```
- **Show Output:**
  - Generated answer correctly citing `RET-8` (30-day extended window).
  - The printed `trace` dictionary showing:
    - Strategy used: `hybrid`
    - Latency: ~3.2 ms
    - Confidence score: `> 0.85`
    - Abstention: `False`
- **Talking Point:** "Every query captures an explicit `RetrievalTrace`, detailing the latency, confidence score, and document authority distribution."

---

### 1:00 - 1:30: Scene 3 — Confidence-Based Abstention & Multi-Turn Verification
- **Action:** Launch the chat CLI:
  ```bash
  python3 run.py --mode chat
  ```
- **Step A (Abstention):** Ask:
  ```
  Customer > Do you accept Bitcoin cryptocurrency payments?
  ```
  - **Show:** The agent politely abstains: *"Our official documentation does not contain support or policy guidelines for this query."*
- **Step B (Multi-turn Order Verification):**
  ```
  Customer > Where is my order 89782837?
  Assistant > ...please verify your identity by sharing the last 4 digits of your registered phone number or pincode...
  Customer > 2837
  Assistant > Thank you, Kabir! Your identity has been verified...
  ```
- **Talking Point:** "Low-confidence or unindexed requests trigger principled abstention. Order queries enforce strict identity verification before disclosing sensitive details."

---

### 1:30 - 2:00: Scene 4 — Batch Audio Processing with Gnani.ai
- **Action:** Run the batch audio command:
  ```bash
  python3 run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/audio_batch_results
  ```
- **Show Output:**
  - View `sample_outputs/audio_batch_results/batch_summary.json` showing 3/3 audio files processed.
  - Play back `sample_outputs/audio_batch_results/sample_order_status_reply.wav`.
  - Highlight Gnani configuration: Voice `Kaveri`, Model `timbre-v2.5`, Language `en-IN`.
- **Status:** Offline synthetic WAV generated when live `GNANI_API_KEY` is not present; seamlessly connects to live Gnani API when key is configured.
