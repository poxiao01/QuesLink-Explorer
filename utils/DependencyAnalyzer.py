from typing import List

import stanza


class DependencyResolver:
    """
    该类用于解析句子中的依存关系，特别是寻找从结构词到问题词的最短依赖路径。
    """

    def __init__(self, question_word, structure_word, dependency_relations, sentence):
        """
        初始化依赖关系解析器。

        :param question_word: 问题词
        :param structure_word: 结构词
        :param dependency_relations: 句子的依存关系列表
        :param sentence: 完整的句子文本
        """
        self.question_word = question_word
        self.structure_word = structure_word
        self.dependency_relations = dependency_relations
        self.sentence = sentence
        self.edge_dict = self._construct_directed_graph()  # 构建有向图
        self.dependency_paths_list = []  # 存储找到的依赖路径
        self._find_shortest_dependency_paths()  # 查找最短依赖路径

    def _construct_directed_graph(self):
        """
        根据依存关系构建有向图。

        :return: 有向图字典，键为节点（词语），值为（目标节点，关系，方向）的列表
        """
        edge_dict = {}
        for relation, words in self.dependency_relations:
            head_word, word = words
            edge_dict.setdefault(head_word, []).append((word, relation, '-->'))
            edge_dict.setdefault(word, []).append((head_word, relation, '<--'))
        return edge_dict

    def _find_shortest_dependency_paths(self):
        """
        从结构词到问题词查找所有最短的依赖路径。
        """
        visited = set()
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
                print(f'最短路不唯一：{self.sentence}')
        else:
            print(f'未找到路径：{self.sentence}')

    def _dfs(self, current_word, target_word, current_path, visited):
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
            for next_word, relation, _ in self.edge_dict[current_word]:
                if next_word not in visited:
                    visited.add(next_word)
                    self._dfs(next_word, target_word, current_path + [f'[{relation}：{_}]'], visited)
                    visited.remove(next_word)

    def get_dependency_paths(self):
        """
        获取从结构词到问题词的最短依赖路径。

        :return: 最短依赖路径列表
        """
        if self.question_word == self.structure_word:
            return []
        for ration, words in self.dependency_relations:
            if words[0] == self.question_word and words[1] == self.structure_word \
                    or words[0] == self.structure_word and words[1] == self.question_word:
                return []

        return self.dependency_paths_list if self.dependency_paths_list else None


def find_structure_word(sentence):
    """
    根据给定句子识别句型起始词及其词性。

    参数:
    - sentence (stanza.models.common.doc.Sentence): Stanza处理过的句子对象。

    返回:
    tuple: 句型起始词及其词性，或('null', 'null')如果未能识别。
    """
    auxiliary_set = {'who', 'what', 'when', 'which', 'how', 'where', 'whose'}

    if sentence.words[0].xpos == 'VB':
        return sentence.words[0].text, sentence.words[0].xpos

    for word in sentence.words:
        if word.text.lower() in auxiliary_set:
            return word.text, word.xpos

    for word in sentence.words:
        if word.xpos.startswith('V'):
            return word.text, word.xpos

    for word in sentence.words:
        if word.text.islower():
            return word.text, word.xpos

    return 'null', 'null'


def map_word_positions_to_relations(word, dependency_relations):
    """
    映射给定词在各种依存关系中的位置至相应的位置标记列表中。

    参数:
    - word (str): 分析的目标给定词。
    - dependency_relations (list[tuple]): 每个元组包含依存关系类型和一个元组(头部词汇, 依存词汇)。

    返回:
    list: 给定词在所有可能依存关系类型中的位置标记列表。
    """
    all_relations = [
        'NUMMOD', 'OBL_TMOD', 'ADVCL', 'OBL_AGENT', 'CONJ', 'OBL', 'CC',
        'OBL_NPMOD', 'CC_PRECONJ', 'COP', 'NMOD_POSSESS', 'PUNCT', 'XCOMP',
        'EXPL', 'AUX', 'OBJ', 'ACL', 'CCOMP', 'ACL_RELCL', 'DEP', 'APPOS',
        'NSUBJ_PASS', 'FLAT', 'CASE', 'AMOD', 'ROOT', 'NMOD_NPMOD', 'AUX_PASS',
        'MARK', 'ADVCL_RELCL', 'ADVMOD', 'NMOD', 'IOBJ', 'DET_PREDET', 'FIXED',
        'DET', 'COMPOUND', 'NSUBJ'
    ]

    detected_relations = set()

    for rel, (head, dep) in dependency_relations:
        if word in (head, dep):
            position = 1 if head == word else 2
            detected_relations.add((rel.upper().replace(':', '_'), position))

    position_markers = []
    for relation in all_relations:
        if (relation, 1) in detected_relations:
            position_markers.append((relation, 1))
        elif (relation, 2) in detected_relations:
            position_markers.append((relation, 2))
    return position_markers


