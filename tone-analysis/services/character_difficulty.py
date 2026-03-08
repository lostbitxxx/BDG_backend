"""
Character Difficulty Database for PSC Pronunciation Analysis

This module provides difficulty ratings and issue categorization for characters
commonly used in PSC tests. Difficulty is based on:
- Retroflex sounds (zh, ch, sh, r)
- Nasal distinctions (n vs l)
- Tone challenges (tone 2, tone 3, tone 4)
- Umbrella vowel (ü)
- Neutral tones
"""

from typing import Dict, List, Any

# Character difficulty ratings and common issues
# Format: "character": {"difficulty": 1-5, "issues": [], "category": "", "pinyin": ""}
# Difficulty: 1=easiest, 5=hardest for Cantonese speakers

CHARACTER_DIFFICULTY: Dict[str, Dict[str, Any]] = {
    # ============================================================================
    # LEVEL 1 - Very Easy (Difficulty 1)
    # Basic characters with no common issues for Cantonese speakers
    # ============================================================================
    "我": {"difficulty": 1, "issues": [], "category": "basic", "pinyin": "wǒ"},
    "你": {"difficulty": 1, "issues": ["n"], "category": "nasal", "pinyin": "nǐ"},
    "他": {"difficulty": 1, "issues": ["t"], "category": "initial", "pinyin": "tā"},
    "她": {"difficulty": 1, "issues": ["t"], "category": "initial", "pinyin": "tā"},
    "它": {"difficulty": 1, "issues": ["t"], "category": "initial", "pinyin": "tā"},
    "大": {"difficulty": 1, "issues": ["d"], "category": "initial", "pinyin": "dà"},
    "小": {"difficulty": 1, "issues": ["x"], "category": "initial", "pinyin": "xiǎo"},
    "人": {"difficulty": 1, "issues": ["r"], "category": "retroflex", "pinyin": "rén"},
    "来": {"difficulty": 1, "issues": ["l"], "category": "nasal", "pinyin": "lái"},
    "去": {"difficulty": 1, "issues": ["q"], "category": "initial", "pinyin": "qù"},
    "天": {"difficulty": 1, "issues": ["t"], "category": "initial", "pinyin": "tiān"},
    "地": {"difficulty": 1, "issues": ["d"], "category": "initial", "pinyin": "dì"},
    "上": {"difficulty": 1, "issues": ["sh"], "category": "retroflex", "pinyin": "shàng"},
    "下": {"dinyin": 1, "issues": ["x"], "category": "initial", "pinyin": "xià"},
    "中": {"difficulty": 1, "issues": ["zh"], "category": "retroflex", "pinyin": "zhōng"},
    "国": {"difficulty": 1, "issues": ["g"], "category": "initial", "pinyin": "guó"},
    "家": {"difficulty": 1, "issues": ["j"], "category": "initial", "pinyin": "jiā"},
    "学": {"difficulty": 1, "issues": ["x"], "category": "initial", "pinyin": "xué"},
    "校": {"difficulty": 1, "issues": ["x"], "category": "initial", "pinyin": "xiào"},
    "车": {"difficulty": 1, "issues": ["ch"], "category": "retroflex", "pinyin": "chē"},

    # ============================================================================
    # LEVEL 2 - Easy (Difficulty 2)
    # Characters with one common issue
    # ============================================================================
    "是": {"difficulty": 2, "issues": ["sh", "tone_4"], "category": "retroflex", "pinyin": "shì"},
    "在": {"difficulty": 2, "issues": ["z", "tone_4"], "category": "initial", "pinyin": "zài"},
    "有": {"difficulty": 2, "issues": ["y", "tone_3"], "category": "initial", "pinyin": "yǒu"},
    "和": {"difficulty": 2, "issues": ["h", "tone_2"], "category": "initial", "pinyin": "hé"},
    "这": {"difficulty": 2, "issues": ["zh", "tone_4"], "category": "retroflex", "pinyin": "zhè"},
    "那": {"difficulty": 2, "issues": ["n", "tone_4"], "category": "nasal", "pinyin": "nà"},
    "为": {"difficulty": 2, "issues": ["w", "tone_4"], "category": "initial", "pinyin": "wèi"},
    "就": {"difficulty": 2, "issues": ["j", "tone_4"], "category": "initial", "pinyin": "jiù"},
    "也": {"difficulty": 2, "issues": ["y", "tone_3"], "category": "initial", "pinyin": "yě"},
    "很": {"difficulty": 2, "issues": ["h", "tone_3"], "category": "initial", "pinyin": "hěn"},
    "都": {"difficulty": 2, "issues": ["d", "tone_1"], "category": "initial", "pinyin": "dōu"},
    "能": {"difficulty": 2, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "néng"},
    "会": {"difficulty": 2, "issues": ["h", "tone_4"], "category": "initial", "pinyin": "huì"},
    "可以": {"difficulty": 2, "issues": ["k"], "category": "initial", "pinyin": "kěyǐ"},
    "没": {"difficulty": 2, "issues": ["m", "tone_2"], "category": "initial", "pinyin": "méi"},
    "很": {"difficulty": 2, "issues": ["h", "tone_3"], "category": "initial", "pinyin": "hěn"},
    "说": {"difficulty": 2, "issues": ["sh", "tone_1"], "category": "retroflex", "pinyin": "shuō"},
    "看": {"difficulty": 2, "issues": ["k", "tone_4"], "category": "initial", "pinyin": "kàn"},
    "文": {"difficulty": 2, "issues": ["w"], "category": "initial", "pinyin": "wén"},
    "西": {"difficulty": 2, "issues": ["x", "tone_1"], "category": "initial", "pinyin": "xī"},

    # ============================================================================
    # LEVEL 3 - Medium (Difficulty 3)
    # Characters with multiple issues or harder phonemes
    # ============================================================================
    "知": {"difficulty": 3, "issues": ["zh", "tone_1"], "category": "retroflex", "pinyin": "zhī"},
    "道": {"difficulty": 3, "issues": ["d", "tone_4"], "category": "initial", "pinyin": "dào"},
    "吃": {"difficulty": 3, "issues": ["ch", "tone_1"], "category": "retroflex", "pinyin": "chī"},
    "出": {"difficulty": 3, "issues": ["ch", "tone_1"], "category": "retroflex", "pinyin": "chū"},
    "事": {"difficulty": 3, "issues": ["sh", "tone_4"], "category": "retroflex", "pinyin": "shì"},
    "时": {"difficulty": 3, "issues": ["sh", "tone_2"], "category": "retroflex", "pinyin": "shí"},
    "十": {"difficulty": 3, "issues": ["sh", "tone_2"], "category": "retroflex", "pinyin": "shí"},
    "事": {"difficulty": 3, "issues": ["sh", "tone_4"], "category": "retroflex", "pinyin": "shì"},
    "春": {"difficulty": 3, "issues": ["ch", "tone_1"], "category": "retroflex", "pinyin": "chūn"},
    "秋": {"difficulty": 3, "issues": ["q", "tone_1"], "category": "initial", "pinyin": "qiū"},
    "年": {"difficulty": 3, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "nián"},
    "月": {"difficulty": 3, "issues": ["y", "tone_4"], "category": "initial", "pinyin": "yuè"},
    "日": {"difficulty": 3, "issues": ["r", "tone_4"], "category": "retroflex", "pinyin": "rì"},
    "今": {"difficulty": 3, "issues": ["j", "tone_1"], "category": "initial", "pinyin": "jīn"},
    "天": {"difficulty": 3, "issues": ["t", "tone_1"], "category": "initial", "pinyin": "tiān"},
    "明": {"difficulty": 3, "issues": ["m", "tone_2"], "category": "initial", "pinyin": "míng"},
    "白": {"difficulty": 3, "issues": ["b", "tone_2"], "category": "initial", "pinyin": "bái"},
    "百": {"difficulty": 3, "issues": ["b", "tone_3"], "category": "initial", "pinyin": "bǎi"},
    "半": {"difficulty": 3, "issues": ["b", "tone_4"], "category": "initial", "pinyin": "bàn"},
    "万": {"difficulty": 3, "issues": ["w", "tone_4"], "category": "initial", "pinyin": "wàn"},

    # ============================================================================
    # LEVEL 4 - Hard (Difficulty 4)
    # Characters with challenging combinations
    # ============================================================================
    "女": {"difficulty": 4, "issues": ["n", "tone_3", "nasal"], "category": "nasal", "pinyin": "nǚ"},
    "吕": {"difficulty": 4, "issues": ["l", "tone_3", "ü"], "category": "umlaute", "pinyin": "lǚ"},
    "努力": {"difficulty": 4, "issues": ["n", "l", "tone_3"], "category": "nasal", "pinyin": "nǔlì"},
    "哪里": {"difficulty": 4, "issues": ["n", "l", "tone_3"], "category": "nasal", "pinyin": "nǎlǐ"},
    "那里": {"difficulty": 4, "issues": ["n", "l", "tone_3"], "category": "nasal", "pinyin": "nàlǐ"},
    "男": {"difficulty": 4, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "nán"},
    "蓝": {"difficulty": 4, "issues": ["l", "tone_2"], "category": "nasal", "pinyin": "lán"},
    "老": {"difficulty": 4, "issues": ["l", "tone_3"], "category": "nasal", "pinyin": "lǎo"},
    "脑": {"difficulty": 4, "issues": ["n", "tone_3"], "category": "nasal", "pinyin": "nǎo"},
    "闹": {"difficulty": 4, "issues": ["n", "tone_4"], "category": "nasal", "pinyin": "nào"},
    "南": {"difficulty": 4, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "nán"},
    "难": {"difficulty": 4, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "nán"},
    "农": {"difficulty": 4, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "nóng"},
    "牛": {"difficulty": 4, "issues": ["n", "tone_2"], "category": "nasal", "pinyin": "niú"},
    "你": {"difficulty": 4, "issues": ["n", "tone_3"], "category": "nasal", "pinyin": "nǐ"},
    "里": {"difficulty": 4, "issues": ["l", "tone_3"], "category": "nasal", "pinyin": "lǐ"},
    "路": {"difficulty": 4, "issues": ["l", "tone_4"], "category": "nasal", "pinyin": "lù"},
    "绿": {"difficulty": 4, "issues": ["l", "tone_4", "ü"], "category": "umlaute", "pinyin": "lǜ"},
    "律": {"difficulty": 4, "issues": ["l", "tone_4", "ü"], "category": "umlaute", "pinyin": "lǜ"},
    "旅": {"difficulty": 4, "issues": ["l", "tone_3", "ü"], "category": "umlaute", "pinyin": "lǚ"},

    # ============================================================================
    # LEVEL 5 - Very Hard (Difficulty 5)
    # Characters with ü and complex tones
    # ============================================================================
    "鱼": {"difficulty": 5, "issues": ["y", "tone_2", "ü"], "category": "umlaute", "pinyin": "yú"},
    "雨": {"difficulty": 5, "issues": ["y", "tone_3", "ü"], "category": "umlaute", "pinyin": "yǔ"},
    "语": {"difficulty": 5, "issues": ["y", "tone_3", "ü"], "category": "umlaute", "pinyin": "yǔ"},
    "月": {"difficulty": 5, "issues": ["y", "tone_4", "üe"], "category": "umlaute", "pinyin": "yuè"},
    "约": {"difficulty": 5, "issues": ["y", "tone_1", "üe"], "category": "umlaute", "pinyin": "yuē"},
    "月": {"difficulty": 5, "issues": ["y", "tone_4", "üe"], "category": "umlaute", "pinyin": "yuè"},
    "绝": {"difficulty": 5, "issues": ["j", "tone_2", "üe"], "category": "umlaute", "pinyin": "jué"},
    "学": {"difficulty": 5, "issues": ["x", "tone_2", "üe"], "category": "umlaute", "pinyin": "xué"},
    "雪": {"difficulty": 5, "issues": ["x", "tone_3", "üe"], "category": "umlaute", "pinyin": "xuě"},
    "血": {"difficulty": 5, "issues": ["x", "tone_4", "üe"], "category": "umlaute", "pinyin": "xuè"},
    "晕": {"difficulty": 5, "issues": ["y", "tone_1", "ün"], "category": "umlaute", "pinyin": "yūn"},
    "云": {"difficulty": 5, "issues": ["y", "tone_2", "ün"], "category": "umlaute", "pinyin": "yún"},
    "群": {"difficulty": 5, "issues": ["q", "tone_2", "ün"], "category": "umlaute", "pinyin": "qún"},
    "裙": {"difficulty": 5, "issues": ["q", "tone_2", "ün"], "category": "umlaute", "pinyin": "qún"},
    "勋": {"difficulty": 5, "issues": ["x", "tone_1", "ün"], "category": "umlaute", "pinyin": "xūn"},

    # ============================================================================
    # Neutral Tone Characters (Difficulty 2-3)
    # ============================================================================
    "的": {"difficulty": 2, "issues": ["neutral"], "category": "neutral", "pinyin": "de"},
    "了": {"difficulty": 2, "issues": ["neutral"], "category": "neutral", "pinyin": "le"},
    "着": {"difficulty": 2, "issues": ["neutral", "z"], "category": "neutral", "pinyin": "zhe"},
    "过": {"difficulty": 2, "issues": ["neutral", "g"], "category": "neutral", "pinyin": "guo"},
    "的": {"difficulty": 2, "issues": ["neutral"], "category": "neutral", "pinyin": "de"},
    "得": {"difficulty": 2, "issues": ["neutral", "d"], "category": "neutral", "pinyin": "de"},
    "地": {"difficulty": 2, "issues": ["neutral", "d"], "category": "neutral", "pinyin": "de"},
    "们": {"difficulty": 2, "issues": ["neutral", "m"], "category": "neutral", "pinyin": "men"},
    "吗": {"difficulty": 2, "issues": ["neutral", "m"], "category": "neutral", "pinyin": "ma"},
    "呢": {"difficulty": 2, "issues": ["neutral", "n"], "category": "neutral", "pinyin": "ne"},
    "吧": {"difficulty": 2, "issues": ["neutral", "b"], "category": "neutral", "pinyin": "ba"},
    "啊": {"difficulty": 2, "issues": ["neutral"], "category": "neutral", "pinyin": "a"},
    "呀": {"difficulty": 2, "issues": ["neutral", "y"], "category": "neutral", "pinyin": "ya"},

    # ============================================================================
    # Tone 3 Difficult Characters (Difficulty 3-4)
    # ============================================================================
    "把": {"difficulty": 3, "issues": ["b", "tone_3"], "category": "tone_3", "pinyin": "bǎ"},
    "马": {"difficulty": 3, "issues": ["m", "tone_3"], "category": "tone_3", "pinyin": "mǎ"},
    "打": {"difficulty": 3, "issues": ["d", "tone_3"], "category": "tone_3", "pinyin": "dǎ"},
    "拿": {"difficulty": 3, "issues": ["n", "tone_2"], "category": "tone_3", "pinyin": "ná"},
    "哪": {"difficulty": 3, "issues": ["n", "tone_3"], "category": "tone_3", "pinyin": "nǎ"},
    "可": {"difficulty": 3, "issues": ["k", "tone_3"], "category": "tone_3", "pinyin": "kě"},
    "使": {"difficulty": 3, "issues": ["sh", "tone_3"], "category": "tone_3", "pinyin": "shǐ"},
    "始": {"difficulty": 3, "issues": ["sh", "tone_3"], "category": "tone_3", "pinyin": "shǐ"},
    "喜": {"difficulty": 3, "issues": ["x", "tone_3"], "category": "tone_3", "pinyin": "xǐ"},
    "想": {"difficulty": 3, "issues": ["x", "tone_3"], "category": "tone_3", "pinyin": "xiǎng"},
    "响": {"difficulty": 3, "issues": ["x", "tone_3"], "category": "tone_3", "pinyin": "xiǎng"},
    "讲": {"difficulty": 3, "issues": ["j", "tone_3"], "category": "tone_3", "pinyin": "jiǎng"},
    "港": {"difficulty": 3, "issues": ["g", "tone_3"], "category": "tone_3", "pinyin": "gǎng"},
    "请": {"difficulty": 3, "issues": ["q", "tone_3"], "category": "tone_3", "pinyin": "qǐng"},
    "等": {"difficulty": 3, "issues": ["d", "tone_3"], "category": "tone_3", "pinyin": "děng"},
    "很": {"difficulty": 3, "issues": ["h", "tone_3"], "category": "tone_3", "pinyin": "hěn"},
    "懂": {"difficulty": 3, "issues": ["d", "tone_3"], "category": "tone_3", "pinyin": "dǒng"},
    "总": {"difficulty": 3, "issues": ["z", "tone_3"], "category": "tone_3", "pinyin": "zǒng"},
    "孔": {"difficulty": 3, "issues": ["k", "tone_3"], "category": "tone_3", "pinyin": "kǒng"},
    "永": {"difficulty": 4, "issues": ["y", "tone_3"], "category": "tone_3", "pinyin": "yǒng"},
}


