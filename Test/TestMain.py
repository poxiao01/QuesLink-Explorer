import os

from utils.FileProcessor import extract_fields_from_file
from utils.TextAnalysisProcessor import TextAnalysisProcessor


def get_file_paths(__base_directory, __output_directory, __test_number):
    """
    根据提供的目录和测试编号，生成一系列文件的完整路径。

    参数:
        __base_directory (str): 所有输入文件的基本目录路径。
        __output_directory (str): 输出文件的基本目录路径。
        __test_number (str): 当前处理的测试编号，用于文件名的定制。

    返回:
        dict: 包含所有相关文件路径的字典，键为文件类型描述，值为对应的文件路径。
    """

    # 文件名模板，用于后续构建完整的文件路径
    test_data_template = 'test-Test-Set.json'
    training_data_template = 'test-Training-Set.txt'
    sentences_information_template = 'test_sentences_information.txt'
    trained_data_template = 'test_Machine_Trained_Data.txt'
    rules_template = 'test_rules'

    # 通过字符串替换，使用传入的测试编号来构建每个文件的完整路径
    # 注意：这里假设文件名模板中的 "test_" 部分会被替换，以生成特定于测试编号的文件名
    test_data_path = f'{__base_directory}{test_data_template.replace("test", f"{__test_number}")}'
    training_data_path = f'{__base_directory}{training_data_template.replace("test", f"{__test_number}")}'
    sentences_information_path = f'{__output_directory}{sentences_information_template.replace("test", f"{__test_number}")}'
    trained_data_path = f'{__output_directory}{trained_data_template.replace("test", f"{__test_number}")}'
    rules_path = f'{__output_directory}{rules_template.replace("test", f"{__test_number}")}'

    # 将构建好的文件路径组织成字典返回
    return {
        'test_data': test_data_path,
        'training_data': training_data_path,
        'sentences_information': sentences_information_path,
        'trained_data': trained_data_path,
        'rules': rules_path
    }


def get_all():
    root_directory = '../unmodifiable_data/'  # 根目录

    # 使用 os.listdir() 列出根目录下的所有项目
    all_items = os.listdir(root_directory)

    # 过滤出目录
    first_level_dirs = [item for item in all_items if os.path.isdir(os.path.join(root_directory, item)) if
                        'folder' in item]

    for input_dir in first_level_dirs:
        # 使用下划线分割字符串，并取最后一部分作为数字
        numbers = input_dir.split('_')[-1]
        base_directory = f'../unmodifiable_data/{input_dir}/'
        output_directory = f'../unmodifiable_data/{input_dir}/'
        paths = get_file_paths(base_directory, output_directory, numbers)
        sentences_list = []
        question_words_list = []
        with open(paths['training_data'], 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for index, line in enumerate(lines):
            if index % 2 == 0:
                sentences_list.append(line.strip())
            else:
                question_words_list.append(line.strip())

        text_analysis_processor = TextAnalysisProcessor()
        text_analysis_processor.train_model_from_scratch(sentences=sentences_list,
                                                         questions=question_words_list, custom_dir='F:\\')
        # text_analysis_processor.load_pretrained_model("../data/sentences_data.csv", ['ID', 'SENTENCE', 'QUESTION_WORD'])

        # 初始化一个空列表用于存储句子
        sentences_list = extract_fields_from_file(paths['test_data'], ['sentence'])
        text_analysis_processor.model_analyze(sentences_list, 'F:\\')
        text_analysis_processor.find_question_word()
        text_analysis_processor.write_results_to_file(paths['sentences_information'])
        text_analysis_processor.write_simplified_results_to_file(paths['trained_data'])
        text_analysis_processor.write_rules_results_to_file(paths['rules'])


get_all()

# # 数据集编号
# test_number = '001'
#
# # 假设的目录
# base_directory = '../unmodifiable_data/001/'
# output_directory = '../unmodifiable_data/001/'
# # 获取所有文件路径
# paths = get_file_paths(base_directory, output_directory, test_number)
# for key in paths.keys():
#     print(f'{key}: {paths[key]}')
#
# sentences_list = []
# question_words_list = []
# with open(paths['hand_tagged'], 'r', encoding='utf-8') as file:
#     lines = file.readlines()
#
# for index, line in enumerate(lines):
#     if index % 2 == 0:
#         sentences_list.append(line.strip())
#     else:
#         question_words_list.append(line.strip())
#
# text_analysis_processor = TextAnalysisProcessor()
# text_analysis_processor.train_model_from_scratch(sentences=sentences_list,
#                                                  questions=question_words_list, custom_dir='F:\\')
# # text_analysis_processor.load_pretrained_model("../data/sentences_data.csv", ['ID', 'SENTENCE', 'QUESTION_WORD'])
#
# # 初始化一个空列表用于存储句子
# sentences_list = extract_fields_from_file(paths['training_data'], ['sentence'])
# text_analysis_processor.model_analyze(sentences_list, 'F:\\')
# text_analysis_processor.find_question_word()
# text_analysis_processor.write_results_to_file(paths['sentences_information'])
# text_analysis_processor.write_simplified_results_to_file(paths['trained_data'])
# text_analysis_processor.write_rules_results_to_file(paths['rules'])
