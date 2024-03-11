import argparse
import time

import numpy as np
import os
import re
import pickle
import random

# template_prompt = '''I am trying to describe the prosodic structure of sentences. I now have the following sequence, where each number in the sequence corresponds to a word in the sentence sequentially. The number '0' represents non-prominent, the number '1' represents prominent, and the number '2' represents highly prominent. Please do not describe other sequences or group words. You answer should include the description of each word and the summary of the whole sentence. Here is an example of the sequence '0''2''1'.
# '0': This word is characterized as non-prominent. It likely bears a neutral stress or emphasis and does not contribute significantly to the overall prosodic structure or rhythm of the sentence.
# '2': This word is highly prominent. It typically carries strong stress or emphasis, drawing attention to itself. It stands out in the sentence and is likely crucial for conveying the intended meaning.
# '1': This word is categorized as prominent. It carries moderate stress or emphasis, suggesting a relatively higher level of importance compared to a non-prominent word.
# Summary: The sentence structure may thus exhibit a pattern of building up emphasis from the first non-prominent word to the highly prominent word. This arrangement helps convey the intended meaning and rhythm in the sentence.
# Now I will give you the corresponding markers word by word. Please describe the prosodic structure and characteristics corresponding to each word.
# Please describe the prosodic structure and characteristics of the sentence corresponding to the sequence #. Please explain it number by number and do not forget any number.\n'''
template_prompt = '''I am trying to describe the prosodic structure of sentences. I now have the following sequence, where each number in the sequence corresponds to a word in the sentence sequentially. The number '0' represents non-prominent, the number '1' represents prominent, and the number '2' represents highly prominent. You answer should include the description of each word and the summary of the whole sentence. Here is an example of the sequence '0''2''1''0'.
'0': This word is characterized as non-prominent. It likely bears a neutral stress or emphasis and does not contribute significantly to the overall prosodic structure or rhythm of the sentence.
'2': This word is highly prominent. It typically carries strong stress or emphasis, drawing attention to itself. It stands out in the sentence and is likely crucial for conveying the intended meaning.
'1': This word is categorized as prominent. It carries moderate stress or emphasis, suggesting a relatively higher level of importance compared to a non-prominent word.
'0': Similar to the first word, this word is non-prominent and does not have any distinctive stress or emphasis.
Summary: The sentence likely follows a prosodic pattern with an initial non-prominent word, followed by a highly prominent word, then a prominent word, and finally ending with another non-prominent word. The sentence structure may thus exhibit a pattern of building up emphasis from the first non-prominent word to the highly prominent word, with a subsequent decrease in emphasis towards the end. This arrangement helps convey the intended meaning and rhythm in the sentence.
Please describe the prosodic structure and characteristics of the sentence corresponding to the sequence #. Please explain it number by number and do not forget any number. Your answer should have the same format as the example above.\n'''


def get_sentence_prompt(sentence, prompt):
    seq = ''
    for word in sentence:
        p = word.split('\t')[1]
        if p != 'NA':
            seq += f"'{p}' "
    return prompt.replace('#', seq[:-1])


def get_prompt_txt(path, prompt):
    write_lines = []
    with open(path, 'r') as f:
        lines = f.readlines()
        sentence = []
        for i in range(len(lines)):
            if lines[i][0] == '<':
                write_lines.append(get_sentence_prompt(sentence, prompt))
                write_lines.append(lines[i])
                sentence = []
            else:
                sentence.append(lines[i])
        write_lines.append(get_sentence_prompt(sentence, prompt))
        write_lines = write_lines[1:]
    write_path = path[:-4] + '_prompt.txt'
    with open(write_path, 'w') as f:
        f.writelines(write_lines)


def get_fake_embedding(path, save_path):
    with open(path, 'r') as f:
        lines = f.readlines()
        s_len = 0
        name = ''
        for i in range(len(lines)):
            if lines[i][0] == '<':
                if name != '':
                    nl = np.random.randn(s_len + 1, 784)
                    np.save(os.path.join(save_path, name), nl)
                s_len = 0
                name = lines[i].split('\t')[1][:-5]
            elif len(lines[i]) > 1 and lines[i].split('\t')[1] != 'NA':
                s_len += 1
        nl = np.random.randn(s_len + 1, 784)
        np.save(os.path.join(save_path, name), nl)


def read_prompt(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        prompt_list = []
        prompt = ''
        file = ''
        for line in lines:
            if line[0] == '<':
                file = line.split('\t')[1]
            else:
                prompt += line
                if line[0] == 'P':
                    prosody = list(filter(str.isdigit, line))
                    length = len(prosody)
                    prompt_list.append({'file': file, 'prompt': prompt, 'length': length, 'prosody': prosody})
                    file, prompt = '', ''
        return prompt_list


def get_failed(path):
    prompt_list = read_prompt(path)
    with open('failed.pkl', 'rb') as f:
        fail = pickle.load(f)
    fail_list = []
    for prompt in prompt_list:
        if prompt['file'] in fail:
            fail_list.append(prompt)
    return fail_list


def format_response(response: str):
    lines = response.split('\n')
    length = 0
    formatted = ''
    for i in range(len(lines)):
        if lines[i] == '':
            continue
        elif lines[i][0] == "'" or lines[i][0] == 'S':
            if lines[i][-1] == ':':
                formatted += lines[i] + ' '
                formatted += lines[i + 1] + '\n'
            else:
                formatted += lines[i] + '\n'
            length += 1
        elif lines[i][0] in ['0', '1', '2']:
            formatted += f"'{lines[i][0]}'" + lines[i][1:] + '\n'
            length += 1
        else:
            continue
    return formatted, length


def get_des_list(path):
    des_list = {'0': [], '1': [], '2': []}
    for root, dirs, files in os.walk(path):
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                lines = f.readlines()[:-1]
                for line in lines:
                    c = line[1]
                    try:
                        sentence = line.split(': ')[1]
                    except:
                        print(file)
                        print(line)
                    des_list[c].append(sentence)
    return des_list


def get_nl(prompt, des_list):
    response = ''
    for c in prompt['prosody']:
        response += f"'{c}': {des_list[str(c)][random.randint(0, len(des_list[c]) - 1)]}"
    response += "Summary: NA\n"
    return response


def save_prosody_label(prompts, save_path):
    for prompt in prompts:
        label = prompt['prosody']
        label = [int(a) for a in label]
        label_path = os.path.join(save_path, prompt['file'].split('.')[0])
        np.save(label_path, np.asarray(label))


if __name__ == "__main__":
    pass
