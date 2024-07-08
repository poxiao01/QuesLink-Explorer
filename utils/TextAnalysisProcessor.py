# 文本分析处理器
import heapq
import json
from data_processing.data_loader import process_data_to_list
from utils.AssociationRule import AssociationRule
from utils.DependencyAnalyzer import DependencyAnalyzer
from utils.Trie_tree import mining


class TextAnalysisProcessor:
    def __init__(self):
        self.all_inverted_index_list = []
        self.all_structure_words_information_list = []
        self.all_sentence_pattern_list = []
        self.all_structure_words_in_dependencies_position_list = []
        self.all_structure_words_and_pos_list = []
        self.all_words_pos_list = []
        self.all_words_dependencies_list = []
        self.model_rules = AssociationRule()
        self.data_list = []

    # 加载训练好的模型
    def load_trained_model(self, model_csv_file, ignore_columns):
        processed_data_list = process_data_to_list(model_csv_file, ignore_columns)
        # 进行频繁项集挖掘和关联规则挖掘
        temp_data_list, self.model_rules = mining(processed_data_list, 2, 0.8)

    # 使用模型对当前数据进行处理
    def model_analyze(self, data_list, custom_dir):
        # data_list： 句子列表
        # custom_dir:   stanford模型目录

        # 所有句子
        self.data_list = data_list

        # 创建DependencyAnalyzer实例，传入自定义目录、句子列表和空的疑问词列表
        dependency_analyzer = DependencyAnalyzer(model_dir=custom_dir, sentences_list=data_list, question_word_list=[])

        # 获取所有单词的依存关系列表
        self.all_words_dependencies_list = dependency_analyzer.get_all_words_dependencies()

        # 获取所有单词的词性标注列表
        self.all_words_pos_list = dependency_analyzer.get_all_words_pos()

        # 获取结构词及其词性的列表
        self.all_structure_words_and_pos_list = dependency_analyzer.get_structure_words_and_pos()

        # 获取结构词在依存关系中的位置列表
        self.all_structure_words_in_dependencies_position_list = (dependency_analyzer.
                                                                  get_structure_words_in_dependencies_position())

        # 判断每个句子的句型（疑问句或陈述句）
        self.all_sentence_pattern_list = ['疑问句' if sentence.strip().endswith('?') else '陈述句' for sentence in data_list]

        # 遍历每个句子，提取有用信息
        for (index, sentence) in enumerate(data_list):
            # 获取当前句子的结构词和词性
            structure_word_and_pos = self.all_structure_words_and_pos_list[index]

            # 初始化一个元组列表，用于存储有用的句子信息
            useful_information = [
                ('SENTENCE_PATTERN', self.all_sentence_pattern_list[index]),  # 句子的句型
                ('SENTENCE_STRUCTURE_WORD', structure_word_and_pos[0]),  # 结构词
                ('SENTENCE_STRUCTURE_WORD_POS', structure_word_and_pos[1])  # 结构词的词性
            ]

            # 遍历结构词在依存关系中的位置，构建更多信息元组
            for structure_words_position in self.all_structure_words_in_dependencies_position_list[index]:
                useful_information.append(('SENTENCE_' + str(structure_words_position[0]), structure_words_position[1]))

            self.all_structure_words_information_list.append(useful_information)

            # 初始化一个临时列表，用于存放规则索引
            temp_list = []
            for info in useful_information:
                if info in self.model_rules.inverted_index_dict:
                    temp_list.append(self.model_rules.inverted_index_dict[info])

            # 如果临时列表非空，使用堆排序合并所有规则索引
            if temp_list:
                merge_index_list = list(heapq.merge(*temp_list))
            else:
                merge_index_list = []

            result_index_list = []

            now_idx = 0
            while now_idx < len(merge_index_list):
                value = list(merge_index_list[now_idx])
                next_idx = now_idx
                while (next_idx + 1 < len(merge_index_list) and merge_index_list[next_idx + 1][0] ==
                       merge_index_list[next_idx][0]):
                    next_idx += 1
                value[1] -= next_idx - now_idx + 1
                if value[1] == 0:
                    result_index_list.append(tuple(value))
                now_idx = next_idx + 1

            # # 按（第三个元素，第二个元素）降序排序规则索引列表
            # result_index_list.sort(key=lambda _x: (_x[1], -_x[2]))
            self.all_inverted_index_list.append(result_index_list)



    # 存储数据
    def write_results_to_file(self, output_file):
        """将结果写入文件"""
        with open(output_file, 'w', encoding='utf-8') as file:
            for i, sentence in enumerate(self.data_list):
                file.write(f"{i + 1}. {sentence}\n")
                file.write(
                    f"句型词：{self.all_structure_words_and_pos_list[i][0]}, "
                    f"词性：{self.all_structure_words_and_pos_list[i][1]}\n")
                file.write("依赖结构：\n")
                for dep in self.all_words_dependencies_list[i]:
                    file.write(f"{dep[0]}: [{dep[1][0]}, {dep[1][1]}]\n")
                file.write(f"句型词相关信息：\n{self.all_structure_words_information_list[i]}\n")
                file.write(f"单词及其词性：\n{self.all_words_pos_list[i]}\n")
                file.write("倒排索引的数据(已按规则的置信度排序)：\n")
                file.write(f'{self.all_inverted_index_list[i]}\n')
