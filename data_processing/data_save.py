import json


def save_dict_to_json(dictionary, file_path, ensure_ascii=False, indent=4, reverse=False):
    """
    将字典内容保存为JSON格式的文件。

    参数:
    - file_path (str): 要保存的文件路径。
    - dictionary (dict): 要保存的字典。
    - ensure_ascii (bool): 如果设为False，则允许输出中文等非ASCII字符。默认为False。
    - indent (int): 缩进空格数，用于美化输出的JSON字符串。默认为4。

    返回:
    - None

    异常:
    - IOError: 当文件写入失败时抛出。
    """
    if not reverse:
        # 创建一个新的字典，其中元组键被转换为字符串
        new_dictionary = dict()
        for key, value in dictionary.items():
            new_dictionary[str(key)] = str(value)

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(new_dictionary, json_file, ensure_ascii=ensure_ascii, indent=indent)
            print(f"字典已成功保存至: {file_path}")
        except IOError as e:
            print(f"保存文件时发生错误: {e}")
    else:
        new_list = []
        for key, value in dictionary.items():
            new_list.append(f'{str(value[0])} 置信度：{value[1]} <-- {str(key)}')

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(new_list, json_file, ensure_ascii=ensure_ascii, indent=indent)
            print(f"字典已成功保存至: {file_path}")
        except IOError as e:
            print(f"保存文件时发生错误: {e}")


def save_list_as_whole(data_list, file_path):
    new_dict = dict()
    for data in data_list:
        new_dict[tuple(data[0])] = data[1]
    save_dict_to_json(new_dict, file_path, reverse=False)
