import json
import os

from typing import List


def extract_fields_from_file(file_path: str, fields: List[str]) -> List[str]:
    """
    从指定的 JSON 文件中提取给定字段的值。

    参数:
        file_path (str): 包含 JSON 数据的文件路径。
        fields (List[str]): 要提取的字段名称列表。

    返回:
        List[Dict[str, Union[str, None]]]: 提取出的字段值的列表，每个元素是一个字典，包含字段名称及其对应的值。
    """
    # 验证 file_path 是否为字符串
    if not isinstance(file_path, str):
        raise ValueError("文件路径必须是字符串类型。")

    # 验证 fields 是否为字符串类型的列表
    if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
        raise ValueError("字段列表必须是字符串类型的列表。")

    # 尝试打开并读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 '{file_path}' 未找到。")
    except json.JSONDecodeError:
        raise ValueError("文件内容不是有效的 JSON 格式。")

    # 确保数据是一个列表
    if not isinstance(data, list):
        raise ValueError("文件中的数据必须是一个字典列表。")

    extracted_data = []  # 存储提取的数据的列表

    # 遍历列表中的每一个字典项
    for item in data:
        # 确保每个项都是字典类型
        if not isinstance(item, dict):
            raise ValueError("列表中的每一项必须是字典。")

        # 提取字段的值
        for field in fields:
            value = item.get(field)
            # 确保字段值是字符串或 None
            if value is not None and not isinstance(value, str):
                raise ValueError(f"字段 '{field}' 的值必须是字符串或 None。")
            extracted_data.append(value)

    return extracted_data  # 返回提取出的字段值的列表


def extract_corrected_questions_from_file(file_path: str) -> List[str]:
    """
    从指定的 JSON 文件中提取 'corrected_question' 字段的值。

    参数:
        file_path (str): 包含 JSON 数据的文件路径。

    返回:
        List[str]: 提取出的 corrected_question 字段值的列表。
    """
    # 确保文件路径是字符串类型
    if not isinstance(file_path, str):
        raise ValueError("文件路径必须是字符串类型。")

    # 尝试打开并读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 从文件中加载 JSON 数据
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 '{file_path}' 未找到。")
    except json.JSONDecodeError:
        raise ValueError("文件内容不是有效的 JSON 格式。")

    # 确保数据是一个列表
    if not isinstance(data, list):
        raise ValueError("文件中的数据必须是一个字典列表。")

    corrected_questions = []  # 存储提取的 corrected_question 值的列表

    # 遍历列表中的每一个字典项
    for item in data:
        # 确保每个项都是字典类型
        if not isinstance(item, dict):
            raise ValueError("列表中的每一项必须是字典。")

        # 尝试从字典中获取 'corrected_question' 键的值
        corrected_question = item.get('corrected_question')

        # 检查 'corrected_question' 是否存在
        if corrected_question is not None:
            # 确保 'corrected_question' 是字符串类型
            if not isinstance(corrected_question, str):
                raise ValueError("'corrected_question' 的值必须是字符串。")
            corrected_questions.append(corrected_question)  # 将提取的值添加到列表中
        else:
            raise KeyError("字典中缺少 'corrected_question' 键。")

    return corrected_questions  # 返回提取出的 corrected_question 值的列表


