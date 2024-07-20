import pandas as pd


def process_data_to_list(file_path, ignore_columns):
    """
    :param file_path: str，CSV文件的路径
    :param ignore_columns: list，需要忽略的列名列表
    :return: list，包含处理后的行数据的列表，整体按照含有 'QUESTION' 的行优先排序
    """
    df = pd.read_csv(file_path)
    df = df.drop(columns=ignore_columns)
    processed_rows = []

    for index, row in df.iterrows():
        temp_list = [(column_name, str(value)) for column_name, value in row.items()
                     if not (isinstance(value, int) and value == 0) and not (
                    column_name == 'DEPENDENCY_PATH' and value == '[]')]
        processed_rows.append(temp_list)

    return processed_rows

