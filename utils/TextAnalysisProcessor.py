import heapq
import json
from typing import List, Tuple, Set, Dict, Optional

from data_processing.data_loader import process_data_to_list
from utils.AssociationRule import AssociationRule
from utils.DependencyAnalyzer import DependencyAnalyzer
from utils.Trie_tree import mining


# 查找疑问词辅助类
class Word:
    def __init__(self, words_pos_list: List[Tuple[str, str, str]],
                 words_dependencies_list: List[Tuple[str, List[Tuple[str, str]]]],
                 structure_word_and_pos_tuple: Tuple[str, str, str]):
        """
        初始化 Word 类，用于处理句子中的单词信息和依赖关系信息。

        :param words_pos_list: 句子中所有单词及其词性的列表
        :param words_dependencies_list: 句子中所有依赖关系的列表
        :param structure_word_and_pos_tuple: 句子的句型词及其词性
        """
        self.words_pos_list = words_pos_list
        self.words_dependencies_list = words_dependencies_list
        self.structure_word_and_pos_tuple = structure_word_and_pos_tuple
        self.information_dict = self._build_information_dict()

    def _build_information_dict(self) -> dict:
        """
        构建单词信息的字典，包括单词的词性和依赖关系信息。

        :return: 包含单词信息的字典
        """
        info_dict = {}

        # 处理单词及其词性信息
        for (_word, pos, _) in self.words_pos_list:
            info_dict[_word] = {('QUESTION_WORD_POS', pos)}

        # 处理依赖关系信息
        for rel, words in self.words_dependencies_list:
            rel = rel.upper().replace(':', '_')
            info_dict[words[0]].add(('QUESTION_' + rel, 1))
            info_dict[words[1]].add(('QUESTION_' + rel, 2))
            # 判断是该词与句型词是否在同一个依赖结构中
            if words[1] == self.structure_word_and_pos_tuple[2]:
                info_dict[words[0]].add(('SAME_DEPENDENCY', rel + '_1'))
            if words[0] == self.structure_word_and_pos_tuple[2]:
                info_dict[words[1]].add(('SAME_DEPENDENCY', rel + '_2'))

            # 判断该词是否与句型词相同
            if words[0] == self.structure_word_and_pos_tuple[2]:
                info_dict[words[0]].add(('SAME_QS_WORD', 'True'))
            if words[1] == self.structure_word_and_pos_tuple[2]:
                info_dict[words[1]].add(('SAME_QS_WORD', 'True'))
        # for (_word, pos, _) in self.words_pos_list:
        #     print(f'信息：{_word} : {info_dict[_word]}')
        return info_dict

    def check_legality(self, input_set: Set[Tuple[str, ...]], confidence: float) -> List[Tuple[str, float]]:
        """
        检查给定集合的合法性。

        :param input_set: 待检查的特征集合
        :param confidence: 置信度
        :return: 符合条件的单词及其置信度列表
        """
        result = []
        for _word in self.information_dict:
            # 若输入集合中的所有特征 在[_word]集合中出现  即满足条件
            if input_set.issubset(self.information_dict[_word]):
                result.append((_word, confidence))
        return result


