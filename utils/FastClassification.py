import os


class SentenceGrouping:
    def __init__(self, source_file_path, target_directory, group_size=200, sub_group_size=100):
        """
        初始化SentenceGrouping类。

        :param source_file_path: str, 输入文件的路径。
        :param target_directory: str, 输出文件的目标目录。
        :param group_size: int, 主分组的大小，默认为200。
        :param sub_group_size: int, 子分组的大小，默认为100。
        """
        self.source_file_path = source_file_path
        self.target_directory = target_directory
        self.group_size = group_size
        self.sub_group_size = sub_group_size
        self.ensure_directory_exists()

    def ensure_directory_exists(self):
        """
        确保目标目录存在，如果不存在则创建。
        """
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory)

    def read_sentences(self):
        """
        从源文件读取所有句子。

        :return: list, 包含所有句子的列表。
        """
        with open(self.source_file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

    def group_sentences(self, sentences):
        """
        将句子分为主分组，然后进一步分为子分组。

        :param sentences: list, 所有句子的列表。
        :return: list, 包含所有子分组的列表。
        """
        main_groups = [sentences[i:i + self.group_size] for i in range(0, len(sentences), self.group_size)]
        sub_groups = []
        for group in main_groups:
            sub_groups.extend([group[i:i + self.sub_group_size] for i in range(0, len(group), self.sub_group_size)])
        return sub_groups

    def write_sub_groups(self, sub_groups):
        """
        将子分组写入文件。

        :param sub_groups: list, 包含所有子分组的列表。
        """
        for index, (hand_tagged, training_set) in enumerate(zip(sub_groups[::2], sub_groups[1::2]), start=1):
            folder_name = f'folder_{index}'
            folder_path = os.path.join(self.target_directory, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            hand_tagged_file_path = os.path.join(folder_path, f'{index}-Test-Set.txt')
            with open(hand_tagged_file_path, 'w', encoding='utf-8') as file:
                file.writelines(hand_tagged)
            training_set_file_path = os.path.join(folder_path, f'{index}-Training-Set.txt')
            with open(training_set_file_path, 'w', encoding='utf-8') as file:
                file.writelines(training_set)

    def process(self):
        """
        执行整个处理流程，包括读取句子、分组和写入文件。
        """
        sentences = self.read_sentences()
        sub_groups = self.group_sentences(sentences)
        self.write_sub_groups(sub_groups)
        print(f'分组完成！')


# 使用示例
source_file_path = '../unmodifiable_data/all-Hand-Tagged_Data.txt'
target_directory = '../unmodifiable_data/'
processor = SentenceGrouping(source_file_path, target_directory, group_size=400, sub_group_size=200)
processor.process()
