"""
Unit and Integration Tests for PERSON 6 — Adaptive RAG Agent
"""

import os
import unittest
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
p6_dir = os.path.abspath(os.path.join(cur_dir, ".."))
if p6_dir not in sys.path:
    sys.path.insert(0, p6_dir)

from src.knowledge_base import KnowledgeBase
from src.retriever import AdaptiveRetriever
from src.tools_adapter import ToolsAdapter
from src.llm_adapter import LLMAdapter
from src.baseline import BaselineAgent
from src.rag_agent import AdaptiveRAGAgent
from src.conversation_agent import ConversationAgent
from src.voice_adapter import GnaniVoiceAdapter

class TestPerson6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_dir = os.path.join(p6_dir, "Capstone_Project_Dataset_FTTT_2026")
        cls.kb = KnowledgeBase(cls.dataset_dir)
        cls.retriever = AdaptiveRetriever(cls.kb)
        cls.tools = ToolsAdapter(cls.dataset_dir)
        cls.llm = LLMAdapter(provider="auto")
        cls.rag_agent = AdaptiveRAGAgent(cls.retriever, cls.llm)
        cls.conv_agent = ConversationAgent(cls.retriever, cls.tools, cls.llm)
        cls.voice_adapter = GnaniVoiceAdapter(cls.conv_agent)

    def test_adaptive_routing_and_tracing(self):
        chunks, trace = self.retriever.retrieve("What is the refund timeline for wallet?", strategy="adaptive", top_k=3)
        self.assertGreater(len(chunks), 0)
        self.assertGreater(trace.latency_ms, 0)
        self.assertFalse(trace.abstained)
        self.assertIn("latency_ms", trace.to_dict())

    def test_confidence_abstention(self):
        chunks, trace = self.retriever.retrieve("xyznonexistent qwertz gibberish query 987654321")
        self.assertTrue(trace.abstained or len(chunks) == 0)

    def test_multi_turn_verification_and_ticket(self):
        self.conv_agent.reset()
        t1 = self.conv_agent.process_turn("I need an update on order 89782837")
        self.assertIn("verify", t1["response"].lower())
        self.assertFalse(t1["verified"])

        t2 = self.conv_agent.process_turn("My phone ends in 4533")
        self.assertTrue(t2["verified"])

        t3 = self.conv_agent.process_turn("My package arrived completely broken and damaged, escalate this!")
        self.assertEqual(t3["decision"], "escalate")

    def test_mocked_voice_adapter_pipeline(self):
        """[MOCKED UNIT TEST] Verify voice adapter audio processing workflow with mocked Gnani clients."""
        from unittest.mock import MagicMock
        mock_stt = MagicMock()
        mock_tts = MagicMock()
        mock_stt.transcribe.return_value = {"transcript": "What is the return window for clothing?"}
        mock_tts.synthesize.return_value = b"RIFFfakeaudio"

        voice = GnaniVoiceAdapter(self.conv_agent, stt_client=mock_stt, tts_client=mock_tts)
        self.assertTrue(voice.is_live)

        res = voice.process_audio_file("/tmp/fake_test.wav", output_dir="/tmp/test_p6_out")
        self.assertEqual(res['transcription'], "What is the return window for clothing?")
        self.assertEqual(res['stt_status'], "live_gnani_stt")
        self.assertIn("zentromart", res['response_text'].lower())
        mock_tts.synthesize.assert_called_once()

if __name__ == "__main__":
    unittest.main()