def extract_question_strings_from_file(file_path: str, language: str = 'en') -> List[str]:
    """
    从指定的 JSON 文件中提取所有指定语言的 'string' 字段值。

    参数:
        file_path (str): 包含 JSON 数据的文件路径。
        language (str): 需要提取的语言代码，默认为 'en'。

    返回:
        List[str]: 提取的 'string' 字段值的列表。
    """
    # 确保文件路径是字符串类型
    if not isinstance(file_path, str):
        raise ValueError("文件路径必须是字符串类型。")

    # 尝试打开并读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 从文件中加载 JSON 数据
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 '{file_path}' 未找到。")
    except json.JSONDecodeError:
        raise ValueError(f"文件 '{file_path}' 内容不是有效的 JSON 格式。")

    # 确保数据中包含 'questions' 键，并且其值是一个列表
    if 'questions' not in data or not isinstance(data['questions'], list):
        raise ValueError(f"文件 '{file_path}' 中的 'questions' 键必须存在且其值必须是一个列表。")

    question_strings = []  # 存储提取的 'string' 字段值的列表

    # 遍历 'questions' 列表中的每一个问题对象
    for question in data['questions']:
        # 确保每个问题对象是字典类型
        if not isinstance(question, dict):
            raise ValueError(f"文件 '{file_path}' 中的 'questions' 列表中的每一项必须是字典。")

        # 确保 'question' 键存在并且其值是一个列表
        if 'question' not in question or not isinstance(question['question'], list):
            raise ValueError(f"文件 '{file_path}' 中的 'question' 键必须存在且其值必须是一个列表。")

        found = False  # 标志位，表示是否在当前问题对象中找到了满足条件的句子

        # 遍历 'question' 列表中的每一个问题文本对象
        for q_text in question['question']:
            # 确保每个问题文本对象是字典类型
            if not isinstance(q_text, dict):
                raise ValueError(f"文件 '{file_path}' 中的 'question' 列表中的每一项必须是字典。")

            # 只读取指定语言的句子
            if q_text.get('language') == language:
                # 尝试从问题文本对象中获取 'string' 字段的值
                question_string = q_text.get('string')
                # 检查 'string' 是否存在
                if question_string is not None:
                    # 确保 'string' 是字符串类型
                    if not isinstance(question_string, str):
                        raise ValueError(f"文件 '{file_path}' 中的 'string' 的值必须是字符串。")
                    question_strings.append(question_string)  # 将提取的值添加到列表中
                    if found:
                        print(
                            f"警告：文件 '{file_path}'，id:{question.get('id')}，该对象中找到多条语言为 '{language}' 的句子。")
                    found = True
                else:
                    raise KeyError(
                        f"错误：文件 '{file_path}'，id:{question.get('id')}，对象中存在 language:{language} 缺少 'string' 键。")

        if not found:
            print(f"警告：文件 '{file_path}'，id:{question.get('id')}，该对象中没有找到语言为 '{language}' 的句子。")

    return question_strings  # 返回提取出的 'string' 字段值的列表


def process_directory(input_directory: str, output_directory: str, language: str = 'en'):
    """
    处理指定目录中的所有 JSON 和 TXT 文件，并将处理后的文本保存到指定的输出目录中。

    注意:
        若输出目录不存在，默认新建一个目录

    参数:
        input_directory (str): 需要处理的目录路径。
        output_directory (str): 保存处理结果的目录路径。
        language (str): 需要提取的语言代码，默认为 'en'。

    返回:
        None
    """
    # 确保目录路径是字符串类型
    if not isinstance(input_directory, str) or not isinstance(output_directory, str):
        raise ValueError("目录路径必须是字符串类型。")

    # 确保语言是字符串类型
    if not isinstance(language, str):
        raise ValueError("语言代码必须是字符串类型。")

    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_directory):
        file_path = os.path.join(input_directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.json'):
            try:
                # 提取指定语言的 'string' 字段值
                strings = extract_corrected_questions_from_file(file_path)

                # 格式化为 id 和 sentence 字典列表
                formatted_data = [{'id': idx + 1, 'sentence': s} for idx, s in enumerate(strings)]

                # 生成输出文件路径
                output_file_name = f"sentences_{filename}"
                output_file_path = os.path.join(output_directory, output_file_name)

                # 保存提取结果到指定文件
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(formatted_data, f, ensure_ascii=False, indent=4)

                print(f"文件 '{file_path}' 处理完毕，结果已保存到 '{output_file_path}'。")

            except Exception as e:
                print(f"处理文件 '{file_path}' 时发生错误: {e}")

        elif os.path.isfile(file_path) and filename.endswith('.txt'):
            try:
                # 提取指定语言的 'string' 字段值
                strings = extract_question_strings_from_file(file_path, language)

                # 格式化为 id 和 sentence 字典列表
                formatted_data = [{'id': idx + 1, 'sentence': s} for idx, s in enumerate(strings)]

                # 生成输出文件路径
                output_file_name = f"sentences_{filename}"
                output_file_path = os.path.join(output_directory, output_file_name)

                # 保存提取结果到指定文件
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(formatted_data, f, ensure_ascii=False, indent=4)

                print(f"文件 '{file_path}' 处理完毕，结果已保存到 '{output_file_path}'。")

            except Exception as e:
                print(f"处理文件 '{file_path}' 时发生错误: {e}")


if __name__ == '__main__':
    # 处理指定目录中的所有 json 和 txt 文件，并将处理后的文本保存到指定的输出目录中。
    # 注意格式必须与 示例txt、json文件一致

    # 输入目录路径
    _input_directory = '../raw_data'

    # 输出目录路径
    _output_directory = '../processed_data'

    process_directory(_input_directory, _output_directory)
