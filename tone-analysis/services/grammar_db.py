"""
Grammar Pattern Database for PSC Section 3
Used for 語法判斷 (grammar judgment) questions.
Contains common grammar patterns and common errors for Cantonese speakers.
"""

# Common Mandarin grammar patterns that Cantonese speakers often get wrong
GRAMMAR_PATTERNS = {
    # Word order issues
    "S+V+O": {
        "pattern": "我吃飯",
        "correct": True,
        "cantonese_error": "食飯 (verb comes first in Cantonese)",
    },

    # Comparison structures
    "比字句": {
        "pattern": "他比我高",
        "correct": True,
        "cantonese_error": "佢高過我 (uses 過)",
    },

    # Aspect particles
    "了_1": {
        "pattern": "我吃了飯",
        "correct": True,
        "cantonese_error": "食咗飯 (uses 咗)",
    },
    "了_2": {
        "pattern": "他來了",
        "correct": True,
        "cantonese_error": "佢嚟喇 (uses 喇)",
    },

    # Double negation
    "double_negation": {
        "pattern": "我不能不去",
        "correct": True,
        "cantonese_error": "我要去 (different structure)",
    },

    # 把字句
    "ba_structure": {
        "pattern": "我把門打開",
        "correct": True,
        "cantonese_error": "我開門 (no 把)",
    },

    # 被字句
    "bei_structure": {
        "pattern": "門被我打開",
        "correct": True,
        "cantonese_error": "門等我打開",
    },

    # Direction complements
    "direction_complement": {
        "pattern": "他跑過來",
        "correct": True,
        "cantonese_error": "佢跑過嚟",
    },

    # Result complements
    "result_complement": {
        "pattern": "他學會了",
        "correct": True,
        "cantonese_error": "佢學識",
    },

    # Question particle
    "question_ma": {
        "pattern": "你去嗎",
        "correct": True,
        "cantonese_error": "你去咩",
    },

    # Negation with 沒有
    "negation_meiyou": {
        "pattern": "我沒有去",
        "correct": True,
        "cantonese_error": "我去咗 (different aspect marking)",
    },

    # Reduplication
    "reduplication": {
        "pattern": "看一看",
        "correct": True,
        "cantonese_error": "睇下",
    },

    # A-not-A questions
    "a_not_a": {
        "pattern": "你去不去",
        "correct": True,
        "cantonese_error": "你去唔去",
    },

    # Time words position
    "time_word_position": {
        "pattern": "我今天去",
        "correct": True,
        "cantonese_error": "我今日去",
    },
}

# Common Cantonese-influenced grammar errors
CANTONESE_GRAMMAR_ERRORS = {
    # Verb-final word order
    "食咗飯先": "先吃了飯 (wrong order)",

    # Wrong aspect particles
    "我有去": "我沒有去",
    "佢走咗": "他走了",

    # Missing measure words
    "三個人": "三個人 (actually correct)",
    "一架車": "一輛車",

    # Wrong comparatives
    "佢高過你": "他比你高",

    # Wrong question particles
    "你去咩": "你去嗎",

    # Wrong modal verbs
    "你要去": "你要去 (actually correct)",
    "你可以去": "你可以去 (actually correct)",
}

# Standard Mandarin grammar rules
STANDARD_GRAMMAR_RULES = {
    # Basic sentence structure
    "basic_order": ["subject", "verb", "object"],

    # Time expressions
    "time_position": "Time words come before the verb",

    # Negation
    "negation_order": "Negation words (不, 沒有) come before the verb",

    # Aspect
    "aspect_particles": "了 (completed), 著 (continuous), 過 (experiential)",

    # Question formation
    "question_particles": "嗎, 呢, 吧, 呀",

    # Comparisons
    "comparison": "A比B+adjective",

    # Passive
    "passive": "B被A+verb",

    # Ba-structure
    "ba_structure": "把+O+verb+complement",
}

def check_grammar(text: str) -> dict:
    """
    Check if text follows standard Mandarin grammar.

    Returns:
        Dictionary with is_correct, errors, and suggestions
    """
    errors = []
    suggestions = []

    # Check for common Cantonese patterns
    for error_pattern, correction in CANTONESE_GRAMMAR_ERRORS.items():
        if error_pattern in text:
            errors.append({
                "pattern": error_pattern,
                "issue": "Cantonese grammar pattern",
                "suggestion": correction,
                "severity": "error"
            })

    return {
        "text": text,
        "is_correct": len(errors) == 0,
        "errors": errors,
        "suggestions": suggestions,
    }

def get_grammar_explanation(pattern: str) -> str:
    """Get explanation for a grammar pattern"""
    if pattern in GRAMMAR_PATTERNS:
        return GRAMMAR_PATTERNS[pattern].get("cantonese_error", "")
    return ""

def is_cantonese_grammar(text: str) -> bool:
    """Check if text contains Cantonese grammar patterns"""
    for error_pattern in CANTONESE_GRAMMAR_ERRORS.keys():
        if error_pattern in text:
            return True
    return False
