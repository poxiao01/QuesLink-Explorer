from data_processing.data_loader import process_data_to_dict
from db.DbAccessor import count_rows_by_conditions


def validate_element_counts_against_db(file_path, ignore_columns):
    """
    验证处理后的排列组合计数是否与数据库中的实际记录数相符。

    :type ignore_columns: object
    :param file_path: str，CSV文件路径
    :param ignore_columns: list，需要忽略的列名列表
    :return: 无返回值，直接打印出不匹配的情况

    步骤：
    1. 从指定CSV文件读取数据，处理并获得排列组合及其计数。
    2. 遍历每种排列组合，构造相应的SQL WHERE子句。
    3. 使用DbAccessor查询数据库中满足条件的记录数。
    4. 比较预期计数与实际计数，打印出任何不匹配的情况。
    """

    # 处理数据并获取排列组合及其计数的字典
    element_counts = process_data_to_dict(file_path, ignore_columns)
    print(len(element_counts))
    # 遍历每种排列组合及其计数，验证与数据库记录数的一致性
    for key, expected_count in element_counts.items():
        # 将字符串形式的排列组合键转换为列表
        elements_tuple = eval(key)

        # 构建WHERE子句的条件列表，同时转换布尔字符串为数字
        where_conditions = [f"{col} = {int(val == 'True')}" if val in ['True', 'False'] else f"{col} = '{val}'"
                            for col, val in elements_tuple]

        # 组合所有条件为完整的WHERE子句
        where_clause = ' AND '.join(where_conditions)

        # 查询数据库中满足该条件的实际记录数
        actual_count = count_rows_by_conditions(where_clause)

        # 比较预期计数与实际计数，打印差异
        if actual_count != expected_count:
            print(f"WHERE子句: {where_clause}")
            print(f"数据库计数: {actual_count}, 预期计数: {expected_count}")
            print("错误！element_counts的数据与数据库中的记录数不符！")
            break  # 发现不匹配后立即停止验证
    print(f'validate_element_counts_against_db函数 运行结束，数据预期正常！')


# 指定CSV文件路径和忽略的列
file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"
ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']

# 调用函数执行验证
validate_element_counts_against_db(file_path, ignore_columns)
