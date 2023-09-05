import re

calorie="220kcal"

test=re.search(r'当り(.+)kcal',calorie).group(1)
print(test)