from typing import Dict, List, Set

import numpy as np


def precision_at_k(relevant_docs: Set[str], retrieved_docs: List[str], k: int) -> float:
    """
    Calculate precision@k: proportion of retrieved documents that are relevant.

    Args:
        relevant_docs: Set of IDs of relevant documents
        retrieved_docs: List of IDs of retrieved documents
        k: Number of documents to consider
    """
    if not retrieved_docs or k == 0:
        return 0.0

    # Consider only the top k documents
    retrieved_k = retrieved_docs[:k]
    # Count relevant documents in the top k
    relevant_retrieved = len(set(retrieved_k) & relevant_docs)

    return relevant_retrieved / k


def recall_at_k(relevant_docs: Set[str], retrieved_docs: List[str], k: int) -> float:
    """
    Calculate recall@k: proportion of relevant documents that are retrieved.

    Args:
        relevant_docs: Set of IDs of relevant documents
        retrieved_docs: List of IDs of retrieved documents
        k: Number of documents to consider
    """
    if not relevant_docs:
        return 0.0

    # Consider only the top k documents
    retrieved_k = retrieved_docs[:k]
    # Count relevant documents in the top k
    relevant_retrieved = len(set(retrieved_k) & relevant_docs)

    return relevant_retrieved / len(relevant_docs)


def mean_reciprocal_rank(relevant_docs: Set[str], retrieved_docs: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR): inverse of the rank of first relevant document.

    Args:
        relevant_docs: Set of IDs of relevant documents
        retrieved_docs: List of IDs of retrieved documents
    """
    if not retrieved_docs or not relevant_docs:
        return 0.0

    for rank, doc_id in enumerate(retrieved_docs, 1):
        if doc_id in relevant_docs:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    relevant_docs: Dict[str, int], retrieved_docs: List[str], k: int
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (nDCG) at k.

    Args:
        relevant_docs: Dict mapping doc IDs to relevance scores (0 to 3)
        retrieved_docs: List of IDs of retrieved documents
        k: Number of documents to consider
    """
    if not retrieved_docs or k == 0:
        return 0.0

    # Calculate DCG
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_docs[:k]):
        rel = relevant_docs.get(doc_id, 0)
        # Using the standard log2(i + 2) discount
        dcg += (2**rel - 1) / np.log2(i + 2)

    # Calculate ideal DCG
    ideal_docs = sorted(relevant_docs.items(), key=lambda x: x[1], reverse=True)
    idcg = 0.0
    for i, (doc_id, rel) in enumerate(ideal_docs[:k]):
        idcg += (2**rel - 1) / np.log2(i + 2)

    if idcg == 0:
        return 0.0

    return dcg / idcg
