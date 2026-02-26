"""
Pinyin Database for PSC (Putonghua Shuiping Ceshi)
Contains pinyin, tones, and phoneme information for common Chinese characters
"""

# Tone mapping: 1=flat, 2=rising, 3=dipping, 4=falling, 0=neutral
TONE_MAP = {
    1: "flat (高平)",
    2: "rising (上升)",
    3: "dipping (降升)",
    4: "falling (降)",
    0: "neutral (轻声)"
}

# Initial (声母) categories
INITIALS = {
    # Bilingual initials
    "b": {"name": "b", "retroflex": False, "nasal": False},
    "p": {"name": "p", "retroflex": False, "nasal": False},
    "m": {"name": "m", "retroflex": False, "nasal": True},
    "f": {"name": "f", "retroflex": False, "nasal": False},
    
    # Dentialveolar
    "d": {"name": "d", "retroflex": False, "nasal": False},
    "t": {"name": "t", "retroflex": False, "nasal": False},
    "n": {"name": "n", "retroflex": False, "nasal": True},
    "l": {"name": "l", "retroflex": False, "nasal": True},
    
    # Guttural
    "g": {"name": "g", "retroflex": False, "nasal": False},
    "k": {"name": "k", "retroflex": False, "nasal": False},
    "h": {"name": "h", "retroflex": False, "nasal": False},
    
    # Alveolar
    "j": {"name": "j", "retroflex": False, "nasal": False},
    "q": {"name": "q", "retroflex": False, "nasal": False},
    "x": {"name": "x", "retroflex": False, "nasal": False},
    
    # Retroflex (卷舌音) - difficult for Cantonese speakers
    "zh": {"name": "zh", "retroflex": True, "nasal": False},
    "ch": {"name": "ch", "retroflex": True, "nasal": False},
    "sh": {"name": "sh", "retroflex": True, "nasal": False},
    "r": {"name": "r", "retroflex": True, "nasal": False},
    
    # Dental/Alveolar
    "z": {"name": "z", "retroflex": False, "nasal": False},
    "c": {"name": "c", "retroflex": False, "nasal": False},
    "s": {"name": "s", "retroflex": False, "nasal": False},
    
    # Zero initial (Y, W)
    "y": {"name": "y", "retroflex": False, "nasal": False},
    "w": {"name": "w", "retroflex": False, "nasal": False},
}

# Finals (韵母) categories
FINALS = {
    # Simple vowels
    "a": {"name": "a", "nasal": False},
    "o": {"name": "o", "nasal": False},
    "e": {"name": "e", "nasal": False},
    "i": {"name": "i", "nasal": False},
    "u": {"name": "u", "nasal": False},
    "ü": {"name": "ü", "nasal": False},
    
    # Compound finals
    "ai": {"name": "ai", "nasal": False},
    "ei": {"name": "ei", "nasal": False},
    "ui": {"name": "ui", "nasal": False},
    "ao": {"name": "ao", "nasal": False},
    "ou": {"name": "ou", "nasal": False},
    "iu": {"name": "iu", "nasal": False},
    "ie": {"name": "ie", "nasal": False},
    "üe": {"name": "üe", "nasal": False},
    "er": {"name": "er", "nasal": False},
    
    # Nasal finals (鼻音韵母) - difficult for Cantonese
    "an": {"name": "an", "nasal": True},
    "en": {"name": "en", "nasal": True},
    "in": {"name": "in", "nasal": True},
    "un": {"name": "un", "nasal": True},
    "ün": {"name": "ün", "nasal": True},
    
    # Nasal-ng finals
    "ang": {"name": "ang", "nasal": True},
    "eng": {"name": "eng", "nasal": True},
    "ing": {"name": "ing", "nasal": True},
    "ong": {"name": "ong", "nasal": True},
}


def get_initial(pinyin: str) -> str:
    """Extract initial from pinyin"""
    if not pinyin:
        return ""
    
    # Check for retroflex initials (zh, ch, sh, r)
    if len(pinyin) >= 2 and pinyin[:2] in INITIALS:
        return pinyin[:2]
    
    # Check for single letter initial
    if pinyin[0] in INITIALS:
        return pinyin[0]
    
    return ""


def get_final(pinyin: str) -> str:
    """Extract final from pinyin"""
    initial = get_initial(pinyin)
    if initial:
        return pinyin[len(initial):]
    return pinyin


def is_retroflex(pinyin: str) -> bool:
    """Check if pinyin has retroflex initial"""
    if not pinyin or not isinstance(pinyin, str):
        return False
    initial = get_initial(pinyin)
    return INITIALS.get(initial, {}).get("retroflex", False)


def is_nasal(pinyin: str) -> bool:
    """Check if pinyin has nasal final"""
    if not pinyin or not isinstance(pinyin, str):
        return False
    final = get_final(pinyin)
    if not isinstance(final, str):
        return False
    return FINALS.get(final, {}).get("nasal", False)


def get_char_info(char: str) -> dict:
    """Get pinyin and tone info for a character"""
    from pypinyin import Style, pinyin
    
    # Get pinyin with tone number
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
    tone = 0
    pinyin_base = pinyin_str
    if pinyin_str:
        # Tone is the last character if it's a digit
        if pinyin_str[-1].isdigit():
            tone = int(pinyin_str[-1])
            pinyin_base = pinyin_str[:-1]
    
    return {
        "char": char,
        "pinyin": pinyin_str,
        "pinyin_base": pinyin_base if 'pinyin_base' in locals() else pinyin_str,
        "tone": tone,
        "initial": get_initial(pinyin_str),
        "final": get_final(pinyin_str),
        "is_retroflex": is_retroflex(pinyin_str),
        "is_nasal": is_nasal(pinyin_str)
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


def get_common_words() -> list:
    """Get common PSC test words with their pinyin"""
    # This would be a larger database in production
    return [
        ("春天来了", ["chun", "tian", "lai", "le"]),
        ("花儿开了", ["hua", "er", "kai", "le"]),
        ("鸟儿在树枝上唱歌", ["niao", "er", "zai", "shu", "zhi", "shang", "chang", "ge"]),
    ]


# PSC Section 1: Common single characters (100 characters)
PSC_SINGLE_CHARS = [
    "八,ba,1", "七,qi,1", "六,liu,4", "五,wu,3", "四,si,4",
    "三,san,1", "二,er,4", "一,yi,1", "九,jiu,3", "十,shi,2",
    "百,bai,3", "千,qian,1", "万,wan,4", "亿,yi,4", "零,ling,2",
    "大,da,4", "小,xiao,3", "中,zhong,1", "上,shang,4", "下,xia,4",
    "天,tian,1", "地,di,4", "人,ren,2", "我,wo,3", "你,ni,3",
    "他,ta,1", "她,ta,1", "它,ta,1", "们,men,0", "的,de,0",
    "了,le,0", "在,zai,4", "有,you,3", "和,he,2", "是,shi,4",
    "我,wo,3", "你,ni,3", "他,ta,1", "她,ta,1", "它,ta,1",
    "这,zhe,4", "那,na,4", "哪,na,3", "谁,shui,2", "什么,shenme,2",
    "怎,zen,3", "么,me,0", "为,wei,4", "什,shen,2", "么,me,0",
    "吗,ma,0", "呢,ne,0", "吧,ba,0", "啊,a,0", "哦,o,4",
    "嗯,en,0", "哈,ha,1", "喂,wei,4", "嘿,hei,1", "哼,heng,4",
]

# More comprehensive database would include all PSC test characters


def load_psc_char_database() -> dict:
    """Load PSC character database"""
    db = {}
    for item in PSC_SINGLE_CHARS:
        parts = item.split(",")
        if len(parts) >= 3:
            char, pinyin, tone = parts
            db[char] = {
                "pinyin": pinyin,
                "tone": int(tone),
                "initial": get_initial(pinyin),
                "final": get_final(pinyin),
                "is_retroflex": is_retroflex(pinyin),
                "is_nasal": is_nasal(pinyin)
            }
    return db
