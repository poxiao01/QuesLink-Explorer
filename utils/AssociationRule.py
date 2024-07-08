# 关联规则类
from db.DbAccessor import count_rows_by_conditions


class AssociationRule:
    def __init__(self):
        """
        初始化关联规则类，设置规则字典和倒排索引。
        """
        self.rules_dict_hashed = {}  # (哈希后)存储关联规则的字典，键为前件，值为关联规则的列表
        self.inverted_index_dict_hashed = {}  # (哈希后)倒排索引，键为前件中的项，值为包含该项的[(关联规则的ID, 后件项数)]的列表
        self.rules_list_hashed = []  # (哈希后)关联规则列表， 下标为规则的ID，即 rules_list_hashed[i] 存储的第i条规则， 且格式为（前件，后件，置信度）

        self.rules_dict = {}  # 存储关联规则的字典，键为前件，值为关联规则的列表
        self.inverted_index_dict = {}  # 倒排索引，键为前件中的项，值为包含该项的[(关联规则的ID, 后件项数)]的列表
        self.rules_list = []  # 关联规则列表， 下标为规则的ID，即 rules_list[i] 存储的第i条规则， 且格式为（前件，后件，置信度）
        self.rules_id = 0

    # 获取未哈希的全部数据
    # check时必须先调用此函数
    def get_original_data(self, item_hasher):
        for (antecedent_hashed, consequent_list_hashed) in self.rules_dict_hashed.items():
            antecedent = item_hasher.get_items_list(antecedent_hashed)
            consequent_list = []
            for item in consequent_list_hashed:
                consequent_list.append((item_hasher.get_items_list(item[0]), item[1], item[2]))
            self.rules_dict[antecedent] = consequent_list

        # 遍历原始字典的每一对键值对
        for pre_item_hashed, suffix_list in self.inverted_index_dict_hashed.items():
            # 获取原始项 pre_item
            pre_item = item_hasher.get_item(pre_item_hashed)

            # 将原始项 pre_item 作为新字典的键，值保持不变
            self.inverted_index_dict[pre_item] = suffix_list

        #    前件        后件           置信度
        for (antecedent, consequent, confidence) in self.rules_list_hashed:
            self.rules_list.append(
                (item_hasher.get_items_list(antecedent), item_hasher.get_items_list(consequent), confidence))

    def add_rule(self, antecedent, consequent, confidence):
        """
        添加关联规则，并更新规则字典和倒排索引。

        Parameters:
        - antecedent: 前件
        - consequent: 后件
        - confidence: 置信度
        """
        rule_id = self.rules_id  # 生成唯一的规则ID
        self.rules_list_hashed.append((antecedent, consequent, confidence))
        self.rules_id += 1

        # 添加规则到规则字典中
        if antecedent not in self.rules_dict_hashed:
            self.rules_dict_hashed[antecedent] = []

        self.rules_dict_hashed[antecedent].append((consequent, confidence, rule_id))

        # 更新倒排索引
        # 注意：格式为 前件中的项：[(规则ID, 后件项数)...]
        for item in antecedent:
            if item not in self.inverted_index_dict_hashed:
                self.inverted_index_dict_hashed[item] = []
            self.inverted_index_dict_hashed[item].append((rule_id, len(antecedent), confidence))

    def check_rules_against_db(self):
        """
        检查关联规则与数据库中的数据是否匹配，并使用 assert 检查预期条件。
        """
        # 第一轮遍历：检查前件中的项是否符合预期
        for antecedent, rules_list in self.rules_dict.items():
            for item in antecedent:
                # 检查前件项是否符合预期条件
                assert not (item[0].find('QUESTION') != -1 or item[0] == 'SAME_QS_WORD' or item[
                    0] == 'SAME_DEPENDENCY' or item[0] == 'DEPENDENCY_PATH'), f'错误！前件项不符合预期！{antecedent}'

            # 第二轮遍历：逐个检查每条规则的后件是否符合预期
            for consequent, confidence, rule_id in rules_list:
                for item in consequent:
                    # 检查后件项是否符合预期条件
                    assert item[0].find('QUESTION') != -1 or item[0] == 'SAME_QS_WORD' or item[
                        0] == 'SAME_DEPENDENCY' or item[0] == 'DEPENDENCY_PATH', f'错误！后件项不符合预期！{consequent}'

                # 构建前件的 WHERE 子句
                where_conditions_antecedent = [
                    f"{col} = {int(val == 'True')}" if val in ['True', 'False'] else f"{col} = '{val}'"
                    for col, val in antecedent
                ]
                where_clause_antecedent = ' AND '.join(where_conditions_antecedent)

                # 构建后件的 WHERE 子句
                where_conditions_consequent = [
                    f"{col} = {int(val == 'True')}" if val in ['True', 'False'] else f"{col} = '{val}'"
                    for col, val in consequent
                ]
                where_clause_consequent = f"{where_clause_antecedent} AND {' AND '.join(where_conditions_consequent)}"

                # 从数据库中获取满足前件 WHERE 子句的行数
                db_count_antecedent = count_rows_by_conditions(where_clause_antecedent)

                # 从数据库中获取满足前件和后件 WHERE 子句的行数
                db_count_consequent = count_rows_by_conditions(where_clause_consequent)

                # 计算实际的置信度
                actual_confidence = db_count_consequent / db_count_antecedent

                # 检查实际置信度与规则中的置信度是否一致
                assert actual_confidence == confidence, f"""
                    规则键的WHERE子句: {where_clause_antecedent}
                    规则值的WHERE子句: {where_clause_consequent}
                    规则键的数据库计数: {db_count_antecedent}, 规则值的数据库计数: {db_count_consequent}
                    预期置信度: {confidence}
                    实际置信度: {actual_confidence}
                    错误！规则的置信度与数据库中的记录不匹配
                """

        print("所有规则验证完成，没有发现不匹配的规则。")

    def check_inverted_index_consistency(self):
        for pre_item, item_list in self.inverted_index_dict.items():
            for index, count, confidence in item_list:
                assert pre_item in self.rules_list[index][
                    0], f'错误！ 倒排索引数据有误！预项"{pre_item}"不在规则列表的前件中。'
                assert count == len(self.rules_list[index][
                                        0]), f'错误！ 倒排索引数据有误！计数"{count}"与前件元素数量"{len(self.rules_list[index][0])}"不符。'
        print("倒排索引验证完成，没有发现不匹配的数据。")

    def save_file(self, filename):
        """
        将关联规则数据保存到文件中。

        Parameters:
        - filename: 要保存的文件名
        """
        rules_file = filename + '_rules.JSON'
        with open(rules_file, 'w', encoding='utf-8') as file:
            rules_id = 0
            for antecedent, consequent, confidence in self.rules_list:
                file.write(f"{rules_id}：{antecedent} ===> {consequent},{confidence}\n")
                rules_id += 1
        print(f"关联规则数据已保存到文件 {rules_file}.")

        inverted_index_file = filename + '_inverted_index.JSON'
        with open(inverted_index_file, 'w', encoding='utf-8') as file:
            for (pre_item, item_list) in self.inverted_index_dict.items():
                file.write(f"{pre_item}: {item_list} \n")
        print(f"倒排索引数据已保存到文件 {inverted_index_file}.")


class QuestionWordFinder:
    def __init__(self):
        self.sentences_list = []
        self.all_inverted_index_list = []
        self.all_structure_words_information = []
