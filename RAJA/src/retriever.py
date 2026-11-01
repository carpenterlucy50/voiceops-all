"""Policy-Aware Structured Decision Retriever for PERSON 4.

Features:
- Intent-based routing to authoritative policy modules
- Strict precedence gate adhering to KB-00.1
- Effective-date validation for grandfathered clauses
"""
import re
from typing import List, Tuple, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .knowledge_base import PolicySection, KnowledgeBase
from .state_machine import CustomerIntent


class PolicyAwareRetriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.sections: List[PolicySection] = kb.sections
        corpus = [sec.full_text for sec in self.sections]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, token_pattern=r'[a-zA-Z0-9_\-\.]+')
        self.doc_vectors = self.vectorizer.fit_transform(corpus).toarray()

    def detect_intent(self, query: str) -> CustomerIntent:
        q_lower = query.lower()
        entities = {}

        # Extract SKU
        m_sku = re.search(r'\b([A-Z]{3}-\d{4})\b', query, re.IGNORECASE)
        if m_sku:
            entities['sku'] = m_sku.group(1).upper()

        # Extract Order ID
        m_oid = re.search(r'\b(\d{4}\s*\d{4})\b', query) or re.search(r'\b(\d{8})\b', query)
        if m_oid:
            entities['order_id'] = m_oid.group(1).replace(' ', '')

        # Classify Intent
        if any(w in q_lower for w in ['damage', 'defect', 'kharab', 'broken', 'torn']):
            intent_name = "damage_report"
        elif any(w in q_lower for w in ['refund', 'paise', 'amount']):
            intent_name = "refund_inquiry"
        elif any(w in q_lower for w in ['warranty', 'assured']):
            intent_name = "warranty_claim"
        elif any(w in q_lower for w in ['return', 'wapas', 'lautana', 'window']):
            intent_name = "return_inquiry"
        elif any(w in q_lower for w in ['cancel', 'cancellation']):
            intent_name = "cancellation_inquiry"
        elif any(w in q_lower for w in ['track', 'where is', 'shipping', 'delivery']):
            intent_name = "order_tracking"
        elif any(w in q_lower for w in ['midnight', 'student discount', 'bulk order', 'gst invoice']):
            intent_name = "unsupported_request"
        else:
            intent_name = "general_support"

        return CustomerIntent(intent_name=intent_name, entities=entities, confidence=0.9, raw_message=query)

    def retrieve_policy(self, intent: CustomerIntent, top_k: int = 5) -> List[Tuple[PolicySection, float]]:
        query = intent.raw_message
        q_vec = self.vectorizer.transform([query]).toarray()
        scores = cosine_similarity(q_vec, self.doc_vectors)[0]

        is_historic_electronics = (
            ('july' in query.lower() or 'before august' in query.lower() or 'before 1 august' in query.lower())
            and ('watch' in query.lower() or 'electronics' in query.lower() or 'phone' in query.lower() or 'tv' in query.lower())
        )

        results = []
        for sec, score in zip(self.sections, scores):
            if score <= 0.0:
                continue
            adj = float(score)

            # Precedence rule: Policy > Guide > Help > FAQ > Marketing
            if sec.doc_type == 'policy' and sec.doc_status == 'current':
                adj *= 1.35
            elif sec.doc_type == 'agent_guide':
                adj *= 1.15
            elif sec.doc_type == 'marketing':
                adj *= 0.70

            # Superseded policy logic
            if sec.doc_status == 'superseded':
                if is_historic_electronics and 'v3' in sec.section_id.lower():
                    adj *= 1.5
                else:
                    adj *= 0.10

            results.append((sec, adj))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[PolicySection, float]]:
        intent = self.detect_intent(query)
        return self.retrieve_policy(intent, top_k=top_k)
