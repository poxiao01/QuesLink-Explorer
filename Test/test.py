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

    def mine_patterns(self, threshold):
        """
        挖掘构造的FP树以获取频繁模式。
        """
        if self.tree_has_single_path(self.root):
            return self.generate_pattern_list()
        else:
            return self.zip_patterns(self.mine_sub_trees(threshold))