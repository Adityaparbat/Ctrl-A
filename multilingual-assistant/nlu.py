from typing import List, Tuple

try:
    from transformers import (
        pipeline,
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )
except Exception:
    pipeline = None  # type: ignore
    AutoModelForSequenceClassification = None  # type: ignore
    AutoTokenizer = None  # type: ignore


_classifier = None
_ner = None


def _lazy_init_models():
    global _classifier, _ner
    if _classifier is not None and _ner is not None:
        return
    if pipeline is None:
        return
    try:
        name = "joeddav/xlm-roberta-large-xnli"
        tokenizer = AutoTokenizer.from_pretrained(name)
        model = AutoModelForSequenceClassification.from_pretrained(name)
        _classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)
    except Exception:
        _classifier = None
    try:
        _ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
    except Exception:
        _ner = None


# Candidate intents
candidate_labels = [
    "play_music",
    "stop_music",
    "get_weather",
    "set_alarm",
]


def detect_intent(user_input: str) -> Tuple[str, float]:
    _lazy_init_models()
    if _classifier is not None:
        result = _classifier(user_input, candidate_labels)
        return result["labels"][0], float(result["scores"][0])
    # Heuristic fallback
    text = user_input.lower()
    if any(k in text for k in ["play", "song", "music"]):
        return "play_music", 0.60
    if any(k in text for k in ["stop", "pause"]):
        return "stop_music", 0.60
    # Unknown intent
    return "none", 0.0


def extract_entities(user_input: str) -> List[str]:
    _lazy_init_models()
    if _ner is not None:
        ents = _ner(user_input)
        return [e["word"] for e in ents if e.get("entity_group") in ("PER", "MISC")]
    # Heuristic fallback: return words after 'play'
    text = user_input.strip()
    lower = text.lower()
    if "play" in lower:
        idx = lower.find("play")
        phrase = text[idx + len("play"):].strip()
        return [phrase] if phrase else []
    return []


def parse_command(user_input: str) -> Tuple[str, List[str], float]:
    intent, score = detect_intent(user_input)
    entities = extract_entities(user_input)
    return intent, entities, score