def get_character_difficulty(char: str) -> Dict[str, Any]:
    """Get difficulty info for a character"""
    return CHARACTER_DIFFICULTY.get(char, {
        "difficulty": 3,  # default medium
        "issues": [],
        "category": "basic",
        "pinyin": ""
    })


def get_characters_by_category(category: str) -> List[str]:
    """Get all characters in a category"""
    return [char for char, info in CHARACTER_DIFFICULTY.items()
            if info.get("category") == category]


def get_characters_by_difficulty(difficulty: int) -> List[str]:
    """Get all characters at a specific difficulty level"""
    return [char for char, info in CHARACTER_DIFFICULTY.items()
            if info.get("difficulty") == difficulty]


def get_issue_characters(issue: str) -> List[str]:
    """Get all characters that have a specific issue"""
    return [char for char, info in CHARACTER_DIFFICULTY.items()
            if issue in info.get("issues", [])]


def get_practice_words_for_issue(issue: str) -> List[str]:
    """Get practice words for a specific issue"""
    issue_words = {
        "zh": ["知道", "中国", "吃饭", "车站", "校长"],
        "ch": ["吃饭", "出去", "车站", "长江", "乘车"],
        "sh": ["是的", "老师", "学生", "说话", "时间"],
        "r": ["人民", "认识", "日本", "然后", "日子"],
        "n": ["努力", "那里", "哪里", "奶奶", "男女"],
        "l": ["来了", "了解", "快乐", "礼貌", "道理"],
        "ü": ["绿", "雨", "语", "鱼", "月"],
        "tone_3": ["马", "把", "打", "哪", "可"],
        "neutral": ["的", "了", "着", "过", "们"],
    }
    return issue_words.get(issue, ["练习", "学习"])
