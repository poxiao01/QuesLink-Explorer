from utils.Trie_tree import find_frequent_pattern


def generate_association_rules(patterns_list, confidence_threshold):
    rules = {}
    patterns = dict()
    for rows in patterns_list:
        row, count = rows
        assert tuple(row) not in patterns, f"{row}"
        patterns[tuple(row)] = count

    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        for index in range(1, len(itemset) - 1):
            antecedent = tuple(itemset[:index])
            consequent = tuple(itemset[index:])

            lower_support = patterns[antecedent]
            confidence = float(upper_support) / lower_support

            if confidence >= confidence_threshold:
                rules[antecedent] = (consequent, confidence)
    return rules


if __name__ == '__main__':
    # 设置数据文件的路径以及需要在处理过程中忽略的列名
    simpData = [['苹果', '牛奶', '啤酒', '牛肉', '鱼'],
                ['香蕉', '牛奶', '牛肉', '香肠', '虾'],
                ['牛奶', '牛肉', '香蕉', '虾'],
                ['苹果', '牛奶', '香蕉', '鱼'],
                ['牛奶', '牛肉', '虾'],
                ['牛肉', '鱼', '啤酒']]

    # 基于处理后的数据，寻找出现频率较高的模式（频繁项集），参数2表示支持度阈值
    data_list = find_frequent_pattern(simpData, 2)

    for data in data_list:
        print(data)
    print('\n\n')
    # 根据频繁项集生成关联规则，参数0.8表示最小置信度阈值
    rules_dict = generate_association_rules(data_list, 0)

    for rule, count in rules_dict.items():
        print(rule, count)
