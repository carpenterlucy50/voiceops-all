"""Automated Test Suite for PERSON 5 (Multilingual Voice-First Agent)."""
import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase
from src.retriever import MultilingualVoiceRetriever
from src.tools_adapter import ToolsAdapter
from src.conversation_agent import ConversationAgent
from src.speech_normalizer import SpeechNormalizer
from src.voice_adapter import MultilingualVoiceAdapter


class TestPerson5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.ds_dir = os.path.join(base_dir, 'Capstone_Project_Dataset_FTTT_2026')
        cls.kb = KnowledgeBase(cls.ds_dir)
        cls.retriever = MultilingualVoiceRetriever(cls.kb)
        cls.tools = ToolsAdapter(cls.ds_dir)
        cls.conv_agent = ConversationAgent(cls.kb, cls.tools, cls.retriever)
        cls.voice = MultilingualVoiceAdapter(cls.conv_agent)

    def test_speech_normalization(self):
        """Test formatting numbers and dates for the ear."""
        formatted_oid = SpeechNormalizer.format_order_id_for_speech("89782837")
        self.assertEqual(formatted_oid, "8 9 7 8, 2 8 3 7")

        tts_norm = SpeechNormalizer.normalize_for_tts("Order 89782837 delivered on 24 October for ₹49.")
        self.assertIn("8 9 7 8, 2 8 3 7", tts_norm)
        self.assertIn("49 rupees", tts_norm)

    def test_asr_phonetic_normalization(self):
        """Test conversion of word-based ASR numbers."""
        cleaned = self.retriever._normalize_asr_query("sku ele-zero zero one two")
        self.assertIn("0012", cleaned)

    def test_multilingual_recovery_prompts(self):
        """Ensure recovery prompts are available for Indian languages."""
        hi_prompt = SpeechNormalizer.get_unclear_recovery_prompt("hi-IN")
        self.assertIn("माफ़ कीजिए", hi_prompt)

        en_prompt = SpeechNormalizer.get_unclear_recovery_prompt("en-IN")
        self.assertIn("didn't catch that", en_prompt)

    def test_mocked_voice_adapter_pipeline(self):
        """[MOCKED UNIT TEST] Verify voice adapter audio processing workflow with mocked Gnani clients."""
        from unittest.mock import MagicMock
        mock_stt = MagicMock()
        mock_tts = MagicMock()
        mock_stt.transcribe.return_value = {"transcript": "Where is my order 8978 2837?"}
        mock_tts.synthesize.return_value = b"RIFFfakeaudio"

        voice = MultilingualVoiceAdapter(self.conv_agent, stt_client=mock_stt, tts_client=mock_tts)
        self.assertTrue(voice.is_live)

        res = voice.process_voice_turn("/tmp/test_voice_turn.wav", conv_id="test_mock_voice")
        self.assertEqual(res['transcription'], "Where is my order 8978 2837?")
        self.assertEqual(res['stt_status'], "live_gnani_stt")
        self.assertIn("89782837", res['reply_text'])
        mock_tts.synthesize.assert_called_once()
        synthesized_text = mock_tts.synthesize.call_args[0][0]
        self.assertIn("8 9 7 8, 2 8 3 7", synthesized_text)

    def test_mocked_empty_audio_recovery(self):
        """[MOCKED UNIT TEST] Verify graceful recovery when audio transcription is empty."""
        from unittest.mock import MagicMock
        mock_stt = MagicMock()
        mock_tts = MagicMock()
        mock_stt.transcribe.return_value = {"transcript": ""}
        mock_tts.synthesize.return_value = b"RIFFfakeaudio"

        voice = MultilingualVoiceAdapter(self.conv_agent, stt_client=mock_stt, tts_client=mock_tts)
        turn_res = voice.process_voice_turn("/tmp/test_empty.wav", conv_id="empty_test")
        self.assertEqual(turn_res['status'], 'empty_transcription_recovered')
        self.assertIn("didn't catch that", turn_res['reply_text'])


if __name__ == '__main__':
    unittest.main()
