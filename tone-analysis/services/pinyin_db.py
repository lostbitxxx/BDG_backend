"""
Comprehensive Pinyin Database for PSC (Putonghua Shuiping Ceshi)
Contains complete phoneme data, error patterns, and feedback for all pronunciation issues.
"""

# ============================================================================
# TONE DEFINITIONS
# ============================================================================

TONE_MAP = {
    0: {"name": "neutral", "name_zh": "轻声", "contour": "short/flat", "description": "Short, light, no clear pitch"},
    1: {"name": "high_flat", "name_zh": "高平", "contour": "flat_high", "f0_range": (280, 360), "duration": (250, 500)},
    2: {"name": "rising", "name_zh": "上升", "contour": "low_to_high", "f0_range": (200, 350), "duration": (250, 500)},
    3: {"name": "dipping", "name_zh": "降升", "contour": "high_low_high", "f0_range": (350, 200, 350), "duration": (250, 500)},
    4: {"name": "falling", "name_zh": "下降", "contour": "high_to_low", "f0_range": (350, 150), "duration": (150, 350)},
}

# ============================================================================
# INITIALS (声母) - Complete with IPA and details
# ============================================================================

INITIALS = {
    # Bilabial (双唇音)
    "b": {
        "name": "双唇不送气清塞音",
        "name_en": "Voiceless bilabial plosive",
        "ipa": "p",
        "voicing": "voiceless",
        "vot": 0,
        "place": "bilabial",
        "manner": "plosive",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "p": {
        "name": "双唇送气清塞音",
        "name_en": "Aspirated bilabial plosive",
        "ipa": "pʰ",
        "voicing": "voiced",
        "vot": 30,
        "place": "bilabial",
        "manner": "plosive",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "m": {
        "name": "双唇鼻音",
        "name_en": "Bilabial nasal",
        "ipa": "m",
        "voicing": "voiced",
        "vot": None,
        "place": "bilabial",
        "manner": "nasal",
        "retroflex": False,
        "nasal": True,
        "difficulty": "easy"
    },
    "f": {
        "name": "唇齿清擦音",
        "name_en": "Voiceless labiodental fricative",
        "ipa": "f",
        "voicing": "voiceless",
        "vot": None,
        "place": "labiodental",
        "manner": "fricative",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },

    # Alveolar (舌尖音)
    "d": {
        "name": "舌尖不送气清塞音",
        "name_en": "Voiceless alveolar plosive",
        "ipa": "t",
        "voicing": "voiceless",
        "vot": 0,
        "place": "alveolar",
        "manner": "plosive",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "t": {
        "name": "舌尖送气清塞音",
        "name_en": "Aspirated alveolar plosive",
        "ipa": "tʰ",
        "voicing": "voiced",
        "vot": 30,
        "place": "alveolar",
        "manner": "plosive",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "n": {
        "name": "舌尖鼻音",
        "name_en": "Alveolar nasal",
        "ipa": "n",
        "voicing": "voiced",
        "vot": None,
        "place": "alveolar",
        "manner": "nasal",
        "retroflex": False,
        "nasal": True,
        "difficulty": "easy"
    },
    "l": {
        "name": "舌尖边音",
        "name_en": "Alveolar lateral approximant",
        "ipa": "l",
        "voicing": "voiced",
        "vot": None,
        "place": "alveolar",
        "manner": "lateral",
        "retroflex": False,
        "nasal": True,
        "difficulty": "medium"
    },

    # Velar (舌根音)
    "g": {
        "name": "舌根不送气清塞音",
        "name_en": "Voiceless velar plosive",
        "ipa": "k",
        "voicing": "voiceless",
        "vot": 0,
        "place": "velar",
        "manner": "plosive",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "k": {
        "name": "舌根送气清塞音",
        "name_en": "Aspirated velar plosive",
        "ipa": "kʰ",
        "voicing": "voiced",
        "vot": 30,
        "place": "velar",
        "manner": "plosive",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "h": {
        "name": "舌根清擦音",
        "name_en": "Voiceless velar fricative",
        "ipa": "x",
        "voicing": "voiceless",
        "vot": None,
        "place": "velar",
        "manner": "fricative",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },

    # Palatal (舌面音)
    "j": {
        "name": "舌面不送气清塞擦音",
        "name_en": "Voiceless palatal affricate",
        "ipa": "tɕ",
        "voicing": "voiceless",
        "vot": 0,
        "place": "palatal",
        "manner": "affricate",
        "retroflex": False,
        "nasal": False,
        "difficulty": "medium"
    },
    "q": {
        "name": "舌面送气清塞擦音",
        "name_en": "Aspirated palatal affricate",
        "ipa": "tɕʰ",
        "voicing": "voiced",
        "vot": 30,
        "place": "palatal",
        "manner": "affricate",
        "retroflex": False,
        "nasal": False,
        "difficulty": "medium"
    },
    "x": {
        "name": "舌面清擦音",
        "name_en": "Voiceless palatal fricative",
        "ipa": "ɕ",
        "voicing": "voiceless",
        "vot": None,
        "place": "palatal",
        "manner": "fricative",
        "retroflex": False,
        "nasal": False,
        "difficulty": "medium"
    },

    # Retroflex (翘舌音) - Difficult for Cantonese/non-native speakers
    "zh": {
        "name": "翘舌不送气清塞擦音",
        "name_en": "Voiceless retroflex affricate",
        "ipa": "ʈʂ",
        "voicing": "voiceless",
        "vot": 0,
        "place": "retroflex",
        "manner": "affricate",
        "retroflex": True,
        "nasal": False,
        "difficulty": "high"
    },
    "ch": {
        "name": "翘舌送气清塞擦音",
        "name_en": "Aspirated retroflex affricate",
        "ipa": "ʈʂʰ",
        "voicing": "voiced",
        "vot": 30,
        "place": "retroflex",
        "manner": "affricate",
        "retroflex": True,
        "nasal": False,
        "difficulty": "high"
    },
    "sh": {
        "name": "翘舌清擦音",
        "name_en": "Voiceless retroflex fricative",
        "ipa": "ʂ",
        "voicing": "voiceless",
        "vot": None,
        "place": "retroflex",
        "manner": "fricative",
        "retroflex": True,
        "nasal": False,
        "difficulty": "high"
    },
    "r": {
        "name": "翘舌浊擦音/近音",
        "name_en": "Retroflex approximant",
        "ipa": "ɻ",
        "voicing": "voiced",
        "vot": None,
        "place": "retroflex",
        "manner": "approximant",
        "retroflex": True,
        "nasal": False,
        "difficulty": "high"
    },

    # Dental/Alveolar (平舌音)
    "z": {
        "name": "舌尖不送气清塞擦音",
        "name_en": "Voiceless alveolar affricate",
        "ipa": "ts",
        "voicing": "voiceless",
        "vot": 0,
        "place": "alveolar",
        "manner": "affricate",
        "retroflex": False,
        "nasal": False,
        "difficulty": "medium"
    },
    "c": {
        "name": "舌尖送气清塞擦音",
        "name_en": "Aspirated alveolar affricate",
        "ipa": "tsʰ",
        "voicing": "voiced",
        "vot": 30,
        "place": "alveolar",
        "manner": "affricate",
        "retroflex": False,
        "nasal": False,
        "difficulty": "medium"
    },
    "s": {
        "name": "舌尖清擦音",
        "name_en": "Voiceless alveolar fricative",
        "ipa": "s",
        "voicing": "voiceless",
        "vot": None,
        "place": "alveolar",
        "manner": "fricative",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },

    # Semivowels (半元音)
    "y": {
        "name": "舌面高舌唇元音",
        "name_en": "Palatal approximant",
        "ipa": "j",
        "voicing": "voiced",
        "vot": None,
        "place": "palatal",
        "manner": "approximant",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
    "w": {
        "name": "唇舌高圆唇元音",
        "name_en": "Labial-velar approximant",
        "ipa": "w",
        "voicing": "voiced",
        "vot": None,
        "place": "labial-velar",
        "manner": "approximant",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },

    # Zero initial (零声母)
    "": {
        "name": "零声母",
        "name_en": "Zero initial",
        "ipa": "",
        "voicing": "varies",
        "vot": None,
        "place": "none",
        "manner": "none",
        "retroflex": False,
        "nasal": False,
        "difficulty": "easy"
    },
}

# ============================================================================
# FINALS (韵母) - Complete with IPA and details
# ============================================================================

FINALS = {
    # Simple vowels (单元音)
    "a": {
        "name": "低舌央不圆唇元音",
        "name_en": "Low central unrounded vowel",
        "ipa": "a",
        "f1_range": (700, 1000),
        "f2_range": (1200, 2000),
        "nasal": False,
        "category": "simple_vowel"
    },
    "o": {
        "name": "后半高圆唇元音",
        "name_en": "Mid-high back rounded vowel",
        "ipa": "o",
        "f1_range": (400, 600),
        "f2_range": (700, 1200),
        "nasal": False,
        "category": "simple_vowel"
    },
    "e": {
        "name": "后半高不圆唇元音",
        "name_en": "Mid-high back unrounded vowel",
        "ipa": "ə",
        "f1_range": (400, 600),
        "f2_range": (1200, 2000),
        "nasal": False,
        "category": "simple_vowel"
    },
    "i": {
        "name": "前高不圆唇元音",
        "name_en": "High front unrounded vowel",
        "ipa": "i",
        "f1_range": (250, 350),
        "f2_range": (2000, 2800),
        "nasal": False,
        "category": "simple_vowel"
    },
    "u": {
        "name": "后高圆唇元音",
        "name_en": "High back rounded vowel",
        "ipa": "u",
        "f1_range": (250, 350),
        "f2_range": (700, 1200),
        "nasal": False,
        "category": "simple_vowel"
    },
    "ü": {
        "name": "前高圆唇元音",
        "name_en": "High front rounded vowel",
        "ipa": "y",
        "f1_range": (250, 350),
        "f2_range": (1500, 2200),
        "nasal": False,
        "category": "simple_vowel"
    },

    # Compound vowels (复合元音)
    "ai": {
        "name": "复合元音ai",
        "name_en": "Diphthong ai",
        "ipa": "ai",
        "nasal": False,
        "category": "compound_vowel"
    },
    "ei": {
        "name": "复合元音ei",
        "name_en": "Diphthong ei",
        "ipa": "ei",
        "nasal": False,
        "category": "compound_vowel"
    },
    "ui": {
        "name": "复合元音ui",
        "name_en": "Diphthong ui",
        "ipa": "ui",
        "nasal": False,
        "category": "compound_vowel"
    },
    "ao": {
        "name": "复合元音ao",
        "name_en": "Diphthong ao",
        "ipa": "au",
        "nasal": False,
        "category": "compound_vowel"
    },
    "ou": {
        "name": "复合元音ou",
        "name_en": "Diphthong ou",
        "ipa": "ou",
        "nasal": False,
        "category": "compound_vowel"
    },
    "iu": {
        "name": "复合元音iu",
        "name_en": "Diphthong iu",
        "ipa": "iu",
        "nasal": False,
        "category": "compound_vowel"
    },
    "ie": {
        "name": "复合元音ie",
        "name_en": "Diphthong ie",
        "ipa": "ie",
        "nasal": False,
        "category": "compound_vowel"
    },
    "üe": {
        "name": "复合元音üe",
        "name_en": "Diphthong üe",
        "ipa": "ye",
        "nasal": False,
        "category": "compound_vowel"
    },
    "er": {
        "name": "卷舌元音",
        "name_en": "Rhotic vowel",
        "ipa": "əɚ",
        "nasal": False,
        "category": "rhotic_vowel"
    },

    # Nasal finals with -n (鼻韵母n尾)
    "an": {
        "name": "鼻韵母an",
        "name_en": "Nasal final an",
        "ipa": "an",
        "nasal": True,
        "nasal_type": "n",
        "f1_range": (600, 800),
        "f2_range": (1200, 1800),
        "category": "nasal_final"
    },
    "en": {
        "name": "鼻韵母en",
        "name_en": "Nasal final en",
        "ipa": "ən",
        "nasal": True,
        "nasal_type": "n",
        "f1_range": (400, 550),
        "f2_range": (1200, 1800),
        "category": "nasal_final"
    },
    "in": {
        "name": "鼻韵母in",
        "name_en": "Nasal final in",
        "ipa": "in",
        "nasal": True,
        "nasal_type": "n",
        "f1_range": (250, 350),
        "f2_range": (2000, 2600),
        "category": "nasal_final"
    },
    "un": {
        "name": "鼻韵母un",
        "name_en": "Nasal final un",
        "ipa": "un",
        "nasal": True,
        "nasal_type": "n",
        "f1_range": (300, 450),
        "f2_range": (800, 1400),
        "category": "nasal_final"
    },
    "ün": {
        "name": "鼻韵母ün",
        "name_en": "Nasal final ün",
        "ipa": "yn",
        "nasal": True,
        "nasal_type": "n",
        "f1_range": (250, 350),
        "f2_range": (1800, 2400),
        "category": "nasal_final"
    },

    # Nasal finals with -ng (鼻韵母ng尾)
    "ang": {
        "name": "鼻韵母ang",
        "name_en": "Nasal final ang",
        "ipa": "aŋ",
        "nasal": True,
        "nasal_type": "ng",
        "f1_range": (600, 800),
        "f2_range": (1000, 1600),
        "category": "nasal_final"
    },
    "eng": {
        "name": "鼻韵母eng",
        "name_en": "Nasal final eng",
        "ipa": "əŋ",
        "nasal": True,
        "nasal_type": "ng",
        "f1_range": (400, 550),
        "f2_range": (1000, 1600),
        "category": "nasal_final"
    },
    "ing": {
        "name": "鼻韵母ing",
        "name_en": "Nasal final ing",
        "ipa": "iŋ",
        "nasal": True,
        "nasal_type": "ng",
        "f1_range": (250, 350),
        "f2_range": (1800, 2400),
        "category": "nasal_final"
    },
    "ong": {
        "name": "鼻韵母ong",
        "name_en": "Nasal final ong",
        "ipa": "uŋ",
        "nasal": True,
        "nasal_type": "ng",
        "f1_range": (350, 500),
        "f2_range": (700, 1300),
        "category": "nasal_final"
    },
}

# ============================================================================
# ERROR PATTERNS (Common pronunciation errors with feedback)
# ============================================================================

ERROR_PATTERNS = {
    # =========================================================================
    # INITIAL ERRORS - Retroflex confusion (most common for Cantonese speakers)
    # =========================================================================
    ("zh", "z"): {
        "error_code": "INIT_ZH_Z",
        "category": "initial_error",
        "description_en": "Retroflex 'zh' pronounced as flat 'z'",
        "description_zh": "翘舌音zh读成平舌音z",
        "fix_en": "Curl your tongue tip back and up towards the hard palate. The tongue should curl back, not stay flat.",
        "fix_zh": "将舌尖翘起向上抵住硬腭。舌头应该向后翘起，而不是保持平坦。",
        "tip_en": "Practice by saying 'zh-zh-zh' with tongue curled back",
        "tip_zh": "练习卷舌说'zh-zh-zh'",
        "difficulty": "high",
        "practice_words": ["知道", "中国", "吃饭", "车站", "校长", "工作"]
    },
    ("ch", "c"): {
        "error_code": "INIT_CH_C",
        "category": "initial_error",
        "description_en": "Retroflex 'ch' pronounced as flat 'c'",
        "description_zh": "翘舌音ch读成平舌音c",
        "fix_en": "Curl tongue back and add strong aspiration. Push more air than with 'c'.",
        "fix_zh": "舌尖翘起并加强送气。比c音送出更多气流。",
        "tip_en": "Practice: ch-ch-ch with strong airflow",
        "tip_zh": "练习：ch-ch-ch 加强送气",
        "difficulty": "high",
        "practice_words": ["吃饭", "出去", "车站", "长江", "乘车", "词典"]
    },
    ("sh", "s"): {
        "error_code": "INIT_SH_S",
        "category": "initial_error",
        "description_en": "Retroflex 'sh' pronounced as flat 's'",
        "description_zh": "翘舌音sh读成平舌音s",
        "fix_en": "Curl tongue back and round lips slightly. The sound should come from further back.",
        "fix_zh": "舌尖翘起，轻微圆唇。声音应该从更后面发出。",
        "tip_en": "Practice: sh-sh-sh with curled tongue",
        "tip_zh": "练习：sh-sh-sh 舌尖翘起",
        "difficulty": "high",
        "practice_words": ["是的", "老师", "学生", "事情", "说话", "水果"]
    },
    ("r", "y"): {
        "error_code": "INIT_R_Y",
        "category": "initial_error",
        "description_en": "'r' pronounced as 'y'",
        "description_zh": "r音读成y音",
        "fix_en": "Curl tongue back and vocalize (add voice). Unlike 'y', 'r' requires tongue retroflexion.",
        "fix_zh": "舌尖翘起，声带振动。与y不同，r需要舌尖翘起。",
        "tip_en": "Practice: r-r-r with tongue curled, then r-y contrast",
        "tip_zh": "练习：r-r-r 舌尖翘起，然后r-y对比",
        "difficulty": "high",
        "practice_words": ["人民", "认识", "日本", "然后", "日子", "认真"]
    },

    # =========================================================================
    # INITIAL ERRORS - Nasal/lateral confusion
    # =========================================================================
    ("n", "l"): {
        "error_code": "INIT_N_L",
        "category": "initial_error",
        "description_en": "Nasal 'n' pronounced as lateral 'l'",
        "description_zh": "鼻音n读成边音l",
        "fix_en": "Press tongue tip to alveolar ridge and let air escape through nose. Close off the sides of your mouth.",
        "fix_zh": "舌尖抵住上齿龈，气从鼻腔呼出。闭合嘴巴两侧。",
        "tip_en": "Hold your nose - if sound comes out, you're using 'n'",
        "tip_zh": "捏住鼻子 - 如果还有声音发出，说明用的是n音",
        "difficulty": "medium",
        "practice_words": ["努力", "那里", "哪里", "奶奶", "男女", "农民"]
    },
    ("l", "n"): {
        "error_code": "INIT_L_N",
        "category": "initial_error",
        "description_en": "Lateral 'l' pronounced as nasal 'n'",
        "description_zh": "边音l读成鼻音n",
        "fix_en": "Press tongue tip to alveolar ridge and let air escape from the sides of your mouth.",
        "fix_zh": "舌尖抵住上齿龈，气从嘴巴两边呼出。",
        "tip_en": "Practice: la-la-la, keeping tongue sides relaxed",
        "tip_zh": "练习：la-la-la，舌头两侧放松",
        "difficulty": "medium",
        "practice_words": ["来了", "了解", "快乐", "道理", "礼貌", "老"]
    },

    # =========================================================================
    # INITIAL ERRORS - Aspirated/unaspirated confusion
    # =========================================================================
    ("p", "b"): {
        "error_code": "INIT_P_B",
        "category": "initial_error",
        "description_en": "Aspirated 'p' pronounced as unaspirated 'b'",
        "description_zh": "送气音p读成不送气音b",
        "fix_en": "Add strong aspiration - push out air when saying 'p'. It should sound like 'puh'.",
        "fix_zh": "加强送气 - 说p时向外推送气流。应该是'puh'的声音。",
        "tip_en": "Hold a piece of paper - it should move when you say 'p'",
        "tip_zh": "放一张纸在面前 - 说p时纸应该会动",
        "difficulty": "medium",
        "practice_words": ["害怕", "漂亮", "朋友", "批评", "皮肤", "苹果"]
    },
    ("t", "d"): {
        "error_code": "INIT_T_D",
        "category": "initial_error",
        "description_en": "Aspirated 't' pronounced as unaspirated 'd'",
        "description_zh": "送气音t读成不送气音d",
        "fix_en": "Add strong aspiration - push out air when saying 't'.",
        "fix_zh": "加强送气 - 说t时向外推送气流。",
        "tip_en": "Hold a piece of paper - it should move when you say 't'",
        "tip_zh": "放一张纸在面前 - 说t时纸应该会动",
        "difficulty": "medium",
        "practice_words": ["天空", "今天", "身体", "问题", "特别", "停止"]
    },
    ("k", "g"): {
        "error_code": "INIT_K_G",
        "category": "initial_error",
        "description_en": "Aspirated 'k' pronounced as unaspirated 'g'",
        "description_zh": "送气音k读成不送气音g",
        "fix_en": "Add strong aspiration - push out air when saying 'k' from the back of your throat.",
        "fix_zh": "加强送气 - 从喉咙后部向外推送气流说k。",
        "tip_en": "Feel the aspiration in your throat, not just at your mouth",
        "tip_zh": "感受气流从喉咙发出，不只是嘴巴",
        "difficulty": "medium",
        "practice_words": ["可以", "看见", "快乐", "科学", "开发", "上课"]
    },

    # =========================================================================
    # TONE ERRORS
    # =========================================================================
    ("tone_1_to_2"): {
        "error_code": "TONE_1_2",
        "category": "tone_error",
        "description_en": "Tone 1 (high flat) pronounced as Tone 2 (rising)",
        "description_zh": "第一声（高平）读成第二声（上升）",
        "fix_en": "Keep your pitch flat and high throughout. Don't let it rise at the end.",
        "fix_zh": "保持音调从头到尾平坦且高音。不要在结尾上升。",
        "tip_en": "Say 'mā' (mother) - hold it at the same high level",
        "tip_zh": "说'妈妈'的'妈' - 保持在同一高音调",
        "difficulty": "medium",
        "practice_words": ["春天", "天空", "工作", "飞机", "妈妈", "高"]
    },
    ("tone_1_to_3"): {
        "error_code": "TONE_1_3",
        "category": "tone_error",
        "description_en": "Tone 1 (high flat) pronounced as Tone 3 (dipping)",
        "description_zh": "第一声（高平）读成第三声（降升）",
        "fix_en": "Keep your pitch flat and high. Don't dip in the middle.",
        "fix_zh": "保持音调平坦且高音。中间不要下降。",
        "tip_en": "Imagine you're singing a flat high note",
        "tip_zh": "想象你在唱一个平坦的高音",
        "difficulty": "medium",
        "practice_words": ["开会", "飞机", "工作", "发生", "非常"]
    },
    ("tone_1_to_4"): {
        "error_code": "TONE_1_4",
        "category": "tone_error",
        "description_en": "Tone 1 (high flat) pronounced as Tone 4 (falling)",
        "description_zh": "第一声（高平）读成第四声（下降）",
        "fix_en": "Keep your pitch flat. Don't let it fall.",
        "fix_zh": "保持音调平坦。不要下降。",
        "tip_en": "Practice: mā-mā-mā, holding each at same pitch",
        "tip_zh": "练习：妈妈妈，保持同一音调",
        "difficulty": "medium",
        "practice_words": ["高", "山", "花", "书", "天"]
    },
    ("tone_2_to_3"): {
        "error_code": "TONE_2_3",
        "category": "tone_error",
        "description_en": "Tone 2 (rising) pronounced as Tone 3 (dipping)",
        "description_zh": "第二声（上升）读成第三声（降升）",
        "fix_en": "Rise from mid to high directly. Don't dip down first.",
        "fix_zh": "从中调直接升到高音。不要先下降。",
        "tip_en": "Imagine asking a question 'What?' with rising intonation",
        "tip_zh": "想象你在问'什么？'升调",
        "difficulty": "medium",
        "practice_words": ["头发", "银行", "不行", "学习", "民族"]
    },
    ("tone_3_to_2"): {
        "error_code": "TONE_3_2",
        "category": "tone_error",
        "description_en": "Tone 3 (dipping) pronounced as Tone 2 (rising)",
        "description_zh": "第三声（降升）读成第二声（上升）",
        "fix_en": "Start mid, go LOW, then rise HIGH. It's a dip-then-rise pattern.",
        "fix_zh": "从中调开始，下降到低音，再升到高音。是先降后升的调子。",
        "tip_en": "Practice: ǎ-ǎ-ǎ, dip then rise",
        "tip_zh": "练习：先降后升",
        "difficulty": "hard",
        "practice_words": ["努力", "水果", "了解", "准备", "北方"]
    },
    ("tone_3_to_4"): {
        "error_code": "TONE_3_4",
        "category": "tone_error",
        "description_en": "Tone 3 (dipping) pronounced as Tone 4 (falling)",
        "description_zh": "第三声（降升）读成第四声（下降）",
        "fix_en": "After falling, you MUST rise. Tone 3 is dip-then-rise, not just fall.",
        "fix_zh": "下降后必须上升。第三声是先降后升，不是只下降。",
        "tip_en": "Remember: tone 3 dips BEFORE rising",
        "tip_zh": "记住：第三声是先下降再上升",
        "difficulty": "hard",
        "practice_words": ["了解", "努力", "简单", "水果"]
    },
    ("tone_4_to_2"): {
        "error_code": "TONE_4_2",
        "category": "tone_error",
        "description_en": "Tone 4 (falling) pronounced as Tone 2 (rising)",
        "description_zh": "第四声（下降）读成第二声（上升）",
        "fix_en": "Start high and fall. Don't rise. Tone 4 goes DOWN, not up.",
        "fix_zh": "从高音开始下降。不要上升。第四声是下降，不是上升。",
        "tip_en": "Imagine expressing disapproval or exclamation",
        "tip_zh": "想象你在表达不满或感叹",
        "difficulty": "medium",
        "practice_words": ["再见", "已经", "工作", "注意", "特别"]
    },

    # =========================================================================
    # FINAL ERRORS - Nasal final confusion
    # =========================================================================
    ("an", "ang"): {
        "error_code": "FINAL_AN_ANG",
        "category": "final_error",
        "description_en": "'an' pronounced as 'ang'",
        "description_zh": "an音读成ang音",
        "fix_en": "Keep your tongue at the front of your mouth. End with -n, not -ng.",
        "fix_zh": "保持舌头在口腔前部。以n结尾，不是ng。",
        "tip_en": "The 'n' is made with tongue at front, 'ng' at back",
        "tip_zh": "n音舌头在前，ng音舌头在后",
        "difficulty": "medium",
        "practice_words": ["南方", "当然", "简单", "很难", "安全"]
    },
    ("ang", "an"): {
        "error_code": "FINAL_ANG_AN",
        "category": "final_error",
        "description_en": "'ang' pronounced as 'an'",
        "description_zh": "ang音读成an音",
        "fix_en": "Move your tongue to the back of your mouth. End with -ng.",
        "fix_zh": "将舌头移到口腔后部。以ng结尾。",
        "tip_en": "Practice: ang-ang-ang, feeling tongue at back",
        "tip_zh": "练习：ang-ang-ang，感受舌头在后",
        "difficulty": "medium",
        "practice_words": ["帮忙", "商场", "厂房", "银行", "方向"]
    },
    ("en", "eng"): {
        "error_code": "FINAL_EN_ENG",
        "category": "final_error",
        "description_en": "'en' pronounced as 'eng'",
        "description_zh": "en音读成eng音",
        "fix_en": "Keep tongue front, end with pure -n sound.",
        "fix_zh": "舌头保持在前，以纯n音结尾。",
        "tip_en": "The 'ng' adds a 'g' quality at the end",
        "tip_zh": "ng在结尾加了g的音质",
        "difficulty": "medium",
        "practice_words": ["根本", "认真", "大门", "本身", "新闻"]
    },
    ("eng", "en"): {
        "error_code": "FINAL_ENG_EN",
        "category": "final_error",
        "description_en": "'eng' pronounced as 'en'",
        "description_zh": "eng音读成en音",
        "fix_en": "Add the -ng ending with tongue at back of mouth.",
        "fix_zh": "以ng结尾，舌头放在口腔后部。",
        "tip_en": "Practice: eng-eng-eng, adding nasal resonance",
        "tip_zh": "练习：eng-eng-eng，加鼻音共鸣",
        "difficulty": "medium",
        "practice_words": ["更冷", "朋友", "风筝", "成功", "形成"]
    },
    ("in", "ing"): {
        "error_code": "FINAL_IN_ING",
        "category": "final_error",
        "description_en": "'in' pronounced as 'ing'",
        "description_zh": "in音读成ing音",
        "fix_en": "Keep tongue front, end with -n only.",
        "fix_zh": "舌头保持在前，只以n结尾。",
        "tip_en": "The 'i' in 'in' is similar to 'see', add 'n' at end",
        "tip_zh": "in中的i类似'see'，末尾加n",
        "difficulty": "medium",
        "practice_words": ["人民", "银行", "今天", "新", "金"]
    },
    ("ing", "in"): {
        "error_code": "FINAL_ING_IN",
        "category": "final_error",
        "description_en": "'ing' pronounced as 'in'",
        "description_zh": "ing音读成in音",
        "fix_en": "Add nasal resonance at the end with -ng.",
        "fix_zh": "末尾加ng的鼻音共鸣。",
        "tip_en": "The 'ng' adds a nasal 'ng' sound at the end",
        "tip_zh": "ng在末尾加了鼻音ng",
        "difficulty": "medium",
        "practice_words": ["高兴", "明星", "卫星", "请", "听"]
    },

    # =========================================================================
    # NEUTRAL TONE ERRORS
    # =========================================================================
    ("neutral_to_full"): {
        "error_code": "NEUTRAL_FULL",
        "category": "neutral_tone_error",
        "description_en": "Should be neutral tone but pronounced with full tone",
        "description_zh": "应该是轻声但读成了完整声调",
        "fix_en": "Make it short and light. It should be quick, like a whisper.",
        "fix_zh": "读得又短又轻。应该很快，像耳语一样。",
        "tip_en": "Neutral tone is about 1/3 the length of full tones",
        "tip_zh": "轻声大约是完整声调的1/3长度",
        "difficulty": "medium",
        "practice_words": ["桌子", "椅子", "房子", "孩子", "妻子"]
    },
    ("full_to_neutral"): {
        "error_code": "FULL_NEUTRAL",
        "category": "neutral_tone_error",
        "description_en": "Should be full tone but pronounced as neutral",
        "description_zh": "应该是完整声调但读成了轻声",
        "fix_en": "Say it with full length and clear tone.",
        "fix_zh": "用完整的长度和清晰的声调来说。",
        "tip_en": "Give it the full duration and pitch contour",
        "tip_zh": "给它完整的长度和声调轮廓",
        "difficulty": "medium",
        "practice_words": ["一", "不", "三"]
    },
}

# ============================================================================
# TONE SANDHI RULES (变调规则)
# ============================================================================

TONE_SANDHI_RULES = {
    # 一不变调 (yī)
    ("一", "一声"): ("yī", "yì"),    # yī + yī = yī yì
    ("一", "二声"): ("yī", "yí"),    # yī + é = yī é (actually yí)
    ("一", "三声"): ("yī", "yǐ"),    # yī + ě = yī ě (actually yǐ)
    ("一", "四声"): ("yī", "yì"),    # yī + è = yī è (actually yì)

    # 不不变调 (bù)
    ("不", "四声"): ("bù", "bù"),    # bù + è = bù è (actually bù)
    ("不", "一声"): ("bù", "bú"),    # bù + ē = bù ē (actually bú)
    ("不", "二声"): ("bù", "bú"),    # bù + é = bù é (actually bú)
    ("不", "三声"): ("bù", "bú"),    # bù + ě = bù ě (actually bú)

    # 第三声连读 (third tone sandhi)
    ("三声", "三声"): ("sán", "sán"),  # 3+3 → 2+3
}

# ============================================================================
# COMMON NEUTRAL TONE WORDS (轻声词)
# ============================================================================

NEUTRAL_TONE_WORDS = {
    # Common particles
    "的": 0, "了": 0, "着": 0, "过": 0, "吗": 0,
    "呢": 0, "吧": 0, "啊": 0, "呀": 0, "哦": 0,
    "吗": 0, "嘛": 0, "啦": 0, "嘞": 0, "咧": 0,

    # Pronouns
    "们": 0, "的": 0,

    # Direction/complement
    "来": 0, "去": 0, "上": 0, "下": 0, "起": 0,

    # Others
    "里": 0, "面": 0, "头": 0, "边": 0,
    "的": 0, "得": 0, "地": 0,
}

# ============================================================================
# PRACTICE WORD LISTS BY CATEGORY
# ============================================================================

PRACTICE_WORDS = {
    # Retroflex practice
    "zh_words": ["知道", "中国", "吃饭", "车站", "校长", "工作", "正在", "住", "重视", "发展"],
    "ch_words": ["吃饭", "出去", "车站", "长江", "乘车", "词典", "春", "出", "初中", "城市"],
    "sh_words": ["是的", "老师", "学生", "事情", "说话", "水果", "时间", "开始", "身上", "世界"],
    "r_words": ["人民", "认识", "日本", "然后", "日子", "认真", "认识", "热", "让", "软"],

    # Nasal distinction
    "n_words": ["努力", "那么", "哪里", "奶奶", "男女", "农民", "头脑", "能", "你", "内"],
    "l_words": ["努力", "来了", "了解", "快乐", "道理", "礼貌", "老", "里", "蓝", "路"],

    # Tone 1
    "tone1_words": ["春天", "天空", "工作", "飞机", "妈妈", "高", "山", "花", "书", "天"],

    # Tone 2
    "tone2_words": ["银行", "头发", "学习", "人民", "谁", "忙", "运动", "白", "来", "河"],

    # Tone 3
    "tone3_words": ["努力", "了解", "简单", "水果", "已经", "准备", "北方", "马", "小", "好"],

    # Tone 4
    "tone4_words": ["再见", "已经", "工作", "注意", "特别", "快", "去", "是", "大", "在"],

    # Nasal finals an/ang
    "an_words": ["南方", "当然", "简单", "很难", "安全", "看", "安", "山", "半", "站"],
    "ang_words": ["帮忙", "商场", "厂房", "银行", "方向", "长", "忙", "房", "刚", "当"],

    # Nasal finals en/eng
    "en_words": ["根本", "认真", "大门", "本身", "新闻", "门", "本", "真", "很", "人"],
    "eng_words": ["更冷", "朋友", "风筝", "成功", "形成", "等", "朋", "风", "梦", "疼"],

    # Nasal finals in/ing
    "in_words": ["人民", "银行", "今天", "新", "金", "心", "亲", "林", "进", "拼"],
    "ing_words": ["高兴", "明星", "卫星", "请", "听", "清", "情", "定", "平", "轻"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_initial(pinyin: str) -> str:
    """Extract initial from pinyin"""
    if not pinyin:
        return ""

    # Remove tone number
    pinyin_base = pinyin
    if pinyin and pinyin[-1].isdigit():
        pinyin_base = pinyin[:-1]

    # Check for retroflex initials (zh, ch, sh, r)
    if len(pinyin_base) >= 2 and pinyin_base[:2] in INITIALS:
        return pinyin_base[:2]

    # Check for single letter initial
    if pinyin_base and pinyin_base[0] in INITIALS:
        return pinyin_base[0]

    return ""


def get_final(pinyin: str) -> str:
    """Extract final from pinyin"""
    initial = get_initial(pinyin)
    if initial:
        pinyin_base = pinyin
        if pinyin and pinyin[-1].isdigit():
            pinyin_base = pinyin[:-1]
        return pinyin_base[len(initial):]
    return pinyin[:-1] if pinyin and pinyin[-1].isdigit() else pinyin


def get_tone(pinyin: str) -> int:
    """Extract tone from pinyin"""
    if pinyin and pinyin[-1].isdigit():
        return int(pinyin[-1])
    return 0  # Neutral


def is_retroflex(pinyin: str) -> bool:
    """Check if pinyin has retroflex initial"""
    if not pinyin or not isinstance(pinyin, str):
        return False
    initial = get_initial(pinyin)
    return INITIALS.get(initial, {}).get("retroflex", False)


def is_nasal_final(pinyin: str) -> bool:
    """Check if pinyin has nasal final"""
    if not pinyin or not isinstance(pinyin, str):
        return False
    final = get_final(pinyin)
    if not isinstance(final, str):
        return False
    return FINALS.get(final, {}).get("nasal", False)


def get_error_info(expected_initial: str, actual_initial: str = None,
                   expected_tone: int = None, actual_tone: int = None) -> dict:
    """Get error information for a given error combination"""

    # Initial error
    if expected_initial and actual_initial and expected_initial != actual_initial:
        key = (expected_initial, actual_initial)
        if key in ERROR_PATTERNS:
            return ERROR_PATTERNS[key]

    # Tone error
    if expected_tone is not None and actual_tone is not None and expected_tone != actual_tone:
        key = f"tone_{expected_tone}_to_{actual_tone}"
        if key in ERROR_PATTERNS:
            return ERROR_PATTERNS[key]

    return None


def get_char_info(char: str) -> dict:
    """Get pinyin and tone info for a character"""
    from pypinyin import Style, pinyin

    try:
        py = pinyin(char, style=Style.TONE)
    except:
        return None

    # Handle the nested list structure
    if isinstance(py, list) and len(py) > 0:
        if isinstance(py[0], list):
            py = py[0] if len(py[0]) > 0 else []
        elif isinstance(py[0], str):
            py = py
        else:
            py = []
    else:
        py = []

    if not py:
        return None

    pinyin_str = py[0] if py else ""

    if not isinstance(pinyin_str, str):
        return None

    # Extract tone number from pinyin
    tone = get_tone(pinyin_str)
    pinyin_base = pinyin_str[:-1] if pinyin_str and pinyin_str[-1].isdigit() else pinyin_str
    initial = get_initial(pinyin_str)
    final = get_final(pinyin_str)

    return {
        "char": char,
        "pinyin": pinyin_str,
        "pinyin_base": pinyin_base,
        "tone": tone,
        "initial": initial,
        "final": final,
        "is_retroflex": is_retroflex(pinyin_str),
        "is_nasal_final": is_nasal_final(pinyin_str),
        "initial_info": INITIALS.get(initial, {}),
        "final_info": FINALS.get(final, {}),
    }


def analyze_text(text: str) -> list:
    """Analyze each character in text"""
    results = []
    for char in text:
        if char.strip():  # Skip whitespace
            info = get_char_info(char)
            if info:
                results.append(info)
    return results


# ============================================================================
# PSC TEST DATA
# ============================================================================

# PSC Section 1: Common single characters (100 characters)
PSC_SINGLE_CHARS = [
    "八,ba,1", "七,qi,1", "六,liu,4", "五,wu,3", "四,si,4",
    "三,san,1", "二,er,4", "一,yi,1", "九,jiu,3", "十,shi,2",
    "百,bai,3", "千,qian,1", "万,wan,4", "亿,yi,4", "零,ling,2",
    "大,da,4", "小,xiao,3", "中,zhong,1", "上,shang,4", "下,xia,4",
    "天,tian,1", "地,di,4", "人,ren,2", "我,wo,3", "你,ni,3",
    "他,ta,1", "她,ta,1", "它,ta,1", "们,men,0", "的,de,0",
    "了,le,0", "在,zai,4", "有,you,3", "和,he,2", "是,shi,4",
    "这,zhe,4", "那,na,4", "哪,na,3", "谁,shui,2", "什么,shenme,2",
    "怎,zen,3", "么,me,0", "为,wei,4", "什,shen,2", "么,me,0",
    "吗,ma,0", "呢,ne,0", "吧,ba,0", "啊,a,0", "哦,o,4",
    "嗯,en,0", "哈,ha,1", "喂,wei,4", "嘿,hei,1", "哼,heng,4",
    "飞,fei,1", "机,ji,1", "电,dian,4", "话,hua,4", "车,che,1",
    "站,zhan,4", "校,xiao,4", "长,zhang,3", "学,xue,2", "习,xi,2",
    "文,wen,2", "字,zi,4", "好,hao,3", "看,kan,4", "听,ting,1",
    "说,shuo,1", "话,hua,4", "读,du,2", "写,xie,3", "画,hua,4",
    "做,zuo,4", "事,shi,4", "想,xiang,3", "看,kan,4", "见,jian,4",
    "吃,chi,1", "喝,he,1", "走,zou,3", "跑,pao,3", "坐,zuo,4",
    "站,zhan,4", "睡,shui,4", "醒,xing,3", "笑,xiao,4", "哭,ku,1",
    "爱,ai,4", "恨,hen,4", "喜,xi,3", "欢,huan,1", "怕,pa,4",
    "能,neng,2", "会,hui,4", "可,ke,3", "以,yi,3", "要,yao,4",
    "给,gei,3", "送,song,4", "拿,na,2", "找,zhao,3", "得,de,0",
]


def load_psc_char_database() -> dict:
    """Load PSC character database"""
    db = {}
    for item in PSC_SINGLE_CHARS:
        parts = item.split(",")
        if len(parts) >= 3:
            char, pinyin, tone = parts
            initial = get_initial(pinyin)
            final = get_final(pinyin)
            db[char] = {
                "pinyin": pinyin,
                "tone": int(tone),
                "initial": initial,
                "final": final,
                "is_retroflex": is_retroflex(pinyin),
                "is_nasal_final": is_nasal_final(pinyin),
                "initial_info": INITIALS.get(initial, {}),
                "final_info": FINALS.get(final, {}),
            }
    return db
