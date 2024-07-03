import itertools

from utils.AssociationRule import AssociationRule
from utils.ItemHasher import ItemHasher


class TrNode(object):
    def __init__(self, value, count):
        self.value = value
        self.count = count
        self.children = []
        self.useful = True

    def has_child(self, value):
        for node in self.children:
            if node.value == value:
                return True
        return False

    def get_child(self, value):
        for node in self.children:
            if node.value == value:
                return node
        return None

    def add_child(self, value, count=1):
        child = TrNode(value, count)
        self.children.append(child)
        return child


class TrieTree(object):
    def __init__(self, transactions, threshold, root_value='Root', root_count=0):
        """
        transactions: list 数据集
        threshold:  阈值
        frequent:   处理后的数据集(字典形式，存储大于等于阈值的所有单项)
        初始化树。
        """
        self.ItemHasher = ItemHasher()
        self.frequent = self.find_frequent_items(transactions, threshold)
        self.root = self.build_fptree(
            transactions, root_value,
            root_count, self.frequent)

    def find_frequent_items(self, transactions, threshold):
        """
        创建一个项的词典，其出现次数超过阈值。
        """
        items = {}

        for transaction in transactions:
            for item in transaction:
                item = self.ItemHasher.hash(item)
                if item in items:
                    items[item] += 1
                else:
                    items[item] = 1
        for key in list(items.keys()):
            if items[key] < threshold:
                del items[key]
        return items

    @staticmethod
    def generate_subsets(items):
        subsets = []
        for r in range(1, len(items) + 1):
            subsets.extend(itertools.combinations(items, r))
        return subsets

    def build_fptree(self, transactions, root_value, root_count, frequent):
        # transactions 原始数据集
        # frequent hash后的频繁项集

        # 创建根结点   (结点名字，结点次数)
        root = TrNode(root_value, root_count)

        for transaction in transactions:
            # 筛选出 出现次数大于等于 支持度 的项
            sorted_items = []
            for x in transaction:
                # 先哈希再判断是否存在
                x = self.ItemHasher.hash(x)
                if x in frequent:
                    sorted_items.append(x)

            # 排序，使项排成 前半部分全为前件的项  后半部分全为后件的项
            sorted_items.sort(key=lambda temp_x: (
                not self.ItemHasher.get_must_antecedent(temp_x),  # 如果是前件，优先级高
                -frequent[temp_x],  # 频次降序
                temp_x  # 按照项本身排序
            ))

            pre_subsets = []
            suff_subsets = []

            for item in sorted_items:
                if self.ItemHasher.get_must_antecedent(item) is True:  # 如果是前件
                    pre_subsets.append(item)
                else:  # 否则是后件
                    suff_subsets.append(item)

            pre_subsets = self.generate_subsets(pre_subsets)
            suff_subsets = self.generate_subsets(suff_subsets)

            if len(pre_subsets) > 0 and len(suff_subsets) > 0:
                for pre_items in pre_subsets:
                    for suff_items in suff_subsets:
                        self.insert_tree(pre_items + suff_items, root, 1)
            for pre_items in pre_subsets:
                self.insert_tree(pre_items, root, 1)
        return root

    def insert_tree(self, items, node, count):
        if len(items) > 0:
            first = items[0]
            child = node.get_child(first)
            if child is None:
                child = node.add_child(first, 0)
            self.insert_tree(items[1:], child, count)
        else:
            node.count += count

    def do_mine_patterns(self, node, support_threshold, path, result_list):
        result_list.append((path, node.count))
        for child in node.children:
            if child.count >= support_threshold:
                self.do_mine_patterns(child, support_threshold, path + [child.value], result_list)
            else:
                child.useful = False

    def mine_patterns(self, node, support_threshold, result_list):
        for child in node.children:
            if child.count >= support_threshold:
                self.do_mine_patterns(child, support_threshold, [child.value], result_list)
            else:
                child.useful = False

    def do_mine_association_rules(self, node, pre_list, suff_list, confidence_threshold, patterns_dict, rules):
        if not node.useful:
            return

        if len(suff_list) > 0:
            assert len(pre_list) > 0, f'{pre_list} -> {suff_list} 错误！前件项数为0无法推出后件！'

        if len(suff_list) != 0:
            assert tuple(pre_list) in patterns_dict, f'错误！前件不存在！{tuple(pre_list)}'
            confidence = node.count / patterns_dict[tuple(pre_list)]
            if confidence < confidence_threshold:
                return

            #  添加关联规则
            rules.add_rule(tuple(pre_list), tuple(suff_list), confidence)

            for child in node.children:
                suff_list.append(child.value)
                self.do_mine_association_rules(child, pre_list, suff_list, confidence_threshold,
                                               patterns_dict, rules)
                suff_list.pop()
        else:
            for child in node.children:
                # 必须为前件
                if self.ItemHasher.get_must_antecedent(child.value) is True:
                    pre_list.append(child.value)
                    self.do_mine_association_rules(child, pre_list, suff_list, confidence_threshold,
                                                   patterns_dict, rules)
                    pre_list.pop()
                else:
                    suff_list.append(child.value)
                    self.do_mine_association_rules(child, pre_list, suff_list, confidence_threshold,
                                                   patterns_dict, rules)
                    suff_list.pop()


def mining(transactions, support_threshold, confidence_threshold):
    tree = TrieTree(transactions, support_threshold)
    patterns_list = []
    tree.mine_patterns(tree.root, support_threshold, patterns_list)

    patterns_dict = dict()
    for rows in patterns_list:
        row, count = rows
        assert tuple(row) not in patterns_dict, f"错误！频繁项:{row} 出现重复！"
        patterns_dict[tuple(row)] = count

    rules = AssociationRule()
    tree.do_mine_association_rules(tree.root, [], [], confidence_threshold, patterns_dict, rules)

    patterns_list = [(tree.ItemHasher.get_items_list(x[0]), x[1]) for x in patterns_list]
    rules.get_original_data(tree.ItemHasher)

    return patterns_list, rules
