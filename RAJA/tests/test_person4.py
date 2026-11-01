"""Automated Test Suite for PERSON 4 (Policy-Aware Structured Decision Agent)."""
import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase
from src.retriever import PolicyAwareRetriever
from src.tools_adapter import ToolsAdapter
from src.conversation_agent import ConversationAgent
from src.state_machine import DialogStateMachine, DialogState


class TestPerson4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.ds_dir = os.path.join(base_dir, 'Capstone_Project_Dataset_FTTT_2026')
        cls.kb = KnowledgeBase(cls.ds_dir)
        cls.retriever = PolicyAwareRetriever(cls.kb)
        cls.tools = ToolsAdapter(cls.ds_dir)
        cls.conv_agent = ConversationAgent(cls.kb, cls.tools, cls.retriever)

    def test_intent_detection(self):
        """Test structured intent and entity extraction."""
        intent = self.retriever.detect_intent("Order 8978 2837 TV damage report")
        self.assertEqual(intent.intent_name, "damage_report")
        self.assertEqual(intent.entities.get('order_id'), "89782837")

    def test_state_machine_transitions(self):
        """Test legal transitions in DialogStateMachine."""
        fsm = DialogStateMachine("test_conv_fsm", max_retries=1)
        self.assertEqual(fsm.state, DialogState.START)

        # Transition to AWAITING_VERIFICATION
        fsm.transition("ORDER_ID_RECEIVED", {"order_id": "89782837"})
        self.assertEqual(fsm.state, DialogState.AWAITING_VERIFICATION)

        # Fail attempt 1
        fsm.transition("VERIFICATION_FAILED")
        self.assertEqual(fsm.state, DialogState.AWAITING_VERIFICATION)
        self.assertEqual(fsm.verification_attempts, 1)

        # Fail attempt 2 -> Locks
        fsm.transition("VERIFICATION_FAILED")
        self.assertEqual(fsm.state, DialogState.VERIFICATION_FAILED_LOCKED)

    def test_high_value_escalation_guardrail(self):
        """Ensure claims over 10,000 INR trigger escalation."""
        res = self.conv_agent.process_turn("conv_esc", "Order number 8978 2837")
        self.assertEqual(res['decision'], "clarify")

        res_ver = self.conv_agent.process_turn("conv_esc", "Last four digits 4533")
        self.assertTrue(res_ver['verified'])

        res_dmg = self.conv_agent.process_turn("conv_esc", "Maine Zentro Vista 43-inch 4K Smart TV damage report kiya tha. Approve kar do.")
        self.assertEqual(res_dmg['decision'], "escalate")
        self.assertIn("create_ticket()", res_dmg['tool_calls'])

    def test_mocked_voice_adapter_pipeline(self):
        """[MOCKED UNIT TEST] Verify voice adapter audio processing workflow with mocked Gnani clients."""
        from unittest.mock import MagicMock
        from src.voice_adapter import GnaniVoiceAdapter
        mock_stt = MagicMock()
        mock_tts = MagicMock()
        mock_stt.transcribe.return_value = {"transcript": "Order number 8978 2837"}
        mock_tts.synthesize.return_value = b"RIFFfakeaudio"

        voice = GnaniVoiceAdapter(self.conv_agent, stt_client=mock_stt, tts_client=mock_tts)
        self.assertTrue(voice.is_live)

        res = voice.process_voice_turn("/tmp/test_voice_turn.wav", conv_id="test_mock_voice")
        self.assertEqual(res['transcription'], "Order number 8978 2837")
        self.assertEqual(res['stt_status'], "live_gnani_stt")
        self.assertIn("verification", res['reply_text'].lower())
        mock_tts.synthesize.assert_called_once()


if __name__ == '__main__':
    unittest.main()
