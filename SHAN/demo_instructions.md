# 2-Minute Live Demo Instructions — PERSON 1
## VoiceOps 2026: Modular Lexical RAG Support Agent

This demo script demonstrates all four capstone pillars within 2 minutes:
1. Document-grounded policy answer with evidence tracking.
2. Context-preserving multi-turn conversation with follow-ups and identity verification.
3. Policy-driven human handover with ticket escalation.
4. Voice interaction using Gnani STT/TTS.

---

## Demo Script (Timeline: 120 Seconds)

### Scene 1: Grounded Document Question (0:00 – 0:30)
- **User Action:** In interactive mode (`python run.py --mode chat`) or via audio:
  > *"How fast are refunds to the ZentroMart Wallet?"*
- **Agent Response:**
  > *"Refunds to ZentroMart Wallet are instant, credited within 2 hours of initiation."*
- **What to Highlight:**
  - Notice the agent accurately retrieves section `[REF-2]` and avoids the trap in `[FAQ-1]` (which claims 5–7 days) because Policy outranks FAQ under `[KB-00.1]`.

---

### Scene 2: Follow-up & Identity Verification (0:30 – 1:00)
- **User Action:**
  > *"Hello, mujhe apne order ke baare mein help chahiye. Order number 8978 2837."*
- **Agent Response:**
  > *"Thank you for providing order 89782837. To protect your privacy, could you please verify your identity by sharing the last 4 digits of your registered phone number or your 6-digit delivery pincode?"*
- **User Action:**
  > *"Last four digits 4533 hain."*
- **Agent Response:**
  > *"Thank you, Kabir! Your identity has been verified. How can I assist you with order 89782837 today?"*
- **What to Highlight:**
  - Order details are strictly gated until verification succeeds.
  - Multi-turn state preserves the verified session across turns without re-asking.

---

### Scene 3: Escalation & Human Handover (1:00 – 1:30)
- **User Action:**
  > *"Maine Zentro Vista 43-inch 4K Smart TV damage report kiya tha. Abhi replacement approve kar do na?"*
- **Agent Response:**
  > *"Under ZentroMart's Damaged Items Policy (DWM-3), damage claims on items over ₹10,000 are handled directly by our Priority Resolution team. I have logged a priority ticket for you (Ticket ID: TKT...). Our specialist team will review your photos and contact you promptly."*
- **What to Highlight:**
  - Order lookup reveals item value > ₹10,000.
  - The agent refuses to improperly approve, executes `create_ticket()`, logs the ticket, and escalates politely.

---

### Scene 4: Voice Interaction with Gnani.ai (1:30 – 2:00)
- **Execution:**
  ```bash
  python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results
  ```
- **What to Show:**
  - Show the input WAV file processed by Gnani STT.
  - Play the output reply WAV file synthesized by Gnani TTS (voice: *Kaveri*, model: *timbre-v2.5*).
  - Open `batch_processing_summary.json` to show the full structured log (transcription, response text, audio path, evidence sections, and tools).
