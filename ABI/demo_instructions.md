# 2-Minute Live Demo Instructions — PERSON 5
## VoiceOps 2026: Multilingual Voice-First Support Agent

Demonstrates voice-first interactions, Gnani STT/TTS integration, speech normalization for the ear, and acoustic error recovery.

---

## Demo Script (Timeline: 120 Seconds)

### Scene 1: Phonetic Speech Input & Spoken Normalization (0:00 – 0:35)
1. Run a voice query or submit audio:
   > *"uh sku ele-zero zero zero to pe zentromart assured hai kya claim kaise karein"*
2. Assistant replies with speech-optimized phrasing:
   > *"Haan, SKU ELE-0002 pe 12 mahine ki ZentroMart Assured warranty hai; claim app mein My Orders se karein."*
3. Highlight:
   - ASR phonetic normalizer mapped "ele-zero zero zero to" directly to `ELE-0002`.
   - Spoken response formats dates and codes cleanly for the ear.

---

### Scene 2: Acoustic Error Recovery (0:35 – 1:00)
1. Simulate silent or background noise audio:
   ```bash
   python run.py --input-dir sample_outputs/test_audio --output-dir sample_outputs/batch_audio_results
   ```
2. When empty or unclear transcription is received, show the assistant politely recovering:
   > *"Sorry, I didn't catch that. Could you please say it again?"*
   (Or in Hindi: *"माफ़ कीजिए, मैं आपकी आवाज़ ठीक से नहीं सुन पाई। क्या आप कृपया दोबारा बोल सकते हैं?"*)

---

### Scene 3: Spoken Multi-Turn Verification (1:00 – 1:35)
1. Caller states:
   > *"Order number hai 8978 2837."*
2. Assistant verifies:
   > *"Thank you for sharing order 8 9 7 8, 2 8 3 7. To verify your identity, please provide the last 4 digits of your registered phone number or your 6-digit delivery pincode."*
3. Caller provides proof:
   > *"Last four digits 4533 hain."*
4. Assistant verifies and unlocks the session.

---

### Scene 4: Gnani Audio Batch Generation (1:35 – 2:00)
1. Inspect the synthesized reply WAV files in `sample_outputs/batch_audio_results/`.
2. Play `wallet_refund_inquiry_reply.wav` and `tv_damage_escalation_reply.wav`.
3. Review `batch_processing_summary.json` showing complete telemetry.
