"""Explicit Finite State Machine and Structured Decision Objects for PERSON 4."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class DialogState(Enum):
    START = "START"
    AWAITING_ORDER_ID = "AWAITING_ORDER_ID"
    AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
    VERIFIED = "VERIFIED"
    VERIFICATION_FAILED_LOCKED = "VERIFICATION_FAILED_LOCKED"
    ESCALATION_HANDOVER_COMPLETED = "ESCALATION_HANDOVER_COMPLETED"


@dataclass
class CustomerIntent:
    intent_name: str
    entities: Dict[str, Any]
    confidence: float
    raw_message: str


@dataclass
class StructuredDecision:
    decision_type: str  # answer, clarify, escalate, refuse
    intent: CustomerIntent
    target_tool: Optional[str]
    tool_arguments: Dict[str, Any]
    policy_section_ids: List[str]
    precedence_validated: bool
    requires_human_review: bool
    response_text: str
    execution_status: str = "pending"


class DialogStateMachine:
    def __init__(self, conversation_id: str, max_retries: int = 1):
        self.conversation_id = conversation_id
        self.max_retries = max_retries
        self.state: DialogState = DialogState.START
        self.order_id: Optional[str] = None
        self.verified_order_data: Optional[Dict[str, Any]] = None
        self.verification_attempts: int = 0
        self.ticket_id: Optional[str] = None
        self.history: List[Dict[str, str]] = []

    def transition(self, event: str, payload: Optional[Dict[str, Any]] = None) -> DialogState:
        """Enforces legal state transitions."""
        payload = payload or {}

        if self.state == DialogState.START:
            if event == "ORDER_ID_RECEIVED":
                self.order_id = payload.get("order_id")
                self.state = DialogState.AWAITING_VERIFICATION
            elif event == "GENERAL_QUERY":
                pass

        elif self.state == DialogState.AWAITING_VERIFICATION:
            if event == "VERIFICATION_SUCCESS":
                self.verified_order_data = payload.get("order_data")
                self.state = DialogState.VERIFIED
            elif event == "VERIFICATION_FAILED":
                self.verification_attempts += 1
                if self.verification_attempts > self.max_retries:
                    self.state = DialogState.VERIFICATION_FAILED_LOCKED

        elif self.state == DialogState.VERIFIED:
            if event == "ESCALATE_TICKET":
                self.ticket_id = payload.get("ticket_id")
                self.state = DialogState.ESCALATION_HANDOVER_COMPLETED

        return self.state
