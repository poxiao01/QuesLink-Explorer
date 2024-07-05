from check.check_dfs_counts import check_data_legality, validate_element_counts_list_against_db
from data_processing.data_loader import process_data_to_list
from data_processing.data_save import save_list_as_whole
from utils.Trie_tree import mining

if __name__ == '__main__':
    # 设置数据文件的路径以及需要在处理过程中忽略的列名
    file_path = "../data/sentences_data.csv"
    ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
    # 调用函数处理数据文件，并将处理后的数据存储为列表
    processed_data_list = process_data_to_list(file_path, ignore_columns)

    # 基于处理后的数据，寻找出现频率较高的模式（频繁项集），参数2表示支持度阈值
    data_list, rules = mining(processed_data_list, 2, 0.8)

    # 对生成的数据列表进行合法性检查，确保数据格式正确无误
    check_data_legality(data_list)

    # 验证频繁项集中各元素的数量是否与数据库中的记录相符，以确保数据准确性
    validate_element_counts_list_against_db(data_list)

    # 检验生成的关联规则是否合法，即是否与数据库中的信息相匹配
    rules.check_rules_against_db()

    # 检查对应关联规则的倒排索引是否合法
    rules.check_inverted_index_consistency()

    # 保存关联规则和倒排索引s
    rules.save_file('../data/Rules')

    # 将处理后的频繁项集数据保存为JSON格式文件
    save_list_as_whole(data_list, '../data/Frequent_itemsets.json')
