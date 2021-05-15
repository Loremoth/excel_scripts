import re

import fitz


def get_order_number_and_date(text_sequence: list):
    relevant_datas = {}

    line_with_order_and_date = text_sequence[text_sequence.index('N. ord. acq./data') + 1]
    relevant_datas["order"], relevant_datas["order date"] = line_with_order_and_date.split(' / ')

    for idx, line in enumerate(text_sequence):
        if 'Data consegna' in line:
            relevant_datas["shipping date"] = re.split('\s+', line)[2]

    return relevant_datas


def filter_important_data(text_sequence):
    berry_idx = [i for i, item in enumerate(text_sequence) if re.search('_+', item)][1]
    perry_idx = [i for i, item in enumerate(text_sequence) if re.search('_+', item)][2]
    return text_sequence[berry_idx + 1:perry_idx]  # removing incipit and final


def concat_lines(text_sequence):
    # attach all numbers at the right data lines

    first_line = None
    new_only_text = []

    for line in text_sequence:
        if (line.upper().isupper() and not line[-1] == 'P' and not 'promo' in line):
            if not first_line:
                first_line = line
            else:
                new_only_text.append(first_line)
                first_line = line
        elif 'promo' in line:
            if first_line:
                new_only_text.append(first_line)
            new_only_text.append(line)
            first_line = None
        else:
            first_line += line

    return new_only_text


def remove_prefix(line):
    # Removes useless prefix on data lines

    new_line = line.copy()
    for word in line:
        if word.isnumeric():
            new_line.remove(word)
        else:
            break
    return new_line


def remove_suffix(line):
    # Removes useless suffixes on data lines

    for idx, word in enumerate(reversed(line)):
        if word.isnumeric() or word == '' or ',' in word or word[-1] == 'P':
            continue
        else:
            return line[:4]


def format_line(line):
    # make line ready to be correctly wrote on excel

    if 'promo' not in line:
        new_word = ''
        line = re.split('\s{2,}', line)
        line = remove_prefix(remove_suffix(line))
        for word in line[:len(line) - 1]:
            new_word += ' ' + word
        return [new_word, line[-1]]
    else:
        return line


def append_promo(text_sequence: list):
    #append promo lines to data lines

    promo_line = None
    new_text_sequence = []

    for line in reversed(text_sequence):
        if 'promo' in line:
            promo_line = line
        else:
            line.append(promo_line)
            new_text_sequence.append(line)

    return [line for line in reversed(new_text_sequence)]


def generate_data(f: str):
    doc = fitz.Document(f)
    text=''
    for page in doc:
        text += page.get_text("text")  # getting pdf in string form

    text_sequence = text.split('\n')  # getting pdf in lis
    relevant_datas = get_order_number_and_date(text_sequence)  # t form
    text_sequence = filter_important_data(text_sequence)  # removes incipit and last part
    text_sequence = concat_lines(text_sequence)  # concat
    text_sequence = [format_line(line) for line in text_sequence]
    text_sequence = append_promo(text_sequence)

    return text_sequence, relevant_datas
