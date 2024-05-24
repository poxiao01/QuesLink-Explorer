import pyfpgrowth

from data_processing.data_loader import process_dataframe

# 指定CSV文件的路径
file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"

# 列出你想要忽略的列名
ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']

transactions = process_dataframe(file_path, ignore_columns)
transactions_str_list = [[str(element) for element in sublist] for sublist in transactions]
# 设置支持度阈值，这里我们使用2作为最小支持度
min_support = 2

# 使用pyfpgrowth找出频繁项集和它们的支持度
patterns_dict = pyfpgrowth.find_frequent_patterns(transactions_str_list, min_support)

# 筛选出包含 'QUESTION' 的频繁项集
question_patterns = [
    (itemset, support)
    for itemset, support in patterns_dict.items()
    if any('QUESTION' in str(item) for item in itemset)
]
for itemset, support in question_patterns:
    if support >= 300:
        print(f"项集: {itemset}, 支持度: {support}")

# 使用pyfpgrowth生成关联规则
rules = pyfpgrowth.generate_association_rules(patterns_dict, 0.8)

# 打印rules的内容，以便检查数据格式
for rule in rules:
    print(rule)

