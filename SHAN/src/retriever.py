"""BM25 Lexical Retrieval Engine for PERSON 1.

Implements pure lexical retrieval with BM25Okapi:
- Section-aware chunking preserving [SECTION-ID]
- Document precedence integration (KB-00: Policy > Guide > Help > FAQ > Marketing)
- Query tokenization with support for English, Hindi, Hinglish, and SKU patterns
"""
import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from .knowledge_base import DocumentSection, KnowledgeBase


class LexicalRetriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.sections: List[DocumentSection] = kb.sections
        self.corpus_tokens: List[List[str]] = [self._tokenize(sec.full_text) for sec in self.sections]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def _tokenize(self, text: str) -> List[str]:
        # Clean and tokenize words, keeping alphanumeric and hyphens (like ELE-0012, RET-2)
        text = text.lower()
        tokens = re.findall(r'[a-z0-9\-\.]+', text)
        return tokens

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentSection, float]]:
        """Retrieve top_k matching sections with BM25 scores and precedence adjustments."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        scored_sections = []

        is_historic_electronics = (
            ('july' in query.lower() or 'before august' in query.lower() or 'before 1 august' in query.lower())
            and ('watch' in query.lower() or 'electronics' in query.lower() or 'phone' in query.lower() or 'tv' in query.lower())
        )

        for sec, score in zip(self.sections, scores):
            if score <= 0.0:
                continue

            # Precedence rule: Penalize superseded documents UNLESS historic electronics query
            adjusted_score = float(score)
            if sec.doc_status == 'superseded':
                if is_historic_electronics and 'v3' in sec.section_id.lower():
                    adjusted_score *= 1.5  # Relevant for pre-August 2026 electronics
                else:
                    adjusted_score *= 0.1  # Heavy penalty for superseded docs

            # Boost Policy and Agent Guide documents over FAQ / Marketing per KB-00.1
            if sec.doc_type == 'policy' and sec.doc_status == 'current':
                adjusted_score *= 1.25
            elif sec.doc_type == 'agent_guide':
                adjusted_score *= 1.15
            elif sec.doc_type == 'marketing':
                adjusted_score *= 0.75

            scored_sections.append((sec, adjusted_score))

        # Sort by adjusted score descending
        scored_sections.sort(key=lambda x: x[1], reverse=True)
        return scored_sections[:top_k]
