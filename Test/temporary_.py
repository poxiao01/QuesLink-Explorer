import json
import os
import re

def unique_sentence():
    import json
    sentence_set = set()

    with open('../processed_data/sentences_9-train-multilingual.txt', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        sentence = entry['sentence']
        if sentence and sentence[0].isalpha() and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        sentence_set.add(sentence)

    with open('../processed_data/sentences_9-test-multilingual.txt', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        sentence = entry['sentence']
        if sentence and sentence[0].isalpha() and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        sentence_set.add(sentence)

    with open('../processed_data/sentences_LC-QuAD-train-data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        sentence = entry['sentence']
        if sentence and sentence[0].isalpha() and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        sentence_set.add(sentence)

    # 创建一个列表来存储去重后的句子及其ID
    unique_sentences = []
    id_counter = 1  # 初始化ID计数器

    # 遍历sentence_set，为每个句子分配一个ID
    for sentence in sentence_set:
        unique_sentences.append({"id": id_counter, "sentence": sentence})
        id_counter += 1

    # 写入JSON文件
    output_file_path = '../processed_data/unique_sentences.json'
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(unique_sentences, file, ensure_ascii=False, indent=4)

    print(f"已将 {len(unique_sentences)} 个唯一句子写入 {output_file_path}")


root_directory = '../unmodifiable_data/'  # 根目录

# 使用 os.listdir() 列出根目录下的所有项目
all_items = os.listdir(root_directory)

# 过滤出目录
first_level_dirs = [item for item in all_items if os.path.isdir(os.path.join(root_directory, item)) if 'folder' in item]

# 编译正则表达式
entity_pattern = re.compile(r'\b(\S+)\b')

for input_dir in first_level_dirs:
    # 使用下划线分割字符串，并取最后一部分作为数字
    numbers = input_dir.split('_')[-1]
    input_file = '../unmodifiable_data/' + input_dir + f'/{numbers}-Test-Set.txt'
    output_file = '../unmodifiable_data/' + input_dir + f'/{numbers}-Test-Set.json'
    try:
        with open(input_file, 'r', encoding='utf8') as f:
            lines = [line.strip() for line in f.readlines()]

        valid_sentences = []
        unique_dict = {}

        # 验证和收集合法的行
        for index in range(0, len(lines), 2):
            line = lines[index]
            entity_line = lines[index + 1]

            match = entity_pattern.match(entity_line)
            if match:
                entity = match.group(1)
                if re.search(r'\b' + re.escape(entity) + r'\b', line, re.IGNORECASE):
                    if line and line[0].isalpha() and line[0].islower():
                        line = line[0].upper() + line[1:]
                    if line not in unique_dict:
                        unique_dict[line] = True
                        valid_sentences.append({"sentence": line})
                    else:
                        print(f'错误: 第 {int(index / 2 + 1)} 行重复\n'
                              f'sentence: {line}\n')
                        raise ValueError
                else:
                    print(f'错误: 第 {int(index / 2 + 1)} 行验证失败')
                    print(f'{int(index / 2 + 1)}: {line}\n{entity_line}\n\n')
                    raise ValueError

        # 将合法的行写入输出文件
        with open(output_file, 'w', encoding='utf8') as f_out:
            json.dump(valid_sentences, f_out, ensure_ascii=False, indent=4)

        print(f"从 '{input_file}' 处理了 {len(valid_sentences)} 行到 '{output_file}' 文件中。")

    except Exception as e:
        print(f"处理文件 '{input_file}' 时发生错误：{e}")





