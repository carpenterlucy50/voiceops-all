"""
Step 4 Multilingual Voice-First Adapter for PERSON 5.

Strict Genuine Gnani Integration:
- Uses official SDK (gnani-vachana):
    from gnani.stt import GnaniSTTClient
    from gnani.tts import GnaniTTSClient
- Reads GNANI_API_KEY from environment.
- Transcribes customer audio using Gnani STT with Indian language code support (e.g. en-IN, hi-IN).
- Applies SpeechNormalizer to shape responses for the ear (grouped order numbers, spoken currencies, dates).
- Synthesizes assistant reply using Gnani TTS (voice='Kaveri', model='timbre-v2.5').
- Handles empty/unclear speech using multilingual recovery prompts.
- No offline mock speech processor or mock responses as runtime fallback.
- If credentials are not configured, reports 'BLOCKED — credentials not configured'.
"""
import os
import json
from typing import Dict, Any, List, Optional, Tuple
def _load_env_file():
    cur = os.path.dirname(os.path.abspath(__file__))
    for _ in range(3):
        cand = os.path.join(cur, ".env")
        if os.path.isfile(cand):
            try:
                with open(cand, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception:
                pass
            break
        cur = os.path.dirname(cur)

_load_env_file()

from .conversation_agent import ConversationAgent
from .speech_normalizer import SpeechNormalizer


class MultilingualVoiceAdapter:
    def __init__(
        self,
        agent: ConversationAgent,
        api_key: Optional[str] = None,
        stt_client: Optional[Any] = None,
        tts_client: Optional[Any] = None
    ):
        self.agent = agent
        self.api_key = api_key or os.environ.get('GNANI_API_KEY')
        self.tts_model = os.environ.get('GNANI_TTS_MODEL', 'timbre-v2.5')
        self.tts_voice = os.environ.get('GNANI_TTS_VOICE', 'Kaveri')
        self.language_code = os.environ.get('GNANI_LANGUAGE_CODE', 'en-IN')

        self.stt_client = stt_client
        self.tts_client = tts_client
        self.is_live = False

        if self.stt_client and self.tts_client:
            self.is_live = True
        elif self.api_key:
            try:
                from gnani.stt import GnaniSTTClient
                from gnani.tts import GnaniTTSClient
                self.stt_client = GnaniSTTClient(api_key=self.api_key)
                self.tts_client = GnaniTTSClient(api_key=self.api_key)
                self.is_live = True
            except Exception as e:
                self.init_error = str(e)
        else:
            self.init_error = "GNANI_API_KEY environment variable is not configured."

    def transcribe(self, audio_path: str, lang_code: Optional[str] = None) -> Tuple[str, str]:
        """Transcribe audio file strictly via Gnani STT in the specified Indian language."""
        code = lang_code or self.language_code
        if not self.is_live or not self.stt_client:
            return "", "BLOCKED — credentials not configured"

        try:
            res = self.stt_client.transcribe(audio_path, language_code=code)
            transcript = res.get('transcript', '').strip() if isinstance(res, dict) else str(res).strip()
            return transcript, "live_gnani_stt"
        except Exception as e:
            return "", f"gnani_stt_error: {str(e)}"

    def synthesize(self, text: str, output_path: str, lang_code: Optional[str] = None) -> str:
        """
        Synthesize text to speech audio strictly via Gnani TTS,
        after applying SpeechNormalizer for ear-targeted speech.
        """
        code = lang_code or self.language_code
        if not self.is_live or not self.tts_client:
            return "BLOCKED — credentials not configured"

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # Apply speech normalization for the ear
        spoken_text = SpeechNormalizer.normalize_for_tts(text, code)

        try:
            res = self.tts_client.synthesize(
                spoken_text,
                voice=self.tts_voice,
                model=self.tts_model,
                language=code,
                output_file=output_path
            )
            if isinstance(res, bytes) and not os.path.exists(output_path):
                with open(output_path, "wb") as f:
                    f.write(res)
            return "live_gnani_tts"
        except Exception as e:
            return f"gnani_tts_error: {str(e)}"

    def process_voice_turn(self, audio_path: str, conv_id: str = "voice_session", lang_code: Optional[str] = None) -> Dict[str, Any]:
        """Process one voice turn end-to-end with multilingual speech normalization."""
        code = lang_code or self.language_code
        if not self.is_live:
            return {
                'audio_input': audio_path,
                'status': 'BLOCKED — credentials not configured',
                'error': 'GNANI_API_KEY is not set in environment. Live Gnani services required.',
                'transcription': '',
                'reply_text': '',
                'reply_audio': None,
                'stt_status': 'BLOCKED — credentials not configured',
                'tts_status': 'BLOCKED — credentials not configured'
            }

        transcript, stt_status = self.transcribe(audio_path, code)

        if not transcript.strip():
            recovery_prompt = SpeechNormalizer.get_unclear_recovery_prompt(code)
            out_audio = os.path.splitext(audio_path)[0] + "_reply.wav"
            tts_status = self.synthesize(recovery_prompt, out_audio, code)
            return {
                'audio_input': audio_path,
                'transcription': '',
                'reply_text': recovery_prompt,
                'reply_audio': out_audio if os.path.exists(out_audio) else None,
                'stt_status': stt_status,
                'tts_status': tts_status,
                'evidence': [],
                'tool_calls': [],
                'status': 'empty_transcription_recovered'
            }

        turn_res = self.agent.process_turn(conv_id, transcript)
        reply_text = turn_res['response']
        out_audio = os.path.splitext(audio_path)[0] + "_reply.wav"
        tts_status = self.synthesize(reply_text, out_audio, code)

        return {
            'audio_input': audio_path,
            'transcription': transcript,
            'reply_text': reply_text,
            'reply_audio': out_audio if os.path.exists(out_audio) else None,
            'decision': turn_res.get('decision', 'answer'),
            'evidence': turn_res.get('evidence', []),
            'tool_calls': turn_res.get('tool_calls', []),
            'stt_status': stt_status,
            'tts_status': tts_status,
            'status': 'success' if tts_status == "live_gnani_tts" else "tts_failed"
        }

    def process_batch(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Batch process audio files using genuine Gnani STT & TTS."""
        os.makedirs(output_dir, exist_ok=True)
        supported_exts = ('.wav', '.mp3', '.ogg', '.m4a', '.flac')

        if not os.path.exists(input_dir):
            return {
                'total_files': 0,
                'successful': 0,
                'failed': 1,
                'errors': [f"Input dir {input_dir} does not exist"],
                'live_gnani': self.is_live,
                'records': []
            }

        files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(supported_exts)])

        if not self.is_live:
            summary = {
                'total_files': len(files),
                'successful': 0,
                'failed': len(files),
                'status': 'BLOCKED — credentials not configured',
                'error': 'GNANI_API_KEY is not configured in environment. Genuine speech services required.',
                'live_gnani': False,
                'records': []
            }
            summary_path = os.path.join(output_dir, 'batch_processing_summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            return summary

        results = []
        errors = []

        for fname in files:
            in_file = os.path.join(input_dir, fname)
            out_wav = os.path.join(output_dir, f"{os.path.splitext(fname)[0]}_reply.wav")
            try:
                transcript, stt_status = self.transcribe(in_file, self.language_code)
                if not transcript.strip():
                    recovery_prompt = SpeechNormalizer.get_unclear_recovery_prompt(self.language_code)
                    tts_status = self.synthesize(recovery_prompt, out_wav, self.language_code)
                    item_res = {
                        'filename': fname,
                        'transcription': transcript,
                        'response_text': recovery_prompt,
                        'audio_reply': out_wav if os.path.exists(out_wav) else None,
                        'retrieved_sections': [],
                        'tool_calls': [],
                        'status': 'empty_transcription_recovered',
                        'stt_status': stt_status,
                        'tts_status': tts_status
                    }
                else:
                    turn_res = self.agent.process_turn(f"batch_{fname}", transcript)
                    reply_text = turn_res['response']
                    tts_status = self.synthesize(reply_text, out_wav, self.language_code)
                    item_res = {
                        'filename': fname,
                        'transcription': transcript,
                        'response_text': reply_text,
                        'audio_reply': out_wav if os.path.exists(out_wav) else None,
                        'retrieved_sections': turn_res.get('evidence', []),
                        'tool_calls': turn_res.get('tool_calls', []),
                        'status': 'success' if tts_status == "live_gnani_tts" else "tts_failed",
                        'stt_status': stt_status,
                        'tts_status': tts_status
                    }
                results.append(item_res)
            except Exception as e:
                errors.append(f"{fname}: {str(e)}")
                results.append({'filename': fname, 'status': 'error', 'error': str(e)})

        summary = {
            'total_files': len(files),
            'successful': sum(1 for r in results if r.get('status') in ('success', 'empty_transcription_recovered')),
            'failed': len(errors) + sum(1 for r in results if r.get('status') in ('error', 'tts_failed')),
            'live_gnani': self.is_live,
            'records': results
        }

        summary_path = os.path.join(output_dir, 'batch_processing_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        return summary
