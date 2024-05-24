from pyfpgrowth import find_frequent_patterns
from pyfpgrowth import generate_association_rules

from data_processing.data_loader import process_data_to_list

# 假设我们有一个简单的交易数据集
transactions = [
    ['牛奶', '面包', '黄油'],
    ['牛奶', '尿布', '啤酒', '鸡蛋'],
]

file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"
ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
processed_data = process_data_to_list(file_path, ignore_columns)


# 使用FP-Growth算法挖掘频繁项集，设置最小支持度为2（即至少出现在2个交易中）
frequent_patterns = find_frequent_patterns(processed_data, 2)
rules_dict = generate_association_rules(frequent_patterns, 0.8)
print(len(rules_dict))

temp_list = []
for key,value in rules_dict.items():
    ok = True
    for p in key:
        if str(p[0]).find('QUESTION') == -1:
            ok = False
            break
    if not ok:
        temp_list.append(key)
        continue
    for p in value[0]:
        if str(p[0]).find('QUESTION') != -1:
            ok = False
            break
    if not ok:
        temp_list.append(key)
        continue
    # print(f'{key} —> {value[0]}, 置信度：{value[1]}')

for x in temp_list:
    del rules_dict[x]

for key,value in rules_dict.items():
    print(f'{key} —> {value[0]}, 置信度：{value[1]}')
print(len(rules_dict))

