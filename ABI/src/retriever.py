"""Multilingual Voice Retriever for PERSON 5.

Features:
- Handles phonetic ASR transcriptions and word-form numbers ('zero zero one two' -> '0012')
- Multilingual query matching for English, Hindi, and Hinglish
- Enforces official KB-00.1 precedence rules
"""
import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from .knowledge_base import VoiceSection, KnowledgeBase

WORD_TO_DIGIT = {
    'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
    'ek': '1', 'do': '2', 'teen': '3', 'char': '4', 'paanch': '5',
    'cheh': '6', 'saat': '7', 'aath': '8', 'nau': '9', 'shunya': '0'
}


class MultilingualVoiceRetriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.sections: List[VoiceSection] = kb.sections
        self.corpus_tokens = [self._tokenize(sec.full_text) for sec in self.sections]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def _normalize_asr_query(self, text: str) -> str:
        """Convert spelled out ASR numbers to digits."""
        # Replace hyphens with spaces so ele-zero becomes ele zero
        norm_text = text.lower().replace('-', ' ')
        words = norm_text.split()
        norm_words = []
        for w in words:
            clean_w = re.sub(r'[^a-z]', '', w)
            if clean_w in WORD_TO_DIGIT:
                norm_words.append(WORD_TO_DIGIT[clean_w])
            else:
                norm_words.append(w)
        joined = " ".join(norm_words)
        # join adjacent digits: '0 0 1 2' -> '0012'
        joined = re.sub(r'(?<=\d)\s+(?=\d)', '', joined)
        return joined

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'[a-zA-Z0-9_\-\.]+', text.lower())

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[VoiceSection, float]]:
        cleaned_query = self._normalize_asr_query(query)
        q_tokens = self._tokenize(cleaned_query)
        if not q_tokens:
            return []

        scores = self.bm25.get_scores(q_tokens)

        is_historic_electronics = (
            ('july' in cleaned_query.lower() or 'before august' in cleaned_query.lower() or 'before 1 august' in cleaned_query.lower())
            and ('watch' in cleaned_query.lower() or 'electronics' in cleaned_query.lower() or 'phone' in cleaned_query.lower() or 'tv' in cleaned_query.lower())
        )

        results = []
        for sec, score in zip(self.sections, scores):
            if score <= 0.0:
                continue
            adj = float(score)

            if sec.doc_status == 'superseded':
                if is_historic_electronics and 'v3' in sec.section_id.lower():
                    adj *= 1.5
                else:
                    adj *= 0.10

            if sec.doc_type == 'policy' and sec.doc_status == 'current':
                adj *= 1.3
            elif sec.doc_type == 'agent_guide':
                adj *= 1.15
            elif sec.doc_type == 'marketing':
                adj *= 0.70

            results.append((sec, adj))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
