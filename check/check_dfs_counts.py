from db.DbAccessor import count_rows_by_conditions


def validate_element_counts_dict_against_db(element_counts_dict):
    """
    验证处理后的所有频繁集是否与数据库中的实际记录数相符。

    :return: 无返回值

    """

    # 遍历所有频繁项集，验证与数据库记录数的一致性
    for key, expected_count in element_counts_dict.items():
        elements_tuple = key

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
            f"错误！element_counts_dict的数据与数据库中的记录")
    print(f"validate_element_counts_dict_against_db函数 运行结束，所有频繁集验证通过！")


def validate_element_counts_list_against_db(element_counts_list):
    """
    验证处理后的频繁项集列表中的每一项与其在数据库中的实际记录数是否一致。

    参数:
        element_counts_list (list): 一个列表，其中每个元素为一个元组，包含两个部分：
                                   第一部分为一个元组，代表SQL查询中的条件（列名和对应的值）；
                                   第二部分为预期的数据库记录数量。

    :return: 无返回值，直接通过assert断言验证结果正确性。

    功能说明:
        1. 遍历`element_counts_list`中的每个元素，该元素由一个条件元组和一个期望计数组成。
        2. 对于每个条件元组，动态构建一个WHERE子句，其中字符串类型的值被适当引用以避免SQL语法错误。
        3. 使用构建的WHERE子句查询数据库，获取实际的记录数。
        4. 将查询到的数据库记录数与预期计数进行对比，若不符则抛出异常，并打印错误详情。
        5. 所有频繁集验证完毕后，打印成功信息。
    """

    # 遍历所有频繁项集，验证与数据库记录数的一致性
    for elements_tuple, expected_count in element_counts_list:
        # 构建WHERE子句的条件列表，确保字符串值被正确引用
        where_conditions = [f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                            for col, val in elements_tuple]
        # 组合所有条件为完整的WHERE子句
        where_clause = ' AND '.join(where_conditions)
        # 从数据库中获取满足WHERE子句的行数
        db_count = count_rows_by_conditions(where_clause)

        # 比较并断言数据库中的行数与期望计数相等
        assert db_count == expected_count, (
            f"WHERE子句: {where_clause}\n数据库实际计数: {db_count}, 预期计数: {expected_count}\n"
            f"验证错误！数据与数据库记录数不符，请检查element_counts_list配置。")

    # 如果所有验证均通过，则打印成功消息
    print("validate_element_counts_list_against_db函数 运行完毕，所有频繁集验证一致，数据校验成功！")


def validate_rules_against_db(rules):
    for key, consequent in rules.rules_dict.items():
        for value in consequent:
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


def check_data_legality(data_list):
    """
    使用断言检查数据合法性函数。
    """
    unique_sorted_rows = set()

    for row_data, _ in data_list:
        # 构建用于检查列名重复的集合
        column_name_set = set()
        for column_name in row_data:
            # 断言检查当前行内列名重复
            assert column_name not in column_name_set, f"一行数据中发现重复的列名！ -> {column_name}"
            column_name_set.add(column_name)

        # 转换为不可变集合，准备检查重复
        sorted_row_frozenset = frozenset(row_data)

        # 断言检查整个数据集中的重复行
        assert sorted_row_frozenset not in unique_sorted_rows, f"发现重复的行（按列名排序后）：{sorted_row_frozenset}"
        unique_sorted_rows.add(sorted_row_frozenset)
