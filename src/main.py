import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth

from data_processing.data_loader import process_dataframe

# 指定CSV文件的路径
file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"

# 列出你想要忽略的列名
ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']

# 读取并处理数据
data = process_dataframe(file_path, ignore_columns)

# 使用 TransactionEncoder 将列表转换为二进制 DataFrame
te = TransactionEncoder()
te_ary = te.fit(data).transform(data)
df = pd.DataFrame(te_ary, columns=te.columns_)

# 现在 df 是一个二进制 DataFrame，适合用于 FP-tree 算法

# 使用 fpgrowth 函数来发现频繁项集
frequent_itemsets = fpgrowth(df, min_support=0.1, use_colnames=True)

# 按支持度对频繁项集进行排序
frequent_itemsets_sorted = frequent_itemsets.sort_values(by='support', ascending=False)

# 打印排序后的频繁项集
for index, row in frequent_itemsets_sorted.iterrows():
    print(f"support: {row['support']}")
    print("itemsets:", str(row['itemsets']))

    print('-----------------------\n')
