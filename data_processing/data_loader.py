import pandas as pd

import pandas as pd


def process_data_to_list(file_path, ignore_columns):
    """
    读取CSV文件，处理DataFrame，并返回处理后的行数据，并按照含有 'QUESTION' 的行优先排序。

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


def permute_dfs(elements, depth, path, useful_mark, element_counts, count_):
    """
    递归生成元素的排列组合，并统计每个排列的出现次数。

    :param elements: frozenset，待排列的元素列表
    :param depth: int，当前递归深度
    :param path: list，当前排列路径
    :param useful_mark: bool，标记当前元素是否有效
    :param element_counts: dict，存储每个排列及其出现次数的列表
    """
    if depth == len(elements):
        frozenset_path = frozenset(path)
        if frozenset_path not in element_counts:
            element_counts[frozenset_path] = count_
        else:
            element_counts[frozenset_path] += count_
        return

    # 当前元素有效或为特定情况（如包含 'QUESTION'）时进行选择或不选择的递归
    if useful_mark or elements[depth][0].find('QUESTION') != -1:
        # 选
        path.append(elements[depth])
        permute_dfs(elements, depth + 1, path, True, element_counts, count_)
        path.pop()

        # 不选，只有在当前元素标记为有用时才进行不选的递归，避免无限递归
        permute_dfs(elements, depth + 1, path, useful_mark, element_counts, count_)


def generate_frequent_itemsets(file_path, ignore_columns, min_support=2):
    """
    从CSV文件中读取数据，处理特定列，并生成频繁项集的计数。

    函数首先读取指定路径的CSV文件，并移除指定的列。接着，针对剩余列中包含 'QUESTION' 的列进行处理，
    接着筛选出满足最小支持度的所有数据行
    生成每一行的数据组合（移除值为0的整数项和特定标记的'DEPENDENCY_PATH'项），并将这些组合按照预定义顺序排序，
    转换为不可变集合(frozenset)以便计数。最后，通过递归函数`permute_dfs`进一步处理这些集合，
    以生成满足最小支持度的频繁项集，并返回这些项集及其支持度的字典。

    :param file_path: str, CSV文件的路径。
    :param ignore_columns: list, 在处理过程中需要忽略的列名列表。
    :param min_support: int 或 float, 频繁项集的最小支持度阈值，默认为2，意味着至少需要出现两次。
    :return: dict, 频繁项集及其支持度的字典，键为frozenset形式的项集，值为支持度计数。

    注意:
    - `permute_dfs`函数应当负责递归地组合项集。
    - 列名中包含 'QUESTION' 的列被视为有效列进行分析。
    - 数据处理阶段会过滤掉值为0的整数型数据以及标记为'[]'的'DEPENDENCY_PATH'列。
    """
    # 使用pandas读取CSV文件并删除指定的列
    df = pd.read_csv(file_path)
    df = df.drop(columns=ignore_columns)  # 删除指定的列
    columns_names = df.columns.tolist()   # 有用的全部列名

    # 筛选以 'QUESTION' 开头的列名
    question_columns = [col for col in df.columns if 'QUESTION' in col]

    columns_names.sort(key=lambda x: float('inf') if x not in question_columns else question_columns.index(x))

    # 初始化处理后的数据列表， 用来暂时存放数据，便于后续筛选出大于等于最小支持度的全部项
    processed_data_list = []
    element_counts = {}

    # 遍历数据帧的每一行
    for _, row in df.iterrows():
        # 准备当前行的数据：去除无效值（整数0和特定的'DEPENDENCY_PATH'标记）
        cleaned_entries = [(col, str(val) if not isinstance(val, str) else val)
                           for col, val in row.items()
                           if not (isinstance(val, int) and val == 0) and not (col == 'DEPENDENCY_PATH' and val != '[]')
                           ]

        # 按照columns_names的顺序对数据排序
        sorted_entries = sorted(cleaned_entries, key=lambda x: columns_names.index(x[0]))
        for entry in sorted_entries:
            element_counts[frozenset(entry)] = element_counts.get(frozenset(entry), 0) + 1
        processed_data_list.append(sorted_entries)

    # 初始化处理后的数据字典，用于存储每个唯一数据组合的计数
    processed_data_dict = {}

    for rows in processed_data_list:
        temp_list = []
        for row in rows:
            if element_counts[frozenset(row)] >= min_support:
                temp_list.append(row)
        if len(temp_list) == 0:
            continue
        # 使用frozenset确保数据的唯一性和可哈希性，作为字典的键
        frozen_entry_set = frozenset(temp_list)

        # 更新字典计数，为每个唯一的数据组合累加计数
        processed_data_dict[frozen_entry_set] = processed_data_dict.get(frozen_entry_set, 0) + 1

    # 初始化最终存储频繁项集的字典
    element_counts = {}

    # 遍历处理后的数据字典，进一步处理以生成频繁项集（此部分依赖于外部函数`permute_dfs`）
    for itemset, count in processed_data_dict.items():
        # 假设`permute_dfs`函数接受itemset、当前深度、路径、是否是根节点、最终结果字典和当前计数作为参数
        permute_dfs(list(itemset), 0, [], False, element_counts, count)

    # 返回满足最小支持度的频繁项集及其计数
    return element_counts
# file_path = "E:/QuesLink_Explorer/data/sentences_data.csv"
# ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
# processed_data = process_data_to_dict(file_path, ignore_columns)