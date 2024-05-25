import itertools

T = f"QUESTION_WORD_POS=NN"
Count = 0
class FPNode(object):
    """
    一个FP树中的节点。
    """

    def __init__(self, value, count, parent):
        """
        创建节点。
        """
        self.value = value
        self.count = count
        self.parent = parent
        self.link = None
        self.children = []

    def has_child(self, value):
        """
        检查节点是否有一个特定值的子节点。
        """
        for node in self.children:
            if node.value == value:
                return True

        return False

    def get_child(self, value):
        """
        返回具有特定值的子节点。
        """
        for node in self.children:
            if node.value == value:
                return node

        return None

    def add_child(self, value):
        """
        添加一个子节点。
        """
        child = FPNode(value, 1, self)
        self.children.append(child)
        return child


class FPTree(object):
    """
    一个频繁模式树。
    """

    def __init__(self, transactions, threshold, root_value, root_count):
        """
        transactions: list 数据集
        threshold:  阈值
        frequent:   处理后的数据集(字典形式，存储大于等于阈值的所有单项)
        headers:    表头
        初始化树。
        """
        self.frequent = self.find_frequent_items(transactions, threshold)
        self.headers = self.build_header_table(self.frequent)
        self.root = self.build_fptree(
            transactions, root_value,
            root_count, self.frequent, self.headers)

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
    def build_header_table(frequent):
        """
        构建头表。
        """
        headers = {}
        for key in frequent.keys():
            headers[key] = None

        return headers

    def build_fptree(self, transactions, root_value,
                     root_count, frequent, headers):
        """
        构建FP树并返回根节点。
        """
        root = FPNode(root_value, root_count, None)

        for transaction in transactions:
            sorted_items = [x for x in transaction if x in frequent]
            sorted_items.sort(key=lambda x: frequent[x], reverse=True)
            if len(sorted_items) > 0:
                self.insert_tree(sorted_items, root, headers)

        return root

    def insert_tree(self, items, node, headers):
        """
        递归地增长FP树。
        """
        first = items[0]
        child = node.get_child(first)
        if child is not None:
            child.count += 1
        else:
            # 添加新子节点。
            child = node.add_child(first)

            # 将其链接到头结构。
            if headers[first] is None:
                headers[first] = child
            else:
                current = headers[first]
                while current.link is not None:
                    current = current.link
                current.link = child

        # 递归调用函数。
        remaining_items = items[1:]
        if len(remaining_items) > 0:
            self.insert_tree(remaining_items, child, headers)

    def tree_has_single_path(self, node):
        """
        如果树中有一条单一路径，返回True，否则返回False。
        """
        num_children = len(node.children)
        if num_children > 1:
            return False
        elif num_children == 0:
            return True
        else:
            return True and self.tree_has_single_path(node.children[0])

    def mine_patterns(self, threshold):
        """
        挖掘构造的FP树以获取频繁模式。
        """
        if self.tree_has_single_path(self.root):
            return self.generate_pattern_list()
        else:
            return self.zip_patterns(self.mine_sub_trees(threshold))

    def zip_patterns(self, patterns):
        """
        如果我们在条件FP树中，则在字典中的模式后附加后缀。
        """
        suffix = self.root.value

        if suffix is not None:
            # 我们在条件树中。
            new_patterns = {}
            for key in patterns.keys():
                new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

            return new_patterns

        return patterns

    def generate_pattern_list(self):
        """
        生成具有支持计数的模式列表。
        """
        patterns = {}
        items = self.frequent.keys()

        # 如果不在条件模式基树种
        if self.root.value is None:
            suffix_value = []
        else:
            suffix_value = [self.root.value]
            patterns[tuple(suffix_value)] = self.root.count

        for i in range(1, len(items) + 1):
            for subset in itertools.combinations(items, i):
                pattern = tuple(sorted(list(subset) + suffix_value))
                patterns[pattern] = \
                    min([self.frequent[x] for x in subset])

        if T in patterns:
            print(f'T = {T} = {patterns[tuple(T)]}')

        return patterns

    def mine_sub_trees(self, threshold):
        """
        生成子树并挖掘它们以获取模式。
        """
        patterns = {}
        mining_order = sorted(self.frequent.keys(),
                              key=lambda x: self.frequent[x])

        # 按出现次数的相反顺序获取树中的项。
        for item in mining_order:
            suffixes = []
            conditional_tree_input = []
            node = self.headers[item]

            # 遵循节点链接以获取特定项的所有出现列表。
            while node is not None:
                suffixes.append(node)
                node = node.link

            # 对于项的每次出现，追溯到根节点的路径。
            for suffix in suffixes:
                frequency = suffix.count
                path = []
                parent = suffix.parent

                while parent.parent is not None:
                    path.append(parent.value)
                    parent = parent.parent

                for i in range(frequency):
                    conditional_tree_input.append(path)

            # 现在我们有了子树的输入，构建它并获取模式。
            subtree = FPTree(conditional_tree_input, threshold,
                             item, self.frequent[item])
            subtree_patterns = subtree.mine_patterns(threshold)
            # 将子树模式插入主模式字典。
            for pattern in subtree_patterns.keys():
                if pattern in patterns:
                    patterns[pattern] += subtree_patterns[pattern]
                else:
                    patterns[pattern] = subtree_patterns[pattern]
        return patterns


def find_frequent_patterns(transactions, support_threshold):
    """
    给定一组交易，找到超过指定支持阈值的模式。
    """
    tree = FPTree(transactions, support_threshold, None, None)
    return tree.mine_patterns(support_threshold)


def generate_association_rules(patterns, confidence_threshold):
    """
    给定一组频繁项集，返回一个字典形式的关联规则
    {(左侧): ((右侧), 置信度)}
    """
    rules = {}
    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        for i in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, i):
                antecedent = tuple(sorted(antecedent))
                consequent = tuple(sorted(set(itemset) - set(antecedent)))

                if antecedent in patterns:
                    lower_support = patterns[antecedent]
                    confidence = float(upper_support) / lower_support

                    if confidence >= confidence_threshold:
                        rules[antecedent] = (consequent, confidence)

    return rules
