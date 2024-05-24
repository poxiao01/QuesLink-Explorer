import pandas as pd

import pandas as pd


def process_data_to_list(file_path, ignore_columns):
    """
    读取CSV文件，处理DataFrame，并返回处理后的行数据，并按照含有 'QUESTION' 的行优先排序。

    :param file_path: str，CSV文件的路径
    :param ignore_columns: list，需要忽略的列名列表
    :return: list，包含处理后的行数据的列表，整体按照含有 'QUESTION' 的行优先排序 去除不含有 'QUESTION' 的所有行
    """
    df = pd.read_csv(file_path)
    df = df.drop(columns=ignore_columns)
    processed_rows = []

    # 收集所有处理后的行，但不在此处排序
    for index, row in df.iterrows():
        temp_list = [(column_name, value) for column_name, value in row.items()
                     if not (isinstance(value, int) and value == 0) and not (
                    column_name == 'DEPENDENCY_PATH' and value == '[]')]
        # 对每一行内部的元素进行排序，优先考虑包含 'QUESTION' 的元素
        temp_list.sort(key=lambda x: (('QUESTION' in x[0]), str(x[1])), reverse=True)
        if len(temp_list) == 0 or temp_list[0][0].find('QUESTION') == -1:
            continue
        processed_rows.append(temp_list)

    return processed_rows


def permute_dfs(elements, depth, path, useful_mark, element_counts):
    """
    递归生成元素的排列组合，并统计每个排列的出现次数。

    :param elements: list，待排列的元素列表
    :param depth: int，当前递归深度
    :param path: list，当前排列路径
    :param useful_mark: bool，标记当前元素是否有效
    :param element_counts: dict，存储每个排列及其出现次数的字典
    """
    if depth == len(elements):
        str_path = str(path)
        if str_path not in element_counts:
            element_counts[str_path] = 1
        else:
            element_counts[str_path] += 1
        return

    if useful_mark:
        # 选
        path.append(elements[depth])
        permute_dfs(elements, depth + 1, path, True, element_counts)
        path.pop()

        # 不选
        permute_dfs(elements, depth + 1, path, True, element_counts)

    else:
        if elements[depth][0].find('QUESTION') != -1:
            # 选
            path.append(elements[depth])
            permute_dfs(elements, depth + 1, path, True, element_counts)
            path.pop()

            # 不选
            permute_dfs(elements, depth + 1, path, useful_mark, element_counts)


def process_data_to_dict(file_path, ignore_columns):
    """
      读取CSV文件，处理DataFrame，并返回处理后的行数据。

      :param file_path: str，CSV文件的路径
      :param ignore_columns: list，需要忽略的列名列表
      :return: list，包含处理后的行数据的列表

      示例：

      file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"
      ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
      processed_data = process_data_to_dict(file_path, ignore_columns)
      """
    # 读取CSV文件并删除指定的列
    df = pd.read_csv(file_path).drop(columns=ignore_columns)
    columns_names = df.columns.tolist()

    # 筛选出包含 'QUESTION' 的列名
    useful_columns_names = [name for name in columns_names if name.find('QUESTION') != -1]

    # 创建一个字典，将列名映射到它们在 useful_columns_names 列表中的索引位置
    column_order = {name: i for i, name in enumerate(useful_columns_names)}

    # 使用列表推导式处理每一行数据
    processed_rows = [
        sorted(((column_name, value.lower() if isinstance(value, str) else str(value))
                for column_name, value in row.items()
                if not (isinstance(value, int) and value == 0) and not (
                column_name == 'DEPENDENCY_PATH' and value == '[]')),  # 排除整数且值为0，以及'DEPENDENCY_PATH'为'[]'的情况
               key=lambda x: (column_order.get(x[0], float('inf')), str(x[1])))  # 转换所有值为字符串进行排序
        for _, row in df.iterrows()
    ]
    element_counts = dict()
    for row_list in processed_rows:
        permute_dfs(row_list, 0, [], False, element_counts)
    return element_counts

# file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"
# ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
# processed_data = process_data_to_dict(file_path, ignore_columns)