# 加载训练的模型并处理输入的数据
class TextAnalysisProcessor:
    def __init__(self):
        self.all_inverted_index_list = []  # 合法规则的倒排索引
        self.all_structure_words_information_list = []  # 句型词信息
        self.all_sentence_pattern_list = []  # 句子类型
        self.all_structure_words_in_dependencies_position_list = []  # 句型词在依赖结构中的位置
        self.all_structure_words_and_pos_list = []  # 句型词及其词性
        self.all_words_pos_list = []  # 句子中所有词及其词性
        self.all_words_dependencies_list = []  # 依赖结构
        self.model_rules = AssociationRule()  # 模型类
        self.data_list = []  # 待分析句子的列表
        self.ans = []

    # 加载训练好的模型
    def load_pretrained_model(self,
                              model_csv_file: str,
                              ignore_columns: List[str]) -> None:
        """
        加载训练好的模型数据。

        :param model_csv_file: 模型数据文件路径
        :param ignore_columns: 忽略的列名列表
        """
        processed_data_list = process_data_to_list(model_csv_file, ignore_columns)
        __, self.model_rules = mining(processed_data_list, support_threshold=2, confidence_threshold=0.8)

    # 从头开始训练模型
    def train_model_from_scratch(self,
                                 sentences: List[str],
                                 questions: List[str],
                                 custom_dir: str) -> None:
        """
        从头开始训练模型。

        :param sentences: 句子列表
        :param questions: 问题列表
        :param custom_dir: 自定义目录路径
        """
        dependency_analyzer = DependencyAnalyzer(model_dir=custom_dir,
                                                 _sentences_list=sentences,
                                                 question_word_list=questions)
        processed_data_list = dependency_analyzer.retrieve_all_information()
        __, self.model_rules = mining(processed_data_list, support_threshold=2, confidence_threshold=0.8)

    # 使用模型对当前数据进行处理
    def model_analyze(self, data_list: List[str], custom_dir: str) -> None:
        """
        使用模型对输入数据进行分析。

        :param data_list: 待分析的句子列表
        :param custom_dir: 自定义模型目录
        """

        # 所有句子
        self.data_list = data_list
        # 创建DependencyAnalyzer实例，传入自定义目录、句子列表和空的疑问词列表
        dependency_analyzer = DependencyAnalyzer(model_dir=custom_dir, _sentences_list=data_list, question_word_list=[])

        # 获取所有单词的依赖关系列表
        self.all_words_dependencies_list = dependency_analyzer.get_all_words_dependencies()

        # 获取所有单词的词性标注列表
        self.all_words_pos_list = dependency_analyzer.get_all_words_pos()

        # 获取句型词及其词性的列表
        self.all_structure_words_and_pos_list = dependency_analyzer.get_structure_words_and_pos()

        # 获取句型词在依存关系中的位置列表
        self.all_structure_words_in_dependencies_position_list = (dependency_analyzer.
                                                                  get_structure_words_in_dependencies_position())

        # 判断每个句子的句型（疑问句或陈述句）
        self.all_sentence_pattern_list = ['疑问句' if sentence.strip().endswith('?') else '陈述句' for sentence in
                                          data_list]

        # 遍历每个句子，提取有用信息
        for (index, sentence) in enumerate(data_list):
            # 获取当前句子的结构词和词性
            structure_word_and_pos = self.all_structure_words_and_pos_list[index]

            # 初始化一个元组列表，用于存储有用的句子信息
            useful_information = [
                ('SENTENCE_PATTERN', self.all_sentence_pattern_list[index]),  # 句子的句型
                ('SENTENCE_STRUCTURE_WORD', structure_word_and_pos[0]),  # 句型词
                ('SENTENCE_STRUCTURE_WORD_POS', structure_word_and_pos[1])  # 句型词词性
            ]

            # 遍历句型词在依存关系中的位置，构建 （SENTENCE_依赖结构，对应依赖结构中的位置）
            for structure_words_position in self.all_structure_words_in_dependencies_position_list[index]:
                useful_information.append(('SENTENCE_' + str(structure_words_position[0]), structure_words_position[1]))
            self.all_structure_words_information_list.append(useful_information)

            # 初始化一个临时列表，用于存放规则索引
            temp_list = []
            for info in useful_information:
                if info in self.model_rules.inverted_index_dict:
                    temp_list.append(self.model_rules.inverted_index_dict[info])

            # 如果临时列表非空，使用heapq.merge合并所有规则索引
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

            # 按 置信度 降序排序规则索引列表
            result_index_list.sort(key=lambda _x: -_x[2])
            self.all_inverted_index_list.append(result_index_list)

    # 枚举所有的前件组合
    def _dfs(self, position_index: int, used_value_set: set, data_list: List[set], confidence_list: List[float], word,
             confidence: float, ans: List[Tuple[str, float]]) -> None:
        """
        深度优先搜索，寻找可能的特征集合。

        :param position_index: 当前处理的位置索引
        :param used_value_set: 当前已使用的特征集合
        :param data_list: 待选择的特征集合列表
        :param confidence_list: 对应的置信度列表
        :param word: Word 实例，用于推导疑问词
        :param confidence: 当前的置信度
        :param ans: 存储结果的列表
        """

        # 基本情况：如果已经处理完data_list中的所有元素
        if position_index == len(data_list):
            # 检查当前集合的合法性
            if used_value_set:
                ans.extend(word.check_legality(used_value_set, confidence))
            return

        # 获取当前位置的元素及其对应的置信度
        current_item = data_list[position_index]
        current_confidence = confidence_list[position_index]

        # 检查是否可以从当前位置向used_value_set添加元素
        if not used_value_set.intersection(current_item):
            # 临时扩展used_value_set，加入当前位置的元素
            used_value_set.update(current_item)
            # 递归处理下一个位置
            self._dfs(position_index + 1, used_value_set, data_list, confidence_list, word,
                      confidence * current_confidence, ans)
            # 恢复used_value_set的原始状态
            used_value_set.difference_update(current_item)

        # 递归调用，跳过当前位置的元素（不添加任何新元素）
        self._dfs(position_index + 1, used_value_set, data_list, confidence_list, word, confidence, ans)

    # 查找每个句子的可能疑问词
    def find_question_word(self) -> None:
        """
        查找每个句子的可能疑问词并更新结果列表。
        """
        # 初始化
        self.ans = []
        for index, sentence in enumerate(self.data_list):
            # 获取唯一的倒排索引及其置信度
            unique_inverted_index_consequent_list, unique_inverted_index_confidence_list = (
                self._get_unique_inverted_index(index))
            # print(f'unique_inverted_index_consequent_list: {unique_inverted_index_consequent_list}\n'
            #       f'unique_inverted_index_confidence_list: {unique_inverted_index_confidence_list}\n'
            #       f'words_pos:{self.all_words_pos_list[index]}\n'
            #       f'dependencies: {self.all_words_dependencies_list[index]}\n'
            #       f'structure_words_and_pos:{self.all_structure_words_and_pos_list[index]}\n')

            # 初始化Word实例
            word = Word(self.all_words_pos_list[index], self.all_words_dependencies_list[index],
                        self.all_structure_words_and_pos_list[index])
            temp_ans = []

            # 执行深度优先搜索
            self._dfs(0, set(), unique_inverted_index_consequent_list, unique_inverted_index_confidence_list, word, 1.0,
                      temp_ans)

            # 按置信度递减排序
            temp_ans.sort(key=lambda x: -x[1])

            # 去重的辅助集合
            having_value = set()
            ans = [(item, confidence) for item, confidence in temp_ans if
                   item not in having_value and not having_value.add(item)]
            self.ans.append(ans)

    #  获取唯一的倒排索引及其对应的最大置信度
    def _get_unique_inverted_index(self, index: int) -> Tuple[List[Set[str]], List[float]]:
        """
        获取唯一的倒排索引及其对应的最大置信度。后件以集合形式返回。

        :param index: 句子在列表中的索引
        :return: 两个列表，第一个是包含唯一后件集合的列表，第二个是对应的最大置信度列表
        """
        # 使用字典存储每个唯一后件及其最大置信度
        unique_inverted_index_dict: Dict[frozenset, float] = {}

        # 遍历倒排索引列表，更新字典中的最大置信度
        for inverted_index in self.all_inverted_index_list[index]:
            rule_id = inverted_index[0]
            # 后件转换为集合并使用不可变集合(frozenset)作为字典的键
            consequent = frozenset(self.model_rules.rules_list[rule_id][1])
            confidence = self.model_rules.rules_list[rule_id][2]

            # 更新字典中的最大置信度
            if consequent in unique_inverted_index_dict:
                unique_inverted_index_dict[consequent] = max(unique_inverted_index_dict[consequent], confidence)
            else:
                unique_inverted_index_dict[consequent] = confidence

        # 将字典的键（集合形式的后件）和对应的最大置信度转换为列表
        unique_inverted_index_consequent_list = [set(consequent) for consequent in unique_inverted_index_dict.keys()]
        unique_inverted_index_confidence_list = list(unique_inverted_index_dict.values())

        return unique_inverted_index_consequent_list, unique_inverted_index_confidence_list

    # 将详细结果信息写入文件
    def write_results_to_file(self, output_file: str) -> None:
        """
        将结果写入文件。
        """
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
                file.write(f"可能的疑问词：\n{self.ans[i]}\n")
                file.write("倒排索引的数据(已按规则的置信度排序)：\n")
                file.write(f'{self.all_inverted_index_list[i]}\n')

    # 只写入疑问词等信息
    def write_simplified_results_to_file(self, output_file: str) -> None:
        """
        将结果写入文件。
        """
        results = []
        for i, sentence in enumerate(self.data_list):
            result_entry = {
                "index": i + 1,
                "sentence": sentence,
                "疑问词": self.ans[i]
            }
            results.append(result_entry)

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

    def write_rules_results_to_file(self, output_file: str) -> None:
        """
        将结果写入文件。
        """
        self.model_rules.save_file(output_file)
