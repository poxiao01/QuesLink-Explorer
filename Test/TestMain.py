# # 导入所需的模块和库
# import heapq
# import json
# # from check.check_dfs_counts import check_data_legality, validate_element_counts_list_against_db
# from data_processing.data_loader import process_data_to_list
# from utils.DependencyAnalyzer import DependencyAnalyzer
# from utils.Trie_tree import mining
#
# # 初始化一个空列表用于存储句子
# sentences_list = []
#
# # 定义自定义目录路径
# custom_dir = "F:\\"
#
# # 打开json文件并加载数据
# with open('../data/test-data.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)
#
# # 遍历数据中的每一项条目
# for entry in data:
#     # 提取纠正后的问题
#     corrected_question = entry['corrected_question']
#
#     # 将纠正后的问题添加到句子列表中
#     sentences_list.append(corrected_question)
#
#     # 输出当前句子，以便查看
#     print(sentences_list[-1])
#
# # 创建DependencyAnalyzer实例，传入自定义目录、句子列表和空的疑问词列表
# dependencyAnalyzer = DependencyAnalyzer(model_dir=custom_dir, sentences_list=sentences_list, question_word_list=[])
#
# # 获取所有单词的依存关系列表
# all_words_dependencies_list = dependencyAnalyzer.get_all_words_dependencies()
#
# # 获取所有单词的词性标注列表
# all_words_pos_list = dependencyAnalyzer.get_all_words_pos()
#
# # 获取结构词及其词性的列表
# all_structure_words_and_pos_list = dependencyAnalyzer.get_structure_words_and_pos()
#
# # 获取结构词在依存关系中的位置列表
# all_structure_words_in_dependencies_position_list = dependencyAnalyzer.get_structure_words_in_dependencies_position()
#
# # 判断每个句子的句型（疑问句或陈述句）
# all_sentence_pattern = ['疑问句' if sentence.strip().endswith('?') else '陈述句' for sentence in sentences_list]
#
# # 输出依存关系、词性、结构词及其词性、结构词的位置等信息
# for x in all_words_dependencies_list:
#     print(x)
# print()
# for x in all_words_pos_list:
#     print(x)
# print()
# for x in all_structure_words_and_pos_list:
#     print(x)
# print()
# for x in all_structure_words_in_dependencies_position_list:
#     print(x)
#
# # 处理CSV数据文件，忽略特定列
# file_path = "../data/sentences_data.csv"
# ignore_columns = ['ID', 'SENTENCE', 'QUESTION_WORD']
# processed_data_list = process_data_to_list(file_path, ignore_columns)
#
# # 进行频繁项集挖掘和关联规则挖掘
# data_list, rules = mining(processed_data_list, 2, 0.8)
#
# # 全部句子的 倒排索引数据列表
# all_inverted_index_list = []
#
# # 全部的句子的 句型词相关信息
# all_structure_words_information = []
#
# # 遍历每个句子，提取有用信息
# for (index, sentence) in enumerate(sentences_list):
#     # 获取当前句子的结构词和词性
#     structure_word_and_pos = all_structure_words_and_pos_list[index]
#
#     # 初始化一个元组列表，用于存储有用的句子信息
#     useful_information = [
#         ('SENTENCE_PATTERN', all_sentence_pattern[index]),  # 句子的句型
#         ('SENTENCE_STRUCTURE_WORD', structure_word_and_pos[0]),  # 结构词
#         ('SENTENCE_STRUCTURE_WORD_POS', structure_word_and_pos[1])  # 结构词的词性
#     ]
#
#     # 遍历结构词在依存关系中的位置，构建更多信息元组
#     for structure_words_position in all_structure_words_in_dependencies_position_list[index]:
#         useful_information.append(('SENTENCE_' + str(structure_words_position[0]), structure_words_position[1]))
#
#     all_structure_words_information.append(useful_information)
#
#     # 初始化一个临时列表，用于存放规则索引
#     temp_list = []
#     for info in useful_information:
#         if info in rules.inverted_index_dict:
#             temp_list.append(rules.inverted_index_dict[info])
#
#     # 如果临时列表非空，使用堆排序合并所有规则索引
#     if temp_list:
#         merge_index_list = list(heapq.merge(*temp_list))
#     else:
#         merge_index_list = []
#
#     result_index_list = []
#
#     now_idx = 0
#     while now_idx < len(merge_index_list):
#         value = list(merge_index_list[now_idx])
#         next_idx = now_idx
#         while (next_idx + 1 < len(merge_index_list) and merge_index_list[next_idx + 1][0] ==
#                merge_index_list[next_idx][0]):
#             next_idx += 1
#         value[1] -= next_idx - now_idx + 1
#         if value[1] == 0:
#             result_index_list.append(tuple(value))
#         now_idx = next_idx + 1
#
#     # # 按（第三个元素，第二个元素）降序排序规则索引列表
#     # result_index_list.sort(key=lambda _x: (_x[1], -_x[2]))
#     all_inverted_index_list.append(result_index_list)
#
# # 写入信息至文本文件
# with open('../data/sentences_information.txt', 'w', encoding='utf-8') as file:
#     # 遍历数据，将句子信息和分析结果写入文件
#     for i, sentence in enumerate(data):
#         file.write(f"{i + 1}. {sentences_list[i]}\n")  # 写入句子编号和句子本身
#         file.write(
#             f"句型词：{all_structure_words_and_pos_list[i][0]}, 词性：{all_structure_words_and_pos_list[i][1]}\n")  # 写入句型词和词性
#         file.write("依赖结构：\n")  # 写入依赖结构标题
#         for dep in all_words_dependencies_list[i]:
#             file.write(f"{dep[0]}: [{dep[1][0]}, {dep[1][1]}]\n")  # 写入具体的依存关系细节
#         file.write(f"句型词相关信息：\n{all_structure_words_information[i]}\n")
#         file.write(f"单词及其词性：\n{all_words_pos_list[i]}\n")
#         file.write("倒排索引的数据(已按规则的置信度排序)：\n")
#         file.write(f'{all_inverted_index_list[i]}')
#         file.write("\n")
#
#
# # 怎么确定一个单词是句子中的哪个单词？
# # 单词的词性  单词在依赖结构中的位置  是否同依赖  是否与句型词相同
#
import json

from utils.TextAnalysisProcessor import TextAnalysisProcessor

text_analysis_processor = TextAnalysisProcessor()
text_analysis_processor.load_trained_model("../data/sentences_data.csv", ['ID', 'SENTENCE', 'QUESTION_WORD'])

# 初始化一个空列表用于存储句子
sentences_list = []

# 打开json文件并加载数据
with open('../data/test-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历数据中的每一项条目
for entry in data:
    corrected_question = entry['corrected_question']
    sentences_list.append(corrected_question)

text_analysis_processor.model_analyze(sentences_list, 'F:\\')

text_analysis_processor.write_results_to_file('../data/sentences_information.txt')
