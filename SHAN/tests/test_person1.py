"""Automated Unit and Integration Tests for PERSON 1."""
import datetime
import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase, REFERENCE_DATE
from src.retriever import LexicalRetriever
from src.baseline import BaselineAgent
from src.rag_agent import RAGAgent
from src.tools_adapter import ToolsAdapter
from src.conversation_agent import ConversationAgent
from src.voice_adapter import GnaniVoiceAdapter


class TestPerson1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.ds_dir = os.path.join(base_dir, 'Capstone_Project_Dataset_FTTT_2026')
        cls.kb = KnowledgeBase(cls.ds_dir)
        cls.retriever = LexicalRetriever(cls.kb)
        cls.tools = ToolsAdapter(cls.ds_dir)
        cls.conv_agent = ConversationAgent(cls.kb, cls.tools, cls.retriever)

    def test_section_parsing_and_ids(self):
        """Verify section headings retain official IDs like [RET-2], [DWM-1]."""
        self.assertGreater(len(self.kb.sections), 20)
        sec_ids = [s.section_id for s in self.kb.sections]
        self.assertIn("RET-2", sec_ids)
        self.assertIn("DWM-1", sec_ids)
        self.assertIn("KB-00.1", sec_ids)

    def test_precedence_and_superseded_policy(self):
        """Ensure current policy outranks superseded policy."""
        results = self.retriever.retrieve("what is the return window for electronics", top_k=5)
        ret_sections = [s.section_id for s, _ in results]
        self.assertIn("RET-2", ret_sections)
        # RETv3-2 should not beat RET-2 for general electronics queries
        v4_rank = next(i for i, (s, _) in enumerate(results) if s.section_id == "RET-2")
        v3_rank = next((i for i, (s, _) in enumerate(results) if s.section_id == "RETv3-2"), 999)
        self.assertLess(v4_rank, v3_rank)

    def test_product_catalog_lookup(self):
        """Test SKU and name resolution in product catalog."""
        prod = self.kb.find_product("Does SKU ELE-0012 have warranty?")
        self.assertIsNotNone(prod)
        self.assertEqual(prod.sku, "ELE-0012")
        self.assertTrue(prod.is_assured)
        self.assertEqual(prod.warranty_months, 12)

    def test_business_day_calculation(self):
        """Test business day math skipping Sundays and Oct 19 warehouse holiday."""
        # Start Saturday 17 October 2026
        # Sun 18 (skip), Mon 19 (holiday - skip), Tue 20 (day 1), Wed 21 (day 2), Thu 22 (day 3), Fri 23 (day 4), Sat 24 (day 5)
        start = datetime.date(2026, 10, 17)
        five_days = self.kb.calculate_business_days(start, 5)
        self.assertEqual(five_days, datetime.date(2026, 10, 24))

    def test_order_verification_gate(self):
        """Test that private order details are protected until verification."""
        # Unverified lookup
        unverified = self.tools.lookup("89782837")
        self.assertTrue(unverified.get('verification_required'))
        self.assertNotIn('items', unverified)
        self.assertNotIn('status', unverified)

        # Verified lookup with last 4 digits (4533)
        verified = self.tools.lookup("89782837", verification_value="4533")
        self.assertTrue(verified.get('verified'))
        self.assertEqual(verified.get('customer_first_name'), 'Kabir')
        self.assertIn('items', verified)

    def test_ticket_creation_escalation(self):
        """Test that ticket creation succeeds and returns ticket ID."""
        ticket_res = self.tools.ticket(
            summary="Verified customer reporting damaged high value TV over 10000 INR requiring priority resolution.",
            order_id="89782837",
            reason="high_value_damage",
            intent="damage_claim"
        )
        self.assertTrue(ticket_res.get('created'))
        self.assertTrue(ticket_res.get('ticket_id', '').startswith('TKT'))

    def test_mocked_voice_adapter_pipeline(self):
        """[MOCKED UNIT TEST] Verify voice adapter audio processing workflow with mocked Gnani clients."""
        from unittest.mock import MagicMock
        mock_stt = MagicMock()
        mock_tts = MagicMock()
        mock_stt.transcribe.return_value = {"transcript": "What is the return window for clothing?"}
        mock_tts.synthesize.return_value = b"RIFFfakeaudio"

        voice = GnaniVoiceAdapter(self.conv_agent, stt_client=mock_stt, tts_client=mock_tts)
        self.assertTrue(voice.is_live)

        res = voice.process_voice_turn("/tmp/test_voice_turn.wav", conv_id="test_mock_voice")
        self.assertEqual(res['transcription'], "What is the return window for clothing?")
        self.assertEqual(res['stt_status'], "live_gnani_stt")
        self.assertIn("zentromart", res['reply_text'].lower())
        mock_tts.synthesize.assert_called_once()


if __name__ == '__main__':
    unittest.main()
