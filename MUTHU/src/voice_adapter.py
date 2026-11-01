"""
Step 4 Gnani Voice Adapter for PERSON 6 (Evaluation-Driven Adaptive RAG Agent).

Strict Genuine Gnani Integration:
- Uses official SDK (gnani-vachana):
    from gnani.stt import GnaniSTTClient
    from gnani.tts import GnaniTTSClient
- Reads GNANI_API_KEY from environment.
- Transcribes customer audio using Gnani STT.
- Routes transcript through the actual Step 3 ConversationAgent with adaptive retrieval tracing.
- Synthesizes assistant reply using Gnani TTS (voice='Kaveri', model='timbre-v2.5', language='en-IN').
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


class GnaniVoiceAdapter:
    def __init__(
        self,
        conversation_agent: ConversationAgent,
        api_key: Optional[str] = None,
        stt_client: Optional[Any] = None,
        tts_client: Optional[Any] = None
    ):
        self.agent = conversation_agent
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

    def speech_to_text(self, audio_path: str) -> Tuple[str, str]:
        """Transcribe audio file strictly via Gnani STT."""
        if not self.is_live or not self.stt_client:
            return "", "BLOCKED — credentials not configured"

        try:
            res = self.stt_client.transcribe(audio_path, language_code=self.language_code)
            transcript = res.get('transcript', '').strip() if isinstance(res, dict) else str(res).strip()
            return transcript, "live_gnani_stt"
        except Exception as e:
            return "", f"gnani_stt_error: {str(e)}"

    def text_to_speech(self, text: str, output_path: str) -> str:
        """Synthesize text to speech audio strictly via Gnani TTS."""
        if not self.is_live or not self.tts_client:
            return "BLOCKED — credentials not configured"

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        try:
            res = self.tts_client.synthesize(
                text,
                voice=self.tts_voice,
                model=self.tts_model,
                language=self.language_code,
                output_file=output_path
            )
            if isinstance(res, bytes) and not os.path.exists(output_path):
                with open(output_path, "wb") as f:
                    f.write(res)
            return "live_gnani_tts"
        except Exception as e:
            return f"gnani_tts_error: {str(e)}"

    def process_audio_file(self, audio_path: str, output_dir: str) -> Dict[str, Any]:
        """Process one audio file end-to-end through Gnani STT -> Adaptive Agent -> Gnani TTS."""
        filename = os.path.basename(audio_path)
        base_name, _ = os.path.splitext(filename)
        out_wav_path = os.path.join(output_dir, f"{base_name}_reply.wav")
        out_meta_path = os.path.join(output_dir, f"{base_name}_result.json")

        if not self.is_live:
            record = {
                "original_audio": filename,
                "status": "BLOCKED — credentials not configured",
                "error": "GNANI_API_KEY is not set in environment. Live Gnani services required.",
                "transcription": "",
                "response_text": "",
                "response_audio": None,
                "stt_status": "BLOCKED — credentials not configured",
                "tts_status": "BLOCKED — credentials not configured"
            }
            with open(out_meta_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            return record

        transcript, stt_status = self.speech_to_text(audio_path)

        if not transcript.strip():
            reply_text = "Sorry, I didn't catch that. Could you say it again?"
            tts_status = self.text_to_speech(reply_text, out_wav_path)
            record = {
                "original_audio": filename,
                "transcription": "",
                "response_text": reply_text,
                "response_audio": f"{base_name}_reply.wav" if os.path.exists(out_wav_path) else None,
                "stt_status": stt_status,
                "tts_status": tts_status,
                "retrieved_evidence": [],
                "status": "empty_transcription_recovered"
            }
            with open(out_meta_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            return record

        agent_result = self.agent.process_turn(f"batch_{base_name}", transcript)
        response_text = agent_result.get("response", "")
        tts_status = self.text_to_speech(response_text, out_wav_path)

        result_record = {
            "original_audio": filename,
            "transcription": transcript,
            "response_text": response_text,
            "response_audio": f"{base_name}_reply.wav" if os.path.exists(out_wav_path) else None,
            "tts_status": tts_status,
            "stt_status": stt_status,
            "gnani_config": {
                "voice": self.tts_voice,
                "model": self.tts_model,
                "language": self.language_code,
                "live_api": self.is_live
            },
            "decision": agent_result.get("decision"),
            "order_id": agent_result.get("order_id"),
            "retrieved_evidence": agent_result.get("evidence", []),
            "status": "success" if tts_status == "live_gnani_tts" else "tts_failed"
        }

        with open(out_meta_path, "w", encoding="utf-8") as f:
            json.dump(result_record, f, indent=2)

        return result_record

    def process_batch(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Batch process audio files using genuine Gnani STT & TTS."""
        os.makedirs(output_dir, exist_ok=True)
        supported_exts = ('.wav', '.mp3', '.ogg', '.m4a', '.flac')

        if not os.path.exists(input_dir):
            return {
                "total_files": 0,
                "successful": 0,
                "failed": 1,
                "errors": [f"Input dir {input_dir} does not exist"],
                "live_gnani": self.is_live,
                "records": []
            }

        audio_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(supported_exts)])

        if not self.is_live:
            summary = {
                "total_files": len(audio_files),
                "successful": 0,
                "failed": len(audio_files),
                "status": "BLOCKED — credentials not configured",
                "error": "GNANI_API_KEY is not configured in environment. Genuine speech services required.",
                "live_gnani": False,
                "records": []
            }
            summary_path = os.path.join(output_dir, "batch_processing_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            return summary

        results = []
        errors = []

        for f in audio_files:
            file_path = os.path.join(input_dir, f)
            try:
                rec = self.process_audio_file(file_path, output_dir)
                results.append(rec)
            except Exception as e:
                errors.append(f"{f}: {str(e)}")
                results.append({"original_audio": f, "error": str(e), "status": "error"})

        summary = {
            "total_files": len(audio_files),
            "successful": sum(1 for r in results if r.get("status") in ("success", "empty_transcription_recovered")),
            "failed": len(errors) + sum(1 for r in results if r.get("status") in ("error", "tts_failed")),
            "live_gnani": self.is_live,
            "records": results
        }

        with open(os.path.join(output_dir, "batch_processing_summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary
