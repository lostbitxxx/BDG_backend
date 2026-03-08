"""
Classifier (量詞) and Noun Matching Database for PSC Section 3
Used for 量詞搭配 (quantifier/noun matching) questions.
Maps nouns to their correct measure words in Standard Mandarin.
"""

# Classifier to noun mapping
# Format: classifier: [list of nouns that use this classifier]
CLASSIFIER_NOUNS = {
    "個": [
        "蘋果", "橙", "香蕉", "梨", "西瓜", "瓜", "球", "蘋果",
        "人", "男人", "女人", "孩子", "學生", "老師", "朋友",
        "問題", "事情", "東西", "禮物", "電話", "電視", "電腦",
        "杯子", "碗", "盤子", "椅子", "桌子", "床", "沙發",
        "城市", "村莊", "國家", "公司", "學校", "醫院", "銀行",
        "袋子", "盒子", "箱子", "瓶子", "罐子", "杯子",
        "眼睛", "耳朵", "嘴巴", "鼻子", "腦袋", "心",
    ],
    "張": [
        "桌子", "椅子", "床", "沙發", "紙", "報紙", "書",
        "照片", "圖片", "地圖", "畫", "牛皮癬", "涼蓆",
        "嘴", "名片", "假條", "罰單", "清單",
    ],
    "條": [
        "褲子", "裙子", "裙子", "領帶", "圍巾", "毛巾", "手帕",
        "魚", "蛇", "蟲", "龍", "黃瓜", "茄子", "蘿蔔",
        "河", "江", "湖", "海", "溝", "渠", "巷", "街",
        "路", "高速公路", "鐵路", "隧道", "橋", "繩子", "帶子",
        "項鏈", "裙子", "口袋", "牙膏", "鼻涕", "口水",
    ],
    "把": [
        "椅子", "扇子", "傘", "刀", "剪刀", "鎖", "鑰匙",
        "力氣", "功夫", "刷子", "鏟子", "勺子", "鏟子",
        "沙子", "泥土", "米", "麵粉", "食鹽", "白糖",
    ],
    "輛": [
        "汽車", "自行車", "摩托車", "公交車", "卡車", "出租車",
        "拖拉機", "救護車", "警車", "消防車", "火車",
    ],
    "架": [
        "飛機", "坦克", "鋼琴", "提琴", "收音機", "電視機",
        "照相機", "攝像機", "織布機", "機器", "儀器",
    ],
    "艘": [
        "船", "輪船", "艦艇", "軍艦", "遊艇", "帆船",
    ],
    "匹": [
        "馬", "綢", "緞", "布料", "馬匹",
    ],
    "頭": [
        "牛", "羊", "豬", "狗", "貓", "驢", "馬", "駱駝", "象",
    ],
    "隻": [
        "鳥", "雞", "鴨", "鵝", "兔子", "老鼠", "螞蟻", "蟲",
        "狗", "貓", "魚", "青蛙", "烏龜", "螃蟹", "蝦",
        "手", "腳", "眼睛", "耳朵", "嘴巴", "鼻子",
        "襪子", "鞋子", "手套", "帽子", "圍巾",
        "船", "飛機", "船上", "船上",
    ],
    "件": [
        "衣服", "襯衫", "褲子", "裙子", "外套", "大衣", "西裝",
        "事", "工作", "事", "案件", "行李", "禮物",
    ],
    "件": [
        "襖", "棉襖", "皮襖", "羽絨服",
    ],
    "雙": [
        "筷子", "襪子", "鞋子", "手套", "眼睛", "耳朵", "眉毛",
    ],
    "副": [
        "眼鏡", "手套", "對聯", "牌", "扑克牌", "象棋", "圍棋",
    ],
    "套": [
        "房子", "家具", "衣服", "書", "電視劇", "電影", "郵票",
    ],
    "本": [
        "書", "雜誌", "字典", "詞典", "筆記本", "練習本",
    ],
    "支": [
        "筆", "香菸", "菸", "蠟燭", "笛子", "小提琴",
    ],
    "枝": [
        "筆", "香菸", "花", "樹", "木", "竹子",
    ],
    "把": [
        "刀", "剪刀", "傘", "扇子", "鎖", "鑰匙", "椅子",
    ],
    "口": [
        "人", "井", "棺材", "豬", "氣", "話",
    ],
    "位": [
        "客人", "老師", "學生", "醫生", "律師", "教授", "總統",
        "總理", "部長", "局長", "處長", "隊長", "船長",
    ],
    "名": [
        "學生", "士兵", "警察", "醫生", "護士", "工人", "農民",
    ],
    "位": [
        "乘客", "旅客", "參觀者", "參賽者", "獲獎者",
    ],
    "種": [
        "人", "動物", "植物", "語言", "方法", "思想", "感情",
        "顏色", "味道", "氣味", "聲音", "語言", "話",
    ],
    "類": [
        "人", "東西", "事情", "問題", "動物", "植物", "書籍",
    ],
    "樣": [
        "東西", "事情", "禮物", "菜", "點心", "水果", "家具",
    ],
    "些": [
        "人", "東西", "事情", "書", "話", "問題",
    ],
    "點兒": [
        "東西", "事情", "活", "毛病", "錯誤",
    ],
}

# Reverse mapping: noun -> classifier
NOUN_TO_CLASSIFIER = {}
for classifier, nouns in CLASSIFIER_NOUNS.items():
    for noun in nouns:
        if noun not in NOUN_TO_CLASSIFIER:
            NOUN_TO_CLASSIFIER[noun] = classifier
        else:
            # Keep both if multiple classifiers exist
            if isinstance(NOUN_TO_CLASSIFIER[noun], str):
                NOUN_TO_CLASSIFIER[noun] = [NOUN_TO_CLASSIFIER[noun], classifier]
            else:
                NOUN_TO_CLASSIFIER[noun].append(classifier)

# Common classifier errors for Cantonese speakers
COMMON_CLASSIFIER_ERRORS = {
    # Cantonese speakers often use wrong classifiers
    "一張魚": "一條魚",
    "一個飛機": "一架飛機",
    "一隻車": "一輛車",
    "一張椅子": "一把椅子",
    "一個人 (but counting)": "一口人",
    "一件衣服 (correct)": "一件衣服",  # This one is correct
    "一條衣服": "一件衣服",  # Wrong - clothes use 件
}

def get_classifier_for_noun(noun: str) -> str:
    """Get the correct classifier for a noun"""
    return NOUN_TO_CLASSIFIER.get(noun, "")

def get_nouns_for_classifier(classifier: str) -> list:
    """Get all nouns that use a specific classifier"""
    return CLASSIFIER_NOUNS.get(classifier, [])

def is_correct_classifier(noun: str, classifier: str) -> bool:
    """Check if the classifier is correct for the noun"""
    correct = get_classifier_for_noun(noun)
    if isinstance(correct, list):
        return classifier in correct
    return classifier == correct

def get_all_classifiers() -> list:
    """Get list of all classifiers"""
    return list(CLASSIFIER_NOUNS.keys())

def get_all_nouns() -> list:
    """Get list of all nouns"""
    return list(NOUN_TO_CLASSIFIER.keys())
