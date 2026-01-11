"""
Validation Module - Domain Restriction for Chatbot
This module ensures the chatbot ONLY answers questions related to:
1. Government schemes
2. Disability / disabled / divyang / handicapped / specially abled (and synonyms)

Uses two-layer validation:
- Rule-based: Keyword and synonym matching
- Semantic: Sentence similarity using transformer models
"""

from sentence_transformers import SentenceTransformer, util

# Load pre-trained sentence transformer model once (efficient)
# Model: all-MiniLM-L6-v2 - lightweight and fast for semantic similarity
model = SentenceTransformer("all-MiniLM-L6-v2")

# Disability-related synonyms and variations
# These keywords help identify disability-related queries
DISABILITY_SYNONYMS = [
    "disability",
    "disabled",
    "disable",
    "divyang",  # Hindi term for persons with disabilities
    "handicapped",
    "physically challenged",
    "mentally challenged",
    "specially abled",
    "impairment",
    "blind",
    "low vision",
    "deaf",
    "hearing impairment",
    "orthopedic handicap",
    "locomotor disability",
    "intellectual disability",
    "mental illness",
    "autism",
    "cerebral palsy"
]

# Scheme-related keywords
# These keywords help identify government scheme-related queries
SCHEME_KEYWORDS = [
    "scheme",
    "schemes",
    "pension",
    "benefit",
    "allowance",
    "reservation",
    "certificate",
    "eligibility",
    "document",
    "documents",
    "application",
    "apply",
    "applying",
    "yojana",  # Hindi term for scheme
    "program",
    "plan"
]

# Allowed intent templates for semantic validation
# These represent valid question patterns the chatbot should accept
ALLOWED_INTENTS = [
    "government schemes for persons with disabilities",
    "disability pension and benefits",
    "documents required for disability schemes",
    "eligibility for disability government schemes",
    "what schemes are available for disabled persons",
    "how to apply for disability schemes",
    "how to apply for government schemes for disabled persons",
    "how to apply for disability pension",
    "what are the benefits for a person with disability",
    "which documents are needed for disability pension",
    "who is eligible for disability scholarship",
    "schemes for blind or visually impaired persons",
    "schemes for deaf or hearing impaired persons",
    "schemes for locomotor disability",
    "government help for my disabled family member",
    "process to apply for disability schemes",
    "online application process for disability schemes"
]


def rule_based_validation(question: str) -> bool:
    """
    Rule-based validation using keyword matching.
    
    Returns True if question contains
    - at least one disability synonym OR
    - at least one scheme keyword
    
    This is a fast, first-pass validation.
    
    Args:
        question: User's question string
    
    Returns:
        True if question is domain-related, False otherwise
    """
    question = question.lower()
    has_disability_keyword = any(word in question for word in DISABILITY_SYNONYMS)
    has_scheme_keyword = any(word in question for word in SCHEME_KEYWORDS)
    
    # Allow questions that are clearly about schemes OR disability.
    # Out-of-domain questions (no such keywords) will still be rejected,
    # and semantic_validation adds an extra safety layer.
    return has_disability_keyword or has_scheme_keyword


def semantic_validation(question: str) -> bool:
    """
    Semantic validation using sentence similarity.
    
    Uses transformer embeddings to check if question is semantically
    similar to allowed intent patterns.
    
    Args:
        question: User's question string
    
    Returns:
        True if semantic similarity > 0.55 threshold, False otherwise
    """
    # Encode question into embedding vector
    q_emb = model.encode(question, convert_to_tensor=True)
    
    # Encode allowed intents into embedding vectors
    intents_emb = model.encode(ALLOWED_INTENTS, convert_to_tensor=True)
    
    # Calculate cosine similarity between question and intents
    similarity = util.cos_sim(q_emb, intents_emb)
    
    # Return True if maximum similarity exceeds threshold
    # Slightly relaxed threshold to understand more natural questions
    return similarity.max().item() > 0.50


def final_validator(question: str) -> bool:
    """
    Final validation function combining rule-based and semantic validation.
    
    Returns True if EITHER validation method passes.
    This ensures flexibility while maintaining domain restriction.
    
    Args:
        question: User's question string
    
    Returns:
        True if question is domain-related, False otherwise
    """
    # Try rule-based first (faster), then semantic (more flexible)
    return rule_based_validation(question) or semantic_validation(question)
