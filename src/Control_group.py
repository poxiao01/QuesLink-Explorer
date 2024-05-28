from pyfpgrowth import find_frequent_patterns, generate_association_rules

from check.check_dfs_counts import validate_element_counts_dict_against_db, validate_rules_against_db
from data_processing.data_loader import process_data_to_list
from data_processing.data_save import save_dict_to_json

if __name__ == '__main__':
    # 定义数据文件路径和需要忽略的列
    file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"
    ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
    # 加载并初步处理数据(忽略某些列)
    processed_data = process_data_to_list(file_path, ignore_columns)
    # 使用FP-Growth算法挖掘频繁项集，设置最小支持度为2
    frequent_patterns = find_frequent_patterns(processed_data, 2)

    # 验证筛选后的频繁集
    validate_element_counts_dict_against_db(frequent_patterns)

    # 生成关联规则，设置最小置信度为0.8
    rules_dict = generate_association_rules(frequent_patterns, 0.8)

    # 筛选出满足条件的关联规则：前件全部不包含 'QUESTION'，后件全部为包含 'QUESTION'
    # 关联规则：{前件: 后件, 置信度}
    filtered_rules_dict = {}
    for key, value in rules_dict.items():
        # key 是前件，value[0] 是后件，value[1] 是置信度
        if all(str(p[0]).find('QUESTION') == -1 for p in key) and all(
                str(p[0]).find('QUESTION') != -1 for p in value[0]):
            filtered_rules_dict[key] = value

    # 验证筛选后的关联规则
    validate_rules_against_db(filtered_rules_dict)

    # 保存筛选后的频繁集到JSON文件
    save_dict_to_json(frequent_patterns, 'E:/QuesLink_Explorer/data/Frequent_itemsets_two.JSON')

    # 保存筛选后的关联规则到JSON文件
    save_dict_to_json(filtered_rules_dict, 'E:/QuesLink_Explorer/data/Rules_two.JSON', reverse=True)
