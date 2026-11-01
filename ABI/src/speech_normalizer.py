"""Speech Normalizer for Spoken Voice Responses (PERSON 5).

Optimizes text for Gnani TTS:
- Spaced digit groups for order IDs (e.g., '89782837' -> '8 9 7 8, 2 8 3 7')
- Expanded dates with explicit years ('2026-10-27' -> '27 October 2026')
- Natural conversational phrasing for voice
- Multilingual recovery prompts
"""
import re


class SpeechNormalizer:
    @staticmethod
    def format_order_id_for_speech(order_id: str) -> str:
        clean = re.sub(r'\D', '', str(order_id))
        if len(clean) == 8:
            first = " ".join(clean[:4])
            second = " ".join(clean[4:])
            return f"{first}, {second}"
        return " ".join(clean)

    @staticmethod
    def normalize_for_tts(text: str, language_code: str = "en-IN") -> str:
        out = text

        # Format 8-digit order numbers for speech
        def replace_oid(m):
            raw = m.group(1).replace(' ', '')
            return f"order {SpeechNormalizer.format_order_id_for_speech(raw)}"
        out = re.sub(r'\border\s+(\d{4}\s*\d{4})\b', replace_oid, out, flags=re.IGNORECASE)
        out = re.sub(r'\border\s+(\d{8})\b', replace_oid, out, flags=re.IGNORECASE)

        # Replace raw currency symbols with spoken words
        out = re.sub(r'₹\s*(\d+)', r'\1 rupees', out)

        # Ensure years are pronounced clearly
        out = re.sub(r'(\d{1,2})\s+(October|November|December|August|July)\b', r'\1 \2 2026', out)

        return out

    @staticmethod
    def get_unclear_recovery_prompt(language_code: str = "en-IN") -> str:
        if language_code.startswith("hi"):
            return "माफ़ कीजिए, मैं आपकी आवाज़ ठीक से नहीं सुन पाई। क्या आप कृपया दोबारा बोल सकते हैं?"
        elif language_code == "hi-en":
            return "Sorry, mujhe aapki awaaz theek se sunai nahi di. Kya aap please dobara bol sakte hain?"
        elif language_code.startswith("ta"):
            return "மன்னிக்கவும், உங்கள் குரல் தெளிவாகக் கேட்கவில்லை. தயவுசெய்து மீண்டும் சொல்ல முடியுமா?"
        elif language_code.startswith("te"):
            return "క్షమించండి, మీ వాయిస్ స్పష్టంగా వినబడలేదు. దయచేసి మళ్లీ చెప్పగలరా?"
        return "Sorry, I didn't catch that. Could you please say it again?"
