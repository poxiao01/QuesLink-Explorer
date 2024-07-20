import string
from typing import List, Tuple, Dict, Set, Optional
import re
import stanza
from stanza.models.common.doc import Sentence


class ShortestPathFinder:
    """
    该类用于解析句子中的依存关系，寻找从句型词到问题词的最短依赖路径。
    """

    def __init__(self, question_word: str, structure_word: str, dependency_relations: List[Tuple[str, Tuple[str, str]]],
                 _sentence: str):
        """
        初始化依赖关系解析器。

        :param question_word: 问题词
        :param structure_word: 句型词
        :param dependency_relations: 句子的依存关系列表
        :param _sentence: 完整的句子文本
        """
        if structure_word == 'How many':
            structure_word = 'How'
            if structure_word not in _sentence:
                structure_word = 'how'

        self.question_word = question_word  # 疑问词
        self.structure_word = structure_word  # 句型词
        self.dependency_relations = dependency_relations  # 依赖关系
        self.sentence = _sentence  # 句子
        self.edge_dict = self._construct_directed_graph()  # 构建有向图
        self.dependency_paths_list = []  # 存储找到的依赖路径
        self._find_shortest_dependency_paths()  # 查找最短依赖路径

    def _construct_directed_graph(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        根据依存关系构建有向图。

        :return: 有向图字典，键为节点（词语），值为（目标节点，关系，方向）的列表
        """
        edge_dict: Dict[str, List[Tuple[str, str, str]]] = {}
        for relation, (head_word, word) in self.dependency_relations:
            edge_dict.setdefault(head_word, []).append((word, relation, '-->'))
            edge_dict.setdefault(word, []).append((head_word, relation, '<--'))
        return edge_dict

    def _find_shortest_dependency_paths(self) -> None:
        """
        从结构词到问题词查找所有最短的依赖路径。
        """
        visited: Set[str] = set()
        visited.add(self.structure_word)
        self._dfs(self.structure_word, self.question_word, [], visited)
        visited.remove(self.structure_word)

        # 如果有多条最短路径，保留它们；否则，保持当前找到的路径
        if self.dependency_paths_list:
            min_path_length = min(len(path) for path in self.dependency_paths_list)
            self.dependency_paths_list = [path for path in self.dependency_paths_list if len(path) == min_path_length]
            # 转换路径表示形式
            self.dependency_paths_list = [' --> '.join(path) for path in self.dependency_paths_list]
            if len(self.dependency_paths_list) > 1:
                print(f'最短路不唯一！{self.sentence}\n')
                # paths_str = '\n'.join(self.dependency_paths_list)
                # dependency_relations_str = '\n'.join(
                #     [f"{relation}: {head_word} -> {word}" for relation, (head_word, word) in self.dependency_relations])
                #
                # raise Exception(f'最短路径不唯一：{self.sentence}\n'
                #                 f'路径: {paths_str}'
                #                 f'依赖结构：{dependency_relations_str}')

        else:
            raise Exception(f'未找到路径：{self.sentence}\n句型词:{self.structure_word}, 疑问词：{self.question_word}\n'
                            f'结构：{self.dependency_relations}')

    def _dfs(self, current_word: str, target_word: str, current_path: List[str], visited: Set[str]) -> None:
        """
        深度优先搜索查找依赖路径。

        :param current_word: 当前处理的词语
        :param target_word: 目标词语
        :param current_path: 当前路径
        :param visited: 已访问节点集合
        """
        if current_word == target_word:
            self.dependency_paths_list.append(current_path)
            return

        if current_word in self.edge_dict:
            for next_word, relation, direction in self.edge_dict[current_word]:
                if next_word not in visited:
                    visited.add(next_word)
                    self._dfs(next_word, target_word, current_path + [f'[{relation}：{direction}]'], visited)
                    visited.remove(next_word)

    def get_dependency_paths(self) -> Optional[List[str]]:
        """
        获取从结构词到问题词的最短依赖路径。

        :return: 最短依赖路径列表（字符串列表），如果没有路径则返回 None
        """
        if self.question_word == self.structure_word:
            return []

        # 检查是否存在直接关系
        for relation, (head_word, word) in self.dependency_relations:
            if (head_word == self.question_word and word == self.structure_word) or \
                    (head_word == self.structure_word and word == self.question_word):
                return []

        return self.dependency_paths_list if self.dependency_paths_list else None


def find_structure_word(__sentence: Sentence) -> Tuple[str, str]:
    """
    根据给定句子识别句型词及其词性。

    参数:
    - sentence (Sentence): Stanza处理过的句子对象。

    返回:
    Tuple[str, str]: 句型词及其词性。
    """
    # 边界检查：确保句子中有词
    if not __sentence.words:
        return 'null', 'null'

    # 定义辅助词集合
    auxiliary_set = {'who', 'what', 'when', 'which', 'how', 'where', 'whose'}

    # 检查第一个词是否是动词
    first_word = __sentence.words[0]
    if first_word.xpos.startswith('VB'):
        return first_word.text, first_word.xpos

    # 特殊情况 "How many"
    if (len(__sentence.words) >= 2 and __sentence.words[0].text.lower() == 'how'
            and __sentence.words[1].text.lower() == 'many'):
        return 'How many', __sentence.words[0].xpos

    # 查找辅助词
    for word in __sentence.words:
        if word.text.lower() in auxiliary_set:
            return word.text, word.xpos

    # 查找动词
    for word in __sentence.words:
        if word.xpos.startswith('V'):
            return word.text, word.xpos

    # 查找小写词
    for word in __sentence.words:
        if word.text.islower():
            return word.text, word.xpos

    raise f'{__sentence} \nError! 未找到指定的句型词!'


def find_question_word_and_pos(__sentence: Sentence, question_word: str) -> Tuple[str, str]:
    """
        根据给定句子的疑问词识别其词性。

        参数:
        - sentence (Sentence): Stanza处理过的句子对象。

        返回:
        Tuple[str, str]: 疑问词及其词性。
        """
    for word in __sentence.words:
        if word.text == question_word:
            return word.text, word.xpos

    raise f'Error! 未找到疑问词的词性！{__sentence} \n {question_word}'


def map_word_positions_to_relations(word: str, dependency_relations: List[Tuple[str, Tuple[str, str]]],
                                    type_prefix: str) -> List[Tuple[str, int]]:
    """
    映射给定词在各种依存关系中的位置至相应的位置标记列表中。

    参数:
    - word (str): 分析的目标给定词。
    - dependency_relations (List[Tuple[str, Tuple[str, str]]]): 每个元组包含依存关系类型和一个元组(头部词汇, 依存词汇)。

    返回:
    List[Tuple[str, int]]: 给定词在所有可能依存关系类型中的位置标记列表。
    """
    all_relations = {
        'NUMMOD', 'OBL_TMOD', 'ADVCL', 'OBL_AGENT', 'CONJ', 'OBL', 'CC',
        'OBL_NPMOD', 'CC_PRECONJ', 'COP', 'NMOD_POSSESS', 'PUNCT', 'XCOMP',
        'EXPL', 'AUX', 'OBJ', 'ACL', 'CCOMP', 'ACL_RELCL', 'DEP', 'APPOS',
        'NSUBJ_PASS', 'FLAT', 'CASE', 'AMOD', 'ROOT', 'NMOD_NPMOD', 'AUX_PASS',
        'MARK', 'ADVCL_RELCL', 'ADVMOD', 'NMOD', 'IOBJ', 'DET_PREDET', 'FIXED',
        'DET', 'COMPOUND', 'NSUBJ'
    }

    position_markers = []

    for rel, (head, dep) in dependency_relations:
        if word in (head, dep):
            position = 1 if head == word else 2
            position_markers.append((type_prefix + rel.upper().replace(':', '_'), position))

    return position_markers


class DependencyAnalyzer:
    def __init__(self, model_dir: str, _sentences_list: List[str], question_word_list: List[str]):
        """
        初始化 DependencyAnalyzer 类。

        参数:
        - model_dir (str): Stanza NLP 模型的自定义目录位置。
        - sentences_list (List[str]): 句子列表。
        - question_word_list (List[str]): 对应每个句子的疑问词列表。
        """
        self.model_dir = model_dir  # 目录
        self.nlp = None
        self.all_words_dependencies_list = []  # 所有句子的单词的依赖结构
        self.all_words_pos_list = []  # 所有句子的单词及其词性
        self.structure_words_and_pos_list = []  # 所有句子的句型词及其词性
        self.question_words_and_pos_list = []  # 所有句子的疑问词及其词性

        self.sentences_list = _sentences_list  # 数据集，包含全部的句子
        self.question_word_list = question_word_list  # 数据集，一一对应每个句子的疑问词

        self.initialize()  # 初始化操作

    def initialize(self):
        """
        初始化 Stanza 的 NLP Pipeline。

        在使用其他方法之前，必须调用此方法初始化 NLP Pipeline。
        """
        try:
            self.nlp = stanza.Pipeline('en', model_dir=self.model_dir, download_method=None,
                                       processors='tokenize,pos,lemma,depparse', use_gpu=True)
        except Exception as e:
            print(f"初始化 NLP Pipeline 失败: {e}")
            raise

        self._process_sentences()

    def _process_sentences(self):
        """
        处理所有句子，提取依赖关系、词性和句型词。
        """
        if len(self.question_word_list) != 0:
            assert len(self.question_word_list) == len(self.sentences_list), (
                f'错误，提取疑问词相关信息必须保证每个句子都有对应的疑问词！\n'
                f'疑问词列表长度：{len(self.question_word_list)}\n'
                f'句子列表长度：{len(self.sentences_list)}'
            )

            for sentence_, question_word in zip(self.sentences_list, self.question_word_list):
                try:
                    # 使用正则表达式进行部分匹配验证
                    assert re.search(r'\b' + re.escape(question_word) + r'\b', sentence_, re.IGNORECASE), (
                        f'疑问词不合法！\n句子：{sentence_}\n疑问词：{question_word}\n\n'
                    )
                except AssertionError as e:
                    raise ValueError(f'处理句子时出错：\n{str(e)}')

        for index_, sentence_ in enumerate(self.sentences_list):
            # 去除末尾的标点符号（仅在末尾是标点符号时进行去除）
            sentence_ = sentence_.strip()
            if sentence_ and sentence_[-1] in string.punctuation:
                sentence_ = sentence_[:-1]
            doc = self.nlp(sentence_)

            sentence_dependencies = []
            sentence_words_pos = []

            counts_dict = dict()

            for word in doc.sentences[0].words:
                head_word = doc.sentences[0].words[word.head - 1].text if word.head > 0 else word.text
                if word.deprel not in counts_dict:
                    counts_dict[word.deprel] = 0
                else:
                    counts_dict[word.deprel] += 1
                sentence_dependencies.append((f'{word.deprel}_{counts_dict[word.deprel]}', [head_word, word.text]))
                sentence_words_pos.append((word.text, word.xpos, word.upos))

            self.all_words_dependencies_list.append(sentence_dependencies)
            self.all_words_pos_list.append(sentence_words_pos)

            structure_word_and_pos = find_structure_word(doc.sentences[0])
            self.structure_words_and_pos_list.append(structure_word_and_pos)

            if len(self.question_word_list) != 0:
                __question_word_and_pos = find_question_word_and_pos(doc.sentences[0], self.question_word_list[index_])
                self.question_words_and_pos_list.append(__question_word_and_pos)

    def extract_sentences_dependencies_paths(self) -> List[List[str]]:
        """
        计算并收集每个句子的依赖路径列表。

        返回:
        List[List[str]]: 每个句子的依赖路径列表。
        """
        sentences_dependencies_paths = []

        for __sentence, question_word, structure_word_pos, dependencies_relations in zip(
                self.sentences_list,
                self.question_word_list,
                self.structure_words_and_pos_list,
                self.all_words_dependencies_list
        ):
            dependency_resolver = ShortestPathFinder(
                question_word=question_word,
                structure_word=structure_word_pos[0],
                dependency_relations=dependencies_relations,
                _sentence=__sentence
            )

            sentence_dependency_paths = dependency_resolver.get_dependency_paths()
            sentences_dependencies_paths.append(sentence_dependency_paths)

        return sentences_dependencies_paths

    def get_all_words_dependencies(self) -> List[List[Tuple[str, List[str]]]]:
        """
        获取所有句子的单词依赖结构。

        返回:
        List[List[Tuple[str, List[str]]]]: 所有句子的依赖关系列表。
        """
        return self.all_words_dependencies_list

    def get_all_words_pos(self) -> List[List[Tuple[str, str, str]]]:
        """
        获取所有句子的单词及其词性。

        返回:
        List[List[Tuple[str, str, str]]]: 所有单词及其词性信息。
        """
        return self.all_words_pos_list

    def get_structure_words_and_pos(self, by_index: int = None) -> List[Tuple[str, str, str]]:
        """
        获取句型词及其词性。

        Args:
        - by_index (int, optional): 要获取的结构词的索引位置。如果为None，则返回所有句型词及其词性信息。默认为None。

        Returns:
        List[Tuple[str, str, str]]: 句型词及其词性信息。
        """
        structure_words_and_pos_list = []

        if by_index is not None:
            word, pos = self.structure_words_and_pos_list[by_index]
            if pos == 'VB':
                structure_words_and_pos_list.append(('VB', pos, word))  # 替换为 'VB'
            else:
                structure_words_and_pos_list.append((word, pos, word))  # 保留原有词和词性
        else:
            for word, pos in self.structure_words_and_pos_list:
                if pos == 'VB':
                    structure_words_and_pos_list.append(('VB', pos, word))  # 替换为 'VB'
                else:
                    structure_words_and_pos_list.append((word, pos, word))  # 保留原有词和词性

        return structure_words_and_pos_list

    def get_question_words_and_pos(self) -> List[Tuple[str, str]]:
        """
        获取疑问词及其词性信息。

        返回:
        List[Tuple[str, str]]: 包含疑问词及其词性信息的列表。
        """
        return self.question_words_and_pos_list

    def get_sentences_dependencies_paths(self) -> List[List[str]]:
        """
        获取每个句子的依赖路径列表。

        返回:
        List[List[str]]: 每个句子的依赖路径列表。
        """
        return self.extract_sentences_dependencies_paths()

    def find_same_dependency(self, idx):
        """
        查找句型词与问题词之间的直接依存关系。

        Args:
        - idx (int): 要检查的索引位置

        Returns:
        - list of tuples or None: 如果找到依存关系，则返回包含依存关系的元组列表；
          如果未找到任何依存关系，则返回None。
          每个元组的格式为 ('SAME_DEPENDENCY', rel_type)，其中rel_type表示依存关系的类型。
        """
        dependency_list = []
        # 遍历依存关系列表，检查句型词与问题词之间是否存在直接依存关系
        for rel, (head_word, word) in self.all_words_dependencies_list[idx]:
            rel = rel.upper().replace(':', '_')
            # 检查两种情况：问题词是否依赖于句型词，或者句型词是否依赖于问题词
            if self.question_word_list[idx] == head_word and self.structure_words_and_pos_list[idx][0] == word:
                dependency_list.append(('SAME_DEPENDENCY', rel + '_1'))
            if self.question_word_list[idx] == word and self.structure_words_and_pos_list[idx][0] == head_word:
                dependency_list.append(('SAME_DEPENDENCY', rel + '_2'))

        if not dependency_list:
            return None
        return dependency_list

    def get_structure_words_in_dependencies_position(self) -> List[List[Tuple[str, int]]]:
        """
        获取句型词在依赖结构的位置。

        返回:
        List[List[Tuple[str, int]]]: 句型词在依赖树中的位置标记列表。
        """
        structure_words_in_dependencies_position = []
        for __index, dependencies in enumerate(self.all_words_dependencies_list):
            structure_words_in_dependencies_position.append(map_word_positions_to_relations(
                self.structure_words_and_pos_list[__index][0], dependencies, 'SENTENCE_'))
        return structure_words_in_dependencies_position

    def get_question_words_in_dependencies_position(self) -> List[List[Tuple[str, int]]]:
        """
        获取疑问词在依赖结构中的位置。

        返回:
        List[List[Tuple[str, int]]]: 句型词在依赖树中的位置标记列表。
        """
        question_words_in_dependencies_position = []
        for __index, dependencies in enumerate(self.all_words_dependencies_list):
            question_words_in_dependencies_position.append(map_word_positions_to_relations(
                self.question_word_list[__index], dependencies, 'QUESTION_'))
        return question_words_in_dependencies_position

    def retrieve_all_information(self):
        result_list = []
        for __index, question_word in enumerate(self.question_word_list):
            temp_list = []
            # 疑问词与句型词相同
            if question_word == self.structure_words_and_pos_list[__index][0]:
                temp_list.append(('SAME_QS_WORD', 'True'))
            # 是否同依赖
            _ = self.find_same_dependency(__index)
            if _ is not None:
                temp_list.extend(_)

            # 依赖路径
            dependency_resolver = ShortestPathFinder(
                question_word=self.question_word_list[__index],  # 当前句子的问题词
                structure_word=self.structure_words_and_pos_list[__index][0],  # 当前句子的结构词
                dependency_relations=self.all_words_dependencies_list[__index],  # 当前句子的依赖关系列表
                _sentence=self.sentences_list[__index]  # 当前句子文本
            )
            sentence_dependency_paths = dependency_resolver.get_dependency_paths()
            for sentence_dependency_path in sentence_dependency_paths:
                temp_list.append(('DEPENDENCY_PATH', sentence_dependency_path))

            # 句子类型(疑问句 or 陈述句)
            __str = '疑问句' if self.sentences_list[__index][-1] == '?' else '陈述句'
            temp_list.append(('SENTENCE_PATTERN', __str))

            # 句型词
            temp_list.append(('SENTENCE_STRUCTURE_WORD', self.structure_words_and_pos_list[__index][0]))

            # 句型词词性
            temp_list.append(('SENTENCE_STRUCTURE_WORD_POS', self.structure_words_and_pos_list[__index][1]))

            # 疑问词
            temp_list.append(('QUESTION_WORD', self.question_word_list[__index]))

            # 疑问词词性
            temp_list.append(('QUESTION_WORD_POS', self.question_words_and_pos_list[__index][1]))

            # 句型词在依赖关系中的位置
            __structure_word = self.structure_words_and_pos_list[__index][0]
            if __structure_word == 'How many':
                __structure_word = 'How'
            temp_list.extend(map_word_positions_to_relations(__structure_word,
                                                             self.all_words_dependencies_list[__index], 'SENTENCE_'))

            # 疑问词在依赖关系中的位置
            temp_list.extend(map_word_positions_to_relations(self.question_word_list[__index],
                                                             self.all_words_dependencies_list[__index], 'QUESTION_'))

            result_list.append(temp_list)
        return result_list


if __name__ == '__main__':
    sentences_list = []
    question_words_list = []
    file_path = '../unmodifiable_data/test_Hand_Tagged_Data.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for index, line in enumerate(lines):
        if index % 2 == 0:
            sentences_list.append(line.strip())
        else:
            question_words_list.append(line.strip())
    dependency_analyzer = DependencyAnalyzer('F:\\', sentences_list, question_words_list)
    T = dependency_analyzer.retrieve_all_information()


