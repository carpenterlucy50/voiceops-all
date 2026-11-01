# 2-Minute Live Demo Instructions — PERSON 4
## VoiceOps 2026: Policy-Aware Structured Decision Agent

Demonstrates state machine transitions, intent-driven policy routing, high-value damage escalation, and Gnani voice.

---

## Demo Script (Timeline: 120 Seconds)

### Scene 1: Structured Intent Routing & Precedence (0:00 – 0:35)
1. Run a practice question:
   > *"credit card wala refund 17 October 2026 ko shuru hua, kab tak aa jaana chahiye?"*
2. Assistant replies:
   > *"Card refunds take 5 to 7 business days. Counting from 17 October 2026, skipping Sundays and warehouse holidays (19 October), your refund should arrive between 24 October 2026 and 27 October 2026."*
3. Highlight:
   - Evaluates business-day calendars skipping the 19 October warehouse holiday.
   - Grounded in `[REF-2]` and `[KB-00.3]`.

---

### Scene 2: FSM Identity Verification & Transition (0:35 – 1:05)
1. Customer writes:
   > *"Hello, mujhe order ke baare mein help chahiye."*
2. FSM enters `START` -> prompts for order ID.
3. Customer provides:
   > *"Order number hai 8978 2837."*
4. FSM transitions to `AWAITING_VERIFICATION` -> executes `lookup_order` (unverified) -> requests phone suffix or delivery pincode.
5. Customer responds:
   > *"Last four digits 4533 hain."*
6. FSM validates proof -> transitions to `VERIFIED` -> greets customer by first name ('Kabir').

---

### Scene 3: High-Value Escalation Guardrail (1:05 – 1:35)
1. Customer asks:
   > *"Maine Zentro Vista 43-inch 4K Smart TV damage report kiya tha. Abhi replacement approve kar do na?"*
2. Assistant checks TV value (> ₹10,000 threshold under `DWM-3`).
3. Refuses to approve replacement directly, executes `create_ticket()`, logs the ticket, and confirms escalation only after `created=True`.

---

### Scene 4: Gnani Audio Batch Runner (1:35 – 2:00)
1. Execute batch processing:
   ```bash
   python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results
   ```
2. Verify `batch_processing_summary.json` showing 100% success rate and generated speech replies.
