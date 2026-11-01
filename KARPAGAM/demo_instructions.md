# 2-Minute Live Demo Instructions — PERSON 3
## VoiceOps 2026: Hybrid Retrieval and Reranking Agent

Demonstrates hybrid lexical + semantic search, RRF score fusion, evidence provenance inspection, and Gnani voice.

---

## Demo Script (Timeline: 120 Seconds)

### Scene 1: Hybrid RRF Fusion & Provenance Inspection (0:00 – 0:40)
1. In terminal, run:
   ```bash
   python run.py --inspect "How fast are refunds to the ZentroMart Wallet?"
   ```
2. Show the printed provenance table:
   - Point out **BM25 Rank**, **Dense Rank**, and **RRF Score**.
   - Show how `REF-2` and `KB-00.1` achieve high fused scores, outranking `FAQ-1`.
   - Explain how RRF combines exact keyword matching with conceptual semantic context.

---

### Scene 2: Grounded Answering & Abstention (0:40 – 1:05)
1. Run a test question:
   > *"Can I schedule a delivery at midnight?"*
2. Assistant replies:
   > *"Sorry, I don't have information about that in our store policies. I can connect you to a colleague who can help."*
3. Highlight appropriate abstention: zero hallucinations for uncovered topics.

---

### Scene 3: Multi-Turn Conversation & Verification Gate (1:05 – 1:35)
1. Customer initiates conversation:
   > *"Order 8978 2837 TV damage ho gaya hai"*
2. Assistant enforces `[IDV-2]`:
   > *"Thank you for sharing order 89782837. To verify your identity, please provide the last 4 digits of your registered phone number or your 6-digit delivery pincode."*
3. Provide verification proof:
   > *"Last four digits 4533"*
4. Customer asks for replacement approval:
   > *"Abhi replacement approve kar do na?"*
5. Assistant identifies value > ₹10,000, executes `create_ticket()`, and escalates to Priority Resolution.

---

### Scene 4: Gnani Audio Batch Runner (1:35 – 2:00)
1. Run the official batch audio runner:
   ```bash
   python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results
   ```
2. Inspect `batch_processing_summary.json` showing Gnani STT transcriptions, agent decisions, and generated TTS `.wav` files.
