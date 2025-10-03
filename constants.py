from re import fullmatch as fm
from configparser import ConfigParser
from time import time

DICT_PATH = "jisho.dic"
ENCODING = "shift_JIS"
TRANS = {
    "？": "?",
    "⋆": "*",
    "＊": "*",
    "【": "[",
    "】": "]",
    "「": "[",
    "」": "]",
    "『": "[",
    "』": "]",
    "＆": "&",
    "｜": "|",
    "！": "!",
    "（": "(",
    "）": ")",
    "《": "<",
    "》": ">",
    "＜": "<",
    "＞": ">",
    "＠": "@",
    "；": ";",
    "＝": "=",
    "“": "\"",
    "”": "\"",
    "‘": "\'",
    "’": "\'",
    "｛": "{",
    "｝": "}",
    "０": "0",
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "０": "0"

}

PI = 3.1415927 # 悄悄藏一个π

KANA = set("あいうえおかがきぎくぐけげこごさざしじすずせぜそぞただちぢつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもやゆよらりるれろわをんー")

ULETTER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LLETTER = set("abcdefghijklmnopqrstuvwxyz")

PUNC = set("?*[-]&|!()<>@;=\"\'{}")

NUM = set("0123456789")

ALLOW = KANA | ULETTER | LLETTER | PUNC | NUM

# x for [aa], q for [nn]
L2K = {
    "x": "あいうえお",
    "k": "かきくけこ",
    "s": "さしすせそ",
    "t": "たちつてと",
    "n": "なにぬねの",
    "h": "はひふへほ",
    "m": "まみむめも",
    "y": "やゆよ",
    "r": "らりるれろ",
    "w": "わを",
    "g": "がぎぐげご",
    "z": "ざじずぜぞ",
    "d": "だぢづでど",
    "b": "ばびぶべぼ",
    "p": "ぱぴぷぺぽ",
    "a": "あかさたなはまやらわがざだばぱ",
    "i": "いきしちにひみりぎじぢびぴ",
    "u": "うくすつぬふむゆるぐずづぶぷ",
    "e": "えけせてねへめよれげぜでべぺ",
    "o": "おこそとのほもよろをごぞどぼぽ",
    "q": "ん"
}

TIME_LIMIT = 20 # 20s

for i in ALLOW:
    TRANS[i] = i

# Read File
with open(DICT_PATH, 'r', encoding=ENCODING) as f:
    file = f.readlines()
dict = [i.strip() for i in file]

# Hash Table
hasht = {}
for i in dict:
    hasht[hash(i)] = i

# Create indices for faster lookup
dict_by_length = {}
dict_by_first_char = {}
for word in dict:
    # Index by length
    length = len(word)
    if length not in dict_by_length:
        dict_by_length[length] = []
    dict_by_length[length].append(word)
    
    # Index by first character
    if word:
        first_char = word[0]
        if first_char not in dict_by_first_char:
            dict_by_first_char[first_char] = []
        dict_by_first_char[first_char].append(word)

# i18n
config = ConfigParser()
config.read("./i18n.cfg",encoding="utf-8")