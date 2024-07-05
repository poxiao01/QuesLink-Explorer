class ItemHasher:
    def __init__(self):
        self.hash_list = []  # 存储哈希过的项的列表
        self.must_antecedent = []  # Bool数组 存储该项是否必须作为前项

    def hash(self, item):
        """
        将项哈希成数字，并添加到 hash_list 中，返回其在 hash_list 中的索引。

        Parameters:
        - item: 待哈希的项

        Returns:
        - index: 哈希化后的索引值
        """
        if item not in self.hash_list:
            self.hash_list.append(item)
            # 判断是否必须作为前项，并记录到 must_antecedent
            if (item[0].find('QUESTION') != -1 or item[0] == 'SAME_QS_WORD' or item[0] == 'SAME_DEPENDENCY' or
                    item[0] == 'DEPENDENCY_PATH'):
                self.must_antecedent.append(False)
            else:
                self.must_antecedent.append(True)
            return len(self.hash_list) - 1
        else:
            return self.hash_list.index(item)

    def get_item(self, hash_value):
        """
        根据哈希值获取原始项。

        Parameters:
        - hash_value: 哈希值（整数）

        Returns:
        - item: 原始项（字符串），如果哈希值不存在则返回 None
        """
        try:
            return self.hash_list[hash_value]
        except IndexError:
            return None

    def get_must_antecedent(self, hash_value):
        """
        根据哈希值获取项的 must_antecedent 值。

        Parameters:
        - hash_value: 哈希值（整数）

        Returns:
        - must_antecedent: 项的 must_antecedent 值（布尔值），如果哈希值不存在则返回 None
        """
        try:
            return self.must_antecedent[hash_value]
        except IndexError:
            return None

    def get_items_list(self, hash_value_list):
        """
        根据哈希值列表获取对应的原始项列表。

        Parameters:
        - hash_value_list: 哈希值列表（整数列表）

        Returns:
        - items_list: 原始项列表（字符串元组）
        """
        return tuple(self.hash_list[x] for x in hash_value_list)


if __name__ == "__main__":
    # 示例代码，暂时保留原有测试代码部分
    pass
