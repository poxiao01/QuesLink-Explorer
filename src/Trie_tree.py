import itertools


class TrNode(object):
    def __init__(self, value, count):
        self.value = value
        self.count = count
        self.children = []

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
        self.frequent = self.find_frequent_items(transactions, threshold)
        self.root = self.build_fptree(
            transactions, root_value,
            root_count, self.frequent)

    @staticmethod
    def find_frequent_items(transactions, threshold):
        """
        创建一个项的词典，其出现次数超过阈值。
        """
        items = {}

        for transaction in transactions:
            for item in transaction:
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
        root = TrNode(root_value, root_count)

        for transaction in transactions:
            sorted_items = [x for x in transaction if x in frequent]
            sorted_items.sort(
                key=lambda x: (x[0].find('QUESTION') == -1, -frequent[x]) if x[0].find('QUESTION') == -1 else (
                    -1, -frequent[x]), reverse=True)

            pre_data_list = [item for item in sorted_items if item[0].find('QUESTION') == -1]
            suff_data_list = [item for item in sorted_items if item[0].find('QUESTION') != -1]

            pre_subsets = self.generate_subsets(pre_data_list)
            suff_subsets = self.generate_subsets(suff_data_list)

            for pre_row in pre_subsets:
                for suff_row in suff_subsets:
                    combined_row = pre_row + suff_row
                    self.insert_tree(combined_row, root, 1)
            for pre_row in pre_subsets:
                self.insert_tree(pre_row, root, 1)
            for suff_row in suff_subsets:
                self.insert_tree(suff_row, root, 1)

        return root

    def insert_tree(self, items, node, count):
        if len(items) > 0:
            first = items[0]
            child = node.get_child(first)
            if child is None:
                child = node.add_child(first, 0)
            self.insert_tree(items[1:], child, count)
        else:
            node.count += 1

    def do_mine_patterns(self, node, support_threshold, path, result_list):
        result_list.append((path, node.count))
        for child in node.children:
            if child.count >= support_threshold:
                self.do_mine_patterns(child, support_threshold, path + [child.value], result_list)

    def mine_patterns(self, node, support_threshold, result_list):
        for child in node.children:
            if child.count >= support_threshold:
                self.do_mine_patterns(child, support_threshold, [child.value], result_list)


def find_frequent_pattern(transactions, support_threshold):
    tree = TrieTree(transactions, support_threshold)

    patterns = []
    tree.mine_patterns(tree.root, support_threshold, patterns)

    return patterns


def generate_association_rules(patterns_list, confidence_threshold):
    rules = {}
    patterns = dict()
    for rows in patterns_list:
        row, count = rows
        assert tuple(row) not in patterns, f"{row}"
        patterns[tuple(row)] = count

    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        antecedent = []
        consequent = []
        for rows in itemset:
            if rows[0].find('QUESTION') == -1:
                assert len(consequent) == 0, f'{itemset}'
                antecedent.append(rows)
            else:
                consequent.append(rows)
        if len(antecedent) == 0 or len(consequent) == 0:
            continue
        antecedent = tuple(antecedent)
        consequent = tuple(consequent)

        assert antecedent in patterns

        lower_support = patterns[antecedent]
        confidence = float(upper_support) / lower_support

        if confidence >= confidence_threshold:
            rules[antecedent] = (consequent, confidence)

    return rules