class DependencyAnalyzer:
    def __init__(self, model_dir: str, sentences_list: List[str], question_word_list: List[str]):
        """
        初始化DependencyAnalyzer类。

        参数:
        - model_dir (str): Stanza NLP模型的自定义目录位置。
        """
        self.model_dir = model_dir  # 目录
        self.nlp = None
        self.all_words_dependencies_list = []  # 所有句子的 单词的依赖结构
        self.all_words_pos_list = []  # 所有句子的 单词及其词性
        self.structure_words_and_pos_list = []  # 所有句子的 句型词及其词性

        self.sentences_list = sentences_list  # 数据集 包含全部的句子
        self.question_word_list = question_word_list  # 数据集 一一对应每个句子的疑问词

        self.initialize()  # 初始化操作

    # 初始化操作
    def initialize(self):
        """
        初始化Stanza的NLP Pipeline。

        在使用其他方法之前，必须调用此方法初始化NLP Pipeline。
        """
        self.nlp = stanza.Pipeline('en', model_dir=self.model_dir, download_method=None,
                                   processors='tokenize,pos,lemma,depparse', use_gpu=True)

        # 提取所有单词的依存关系 和 所有单词的词性  句型词及对应的词性
        all_words_dependencies_list = []
        all_words_pos_list = []
        structure_words_and_pos_list = []

        for sentence in self.sentences_list:
            doc = self.nlp(sentence[:-1])

            sentence_dependencies = []
            sentence_words_pos = []

            for word in doc.sentences[0].words:
                head_word = doc.sentences[0].words[word.head - 1].text if word.head > 0 else word.text
                sentence_dependencies.append((word.deprel, [head_word, word.text]))
                sentence_words_pos.append((word.text, word.xpos, word.upos))

            all_words_dependencies_list.append(sentence_dependencies)
            all_words_pos_list.append(sentence_words_pos)

            structure_word = find_structure_word(doc.sentences[0])
            structure_words_and_pos_list.append(structure_word)

        self.all_words_dependencies_list = all_words_dependencies_list
        self.all_words_pos_list = all_words_pos_list
        self.structure_words_and_pos_list = structure_words_and_pos_list  # 提取句型词及对应的词性

    # 提取疑问词及对应的词性
    def extract_question_words_information(self):
        assert len(self.question_word_list) == len(self.sentences_list), (
            f'错误，提取疑问词相关信息必须保证每个句子都有对应的疑问词！\n'
            f'疑问词列表长度：{len(self.question_word_list)}\n'
            f'句子列表长度：{len(self.sentences_list)}')
        question_words_and_pos = []

        for sentence, question_word in zip(self.sentences_list, self.question_word_list):
            doc = self.nlp(sentence)
            for token in doc:
                if token.text == question_word:
                    question_words_and_pos.append((token.text, token.tag_))
                    break
        return question_words_and_pos

    def get_all_words_dependencies(self):
        return self.all_words_dependencies_list

    def get_all_words_pos(self):
        return self.all_words_pos_list

    def get_structure_words_and_pos(self):
        structure_words_and_pos_list = []
        for word, pos in self.structure_words_and_pos_list:
            if pos == 'VB':
                structure_words_and_pos_list.append(('VB', 'VB'))  # 替换为'VB'
            else:
                structure_words_and_pos_list.append((word, pos))  # 保留原有词和词性
        return structure_words_and_pos_list

    def get_question_words_and_pos(self):
        return self.extract_question_words_information()

    def get_sentences_dependencies_paths(self):
        return self.get_sentences_dependencies_paths()

    def get_structure_words_in_dependencies_position(self):
        structure_words_in_dependencies_position = []
        for (index, dependencies) in enumerate(self.all_words_dependencies_list):
            structure_words_in_dependencies_position.append(map_word_positions_to_relations(
                self.structure_words_and_pos_list[index][0], dependencies))
        return structure_words_in_dependencies_position

    # 提取 句型词->疑问词的路径
    def extract_sentences_dependencies_paths(self):
        """
        计算并收集每个句子的依赖路径列表。

        参数:
        - sentences_list (list[str]): 句子列表。
        - questions_words_list (list[str]): 疑问词列表。
        - structure_words_and_pos_list (list[tuple]): 句型起始词及其词性信息列表。
        - all_words_dependencies_relations (list[list[tuple]]): 所有单词的依赖关系列表。

        返回:
        list: 所有句子的依赖路径列表。
        """
        sentences_dependencies_paths = []

        for sentence, question_word, structure_word_pos, dependencies_relations in zip(self.sentences_list,
                                                                                       self.question_word_list,
                                                                                       self.structure_words_and_pos_list,
                                                                                       self.all_words_dependencies_list):
            dependency_resolver = DependencyResolver(
                question_word=question_word,
                structure_word=structure_word_pos[0],
                dependency_relations=dependencies_relations,
                sentence=sentence
            )

            sentence_dependency_paths = dependency_resolver.get_dependency_paths()
            sentences_dependencies_paths.append(sentence_dependency_paths)

        return sentences_dependencies_paths

    # 提取给定单词在句子中依赖结构中的位置

