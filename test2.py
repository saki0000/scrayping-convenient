import re

import pykakasi

kks = pykakasi.kakasi()

calorie="220kcal"
name="ロッテ　雪見だいふく　コクのショコラ"

result = kks.convert(name)
words=""
for w in result:
    words+=w["kana"]
print(words)