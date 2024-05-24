from data_processing.data_loader import process_data_to_dict
from data_processing.data_save import save_dict_to_json_sorted_by_value
from db.DbAccessor import count_rows_by_conditions


def validate_element_counts_against_db(file_path, ignore_columns):
    """
    验证处理后的排列组合计数是否与数据库中的实际记录数相符。

    :type ignore_columns: object
    :param file_path: str，CSV文件路径
    :param ignore_columns: list，需要忽略的列名列表
    :return: 返回一个记录出现次数的字典

    步骤：
    1. 从指定CSV文件读取数据，处理并获得排列组合及其计数。
    2. 遍历每种排列组合，构造相应的SQL WHERE子句。
    3. 使用DbAccessor查询数据库中满足条件的记录数。
    4. 比较预期计数与实际计数，打印出任何不匹配的情况。
    """

    # 处理数据并获取排列组合及其计数的字典
    element_counts = process_data_to_dict(file_path, ignore_columns)
    # 遍历每种排列组合及其计数，验证与数据库记录数的一致性
    for key, expected_count in element_counts.items():
        # 将字符串形式的排列组合键转换为列表
        elements_tuple = eval(key)

        # 构建WHERE子句的条件列表，同时转换布尔字符串为数字
        where_conditions = [f"{col} = {int(val == 'True')}" if val in ['True', 'False'] else f"{col} = '{val}'"
                            for col, val in elements_tuple]

        # 组合所有条件为完整的WHERE子句
        where_clause = ' AND '.join(where_conditions)

        # 从数据库中获取满足WHERE子句的行数
        db_count = count_rows_by_conditions(where_clause)

        # 比较数据库中的行数与处理后的数据字典中的值
        assert db_count == expected_count, (
            f"WHERE子句: {where_clause}\n数据库计数: {db_count}, 预期计数: {expected_count}\n"
            f"错误！element_counts的数据与数据库中的记录")
    print(f'validate_element_counts_against_db函数 运行结束，数据预期正常！')

    # 筛选出 出现次数大于1的项
    filtered_element_counts = {key: value for key, value in element_counts.items() if value > 1}

    return filtered_element_counts


def validate_rules_against_db(rules_dict):
    for key, value in rules_dict.items():
        where_conditions_key = [f"{col} = {int(val == 'True')}" if val in ['True', 'False'] else f"{col} = '{val}'"
                                for col, val in key]
        where_conditions_value = where_conditions_key + [
            f"{col} = {int(val == 'True')}" if val in ['True', 'False'] else f"{col} = '{val}'"
            for col, val in value[0]]

        # 组合所有条件为完整的WHERE子句
        where_clause_key = ' AND '.join(where_conditions_key)
        where_clause_value = ' AND '.join(where_conditions_value)

        # 从数据库中获取满足WHERE子句的行数
        db_count_key = count_rows_by_conditions(where_clause_key)
        db_count_value = count_rows_by_conditions(where_clause_value)

        # 调整 assert 语句中的打印信息
        assert db_count_value / db_count_key == value[1], (
            f"规则键的WHERE子句: {where_clause_key}\n规则值的WHERE子句: {where_clause_value}\n"
            f"规则键的数据库计数: {db_count_key}, 规则值的数据库计数: {db_count_value}\n"
            f"预期置信度: {value[1]}\n"
            f"实际置信度：{db_count_value / db_count_key}\n"
            f"错误！规则的置信度与数据库中的记录不匹配")

    print("validate_rules_against_db函数 运行结束，所有规则验证通过！")



if __name__ == '__main__':
    # 指定CSV文件路径和忽略的列
    file_path_ = "E:/QuesLink_Explorer/data/sentences_data.csv"
    ignore_columns_ = ['ID', 'SENTENCE', 'QUESTION_WORD']

    # 调用函数执行验证
    # counts_dict = validate_element_counts_against_db(file_path_, ignore_columns_)
    # save_dict_to_json_sorted_by_value('E:/QuesLink_Explorer/data/target_data.JSON', counts_dict, reverse=True)

    element_counts_ = process_data_to_dict(file_path_, ignore_columns_)
    print(len(element_counts_))
