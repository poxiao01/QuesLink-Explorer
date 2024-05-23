import json


def save_dict_to_json_sorted_by_value(file_path, dictionary, ensure_ascii=False, indent=4, reverse=False):
    """
    将字典内容按值排序后保存为JSON格式的文件。

    参数:
    - file_path (str): 要保存的文件路径。
    - dictionary (dict): 要保存的字典。
    - ensure_ascii (bool): 如果设为False，则允许输出中文等非ASCII字符。默认为False。
    - indent (int): 缩进空格数，用于美化输出的JSON字符串。默认为4。
    - reverse (bool): 排序方式，默认为不反转(False)，即升序。若设置为True，则为降序。

    返回:
    - None

    异常:
    - IOError: 当文件写入失败时抛出。
    """

    # 先对字典按值进行排序
    sorted_dict = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse))

    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(sorted_dict, json_file, ensure_ascii=ensure_ascii, indent=indent)
        print(f"字典已成功按值排序并保存至: {file_path}")
    except IOError as e:
        print(f"保存文件时发生错误: {e}")
