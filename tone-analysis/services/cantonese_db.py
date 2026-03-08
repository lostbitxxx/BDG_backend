"""
Cantonese vs Mandarin Vocabulary Database for PSC Section 3
Used for 詞語判斷 (vocabulary contrast) questions.
These are common Cantonese words that differ from Standard Mandarin.
"""

# Cantonese to Mandarin vocabulary mapping
# Format: cantonese_term: mandarin_term
CANTONESE_VS_MANDARIN = {
    # Common daily vocabulary
    "邊度": "哪裡",          # Where
    "洗手間": "衛生間",       # Toilet
    "銀包": "錢包",          # Wallet
    "針車": "縫紉機",        # Sewing machine
    "飛機": "飛機",          # Airplane (same in Cantonese but different tone)
    "既": "的",              # Possessive (Cantonese uses 喱/既)
    "幾多": "多少",          # How many
    "係": "是",              # Is
    "唔該": "謝謝/麻煩",     # Thank you/Excuse me
    "再見": "再見",          # Goodbye (same)

    # Food related
    "食": "吃",              # Eat
    "飲": "喝",              # Drink
    "早餐": "早飯",          # Breakfast
    "晏": "午餐",            # Lunch
    "晚": "晚飯",            # Dinner

    # Verbs
    "睇": "看",              # Look/Watch
    "聽": "聽",              # Listen (same but different context)
    "曉": "會",              # Can/Know how to
    "識": "會/認識",         # Know (how to)/Know (person)
    "冇": "沒有",            # Don't have
    "有": "有",              # Have (same)
    "去": "去",              # Go (same)
    "嚟": "來",              # Come
    "走": "跑",              # Run
    "打工": "工作",          # Work (part-time)

    # Pronouns
    "我哋": "我們",          # We
    "你哋": "你們",          # You (plural)
    "佢": "他/她/它",       # He/She/It
    "佢哋": "他們/她們",    # They
    "邊個": "誰",            # Who
    "咩": "什麼",            # What

    # Adjectives
    "靚": "漂亮/好看",       # Beautiful
    "衰": "壞",              # Bad
    "叻": "厲害/聰明",       # Clever
    "正": "厲害/棒",         # Great
    "曳": "調皮",            # Naughty

    # Time expressions
    "今日": "今天",          # Today
    "昨日": "昨天",          # Yesterday
    "明日": "明天",          # Tomorrow
    "現在": "現在",          # Now (same)
    "頭先": "剛才",          # Just now
    "晏啲": "待會兒",        # Later
    "唔該": "謝謝",          # Thank you

    # Question words
    "點解": "為什麼",        # Why
    "點樣": "怎麼樣",        # How
    "幾時": "什麼時候",      # When
    "邊": "哪",              # Which

    # Common phrases
    "你食咗未": "你吃了嗎", # Have you eaten?
    "早晨": "早上好",        # Good morning
    "晚安": "晚安",          # Good night (same)
    "多謝": "謝謝",          # Thank you

    # More vocabulary
    "公園": "公園",          # Park (same)
    "商場": "商場",          # Shopping mall (same)
    "地鐵": "地鐵",          # Subway (same)
    "巴士": "公交車",        # Bus
    "私家車": "私家車",      # Car (same)

    # Nouns
    "屋企": "家",            # Home
    "公司": "公司",          # Company (same)
    "學校": "學校",          # School (same)
    "大學": "大學",          # University (same)

    # More Cantonese terms
    "魚蛋": "魚丸",          # Fish ball
    "雲吞": "餛飩",          # Wonton
    "腸粉": "腸粉",          # Rice noodle roll
    "叉燒": "叉燒",          # Char siu (same)

    # Family
    "阿爸": "爸爸",          # Dad
    "阿媽": "媽媽",          # Mom
    "阿哥": "哥哥",          # Older brother
    "阿姐": "姐姐",          # Older sister
    "細佬": "弟弟",          # Younger brother
    "細妹": "妹妹",          # Younger sister

    # Body parts
    "頭": "頭",              # Head (same)
    "眼": "眼睛",            # Eye
    "耳": "耳朵",            # Ear
    "口": "嘴",              # Mouth
    "手": "手",              # Hand (same)
    "腳": "腳",              # Foot/Leg (same)
}

# Reverse mapping (Mandarin to Cantonese) - for checking if user uses Cantonese
MANDARIN_TO_CANTONESE = {v: k for k, v in CANTONESE_VS_MANDARIN.items()}

# Common Cantonese sentence patterns that are non-standard Mandarin
CANTONESE_PATTERNS = [
    # "喱啲" instead of "這些"
    # "嗰啲" instead of "那些"
    # "先" placed at end instead of "再"
]

# Get all Cantonese words
def get_cantonese_words() -> list:
    return list(CANTONESE_VS_MANDARIN.keys())

# Get all Mandarin words
def get_mandarin_words() -> list:
    return list(CANTONESE_VS_MANDARIN.values())

# Check if a word is Cantonese
def is_cantonese(word: str) -> bool:
    return word in CANTONESE_VS_MANDARIN

# Check if a word is Mandarin
def is_mandarin(word: str) -> bool:
    return word in MANDARIN_TO_CANTONESE

# Get Mandarin equivalent of Cantonese word
def get_mandarin_equivalent(cantonese: str) -> str:
    return CANTONESE_VS_MANDARIN.get(cantonese, "")

# Get Cantonese equivalent of Mandarin word
def get_cantonese_equivalent(mandarin: str) -> str:
    return MANDARIN_TO_CANTONESE.get(mandarin, "")
