"""
Domain Guardrail Module - Strict Domain Restriction
This module ensures the chatbot ONLY answers questions related to:
- Government schemes for persons with disabilities in India
- Welfare services, certificates, pensions, scholarships
- Assistive devices, employment & skill schemes
- Portals and helplines

Uses semantic similarity with a domain embedding to detect out-of-domain questions.
"""

from embeddings import encode_text, compute_cosine_similarity

# Domain embedding - represents the disability schemes domain
# This is a reference embedding that captures the domain semantics
DOMAIN_REFERENCE_TEXT = (
    "Government schemes for persons with disabilities divyangjan in India including "
    "welfare services certificates pensions retirement schemes scholarships assistive devices "
    "employment skill schemes portals helplines deadline application deadline last date "
    "financial aid support rights act unique disability id card udid railway concession"
)

# Pre-compute domain embedding (computed once at module load)
_domain_embedding = None

# Similarity threshold for domain validation
# Questions below this threshold are considered out-of-domain
# Lowered slightly to handle "retirement schemes" and similar queries
DOMAIN_SIMILARITY_THRESHOLD = 0.40


def _get_domain_embedding():
    """Get or compute the domain reference embedding."""
    global _domain_embedding
    if _domain_embedding is None:
        _domain_embedding = encode_text(DOMAIN_REFERENCE_TEXT)
    return _domain_embedding


def is_domain_related(query: str) -> bool:
    """
    Check if a query is related to the disability schemes domain using semantic similarity.
    
    Uses embedding-based similarity comparison instead of keyword matching.
    Also handles special cases like "retirement schemes" which should map to pension schemes.
    
    Args:
        query: User's query string
    
    Returns:
        True if query is domain-related (similarity >= threshold), False otherwise
    """
    query_lower = query.lower()
    
    # Quick check: if query mentions "disabled", "disability", "scheme", "pension", "retirement", it's likely domain-related
    domain_keywords = ['disabled', 'disability', 'divyang', 'scheme', 'pension', 'retirement', 'retire', 
                       'scholarship', 'assistive', 'benefit', 'certificate', 'welfare', 'support', 'fund', 
                       'money', 'job', 'card', 'udid', 'apply', 'application', 'status', 'rights', 'act', 'rule',
                       'government', 'govt', 'aid', 'grant', 'allowance', 'loan', 'subsidy', 'help', 'financial',
                       'minister', 'ministry', 'contact', 'who']
                       
    if any(keyword in query_lower for keyword in domain_keywords):
        # Encode the user query
        query_embedding = encode_text(query)
        
        # Get domain reference embedding
        domain_embedding = _get_domain_embedding()
        
        # Compute cosine similarity
        similarity = compute_cosine_similarity(query_embedding, domain_embedding)
        
        # For queries with domain keywords, use significantly lower threshold
        # We want to trust the keyword match but still filter out complete nonsense
        effective_threshold = 0.20
        
        # Return True if similarity meets threshold
        return similarity >= effective_threshold
    
    # For queries without obvious keywords, use standard threshold
    query_embedding = encode_text(query)
    domain_embedding = _get_domain_embedding()
    similarity = compute_cosine_similarity(query_embedding, domain_embedding)
    
    # Lowered standard threshold effectively to catch fuzzy conceptual matches
    return similarity >= 0.26


def get_rejection_message() -> str:
    """
    Return the EXACT rejection message for out-of-domain questions.
    This message must NEVER be modified.
    """
    return "I can help only with government schemes and services for persons with disabilities. Please ask a related question."
