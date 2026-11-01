import os
import re
import csv
"""Step 2: Retrieval-Augmented Generation Agent for PERSON 1.

Retrieves sections using BM25, enriches with product catalog info, strictly enforces KB precedence,
and tracks retrieved evidence IDs.
"""
from typing import Dict, Any, List, Optional
from .knowledge_base import KnowledgeBase
from .retriever import LexicalRetriever
from .llm_adapter import LLMAdapter

RAG_SYSTEM_PROMPT = """You are an AI customer support assistant for ZentroMart, an Indian online shopping store.
Always identify yourself as an AI assistant.
Answer customer queries strictly based on the provided document excerpts and catalog data.
Follow these official knowledge base rules:
1. When documents conflict, policy documents with status 'current' win over agent guides, help articles, and FAQs.
2. Superseded documents apply ONLY to cases their successor document says they still cover (e.g. electronics delivered before 1 August 2026).
3. If the provided documents do not contain information to answer the question, clearly state that you do not have this information and offer to connect the customer to a human colleague. Never invent a policy, fee, date, or timeline.
4. Keep answers concise, clear, and professional.
"""


class RAGAgent:
    def __init__(self, kb: KnowledgeBase, retriever: LexicalRetriever = None, llm: LLMAdapter = None):
        self.kb = kb
        self.retriever = retriever or LexicalRetriever(kb)
        self.llm = llm or LLMAdapter()

    def answer_question(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Grounded answer generation with evidence retrieval and tracking."""
        # Check product catalog lookup
        prod = self.kb.find_product(question)
        prod_context = ""
        evidence_records: List[str] = []

        if prod:
            prod_context = (
                f"Catalog Data: SKU={prod.sku}, Name='{prod.name}', Category={prod.category}, "
                f"ReturnCategory={prod.return_category}, Price=₹{prod.price_inr}, "
                f"WarrantyMonths={prod.warranty_months}, Assured={prod.is_assured}\n"
            )
            evidence_records.append(f"products.csv:{prod.sku}")

        # Retrieve relevant sections
        scored_sections = self.retriever.retrieve(question, top_k=top_k)
        retrieved_ids = [sec.section_id for sec, _ in scored_sections]
        evidence_records.extend(retrieved_ids)

        # Build context from retrieved sections
        context_parts = []
        if prod_context:
            context_parts.append(prod_context)

        for sec, score in scored_sections:
            context_parts.append(f"[{sec.section_id}] {sec.heading} ({sec.doc_type}, {sec.doc_status}):\n{sec.content}")

        context_str = "\n\n".join(context_parts)

        # Generate grounded response
        response, source = self.llm.generate(
            prompt=question,
            system_prompt=RAG_SYSTEM_PROMPT,
            context=context_str
        )

        # Determine decision type (answer vs clarify vs escalate)
        decision = "answer"
        if ("kitne din" in question.lower() or "how many days" in question.lower()) and len(question.split()) < 7:
            decision = "clarify"
        elif "colleague" in response.lower() or "connect" in response.lower() or "don't have" in response.lower():
            decision = "answer"


        return {
            'question': question,
            'response': response,
            'retrieved_sections': retrieved_ids,
            'evidence_records': evidence_records,
            'decision': decision,
            'source': source,
            'has_retrieval': True,
            'context': context_str
        }

