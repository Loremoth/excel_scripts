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
    perry_idx = [i for i, item in enumerate(text_sequence) if re.search('_+', item)][-2]
    return text_sequence[berry_idx + 1:perry_idx]  # removing incipit and final


def concat_lines(text_sequence):
    # attach all numbers at the right data lines

    first_line = None
    new_only_text = []

    for line in text_sequence:
        for word in line:
            if 'promo' in word:
                if first_line:
                    new_only_text.append(first_line)
                    first_line = None
                new_only_text.append(line)
                break
        else:
            if len(line) >= 3 and line[0].isnumeric() and line[1].isnumeric() and line[2].lower().islower():
                if first_line:
                    new_only_text.append(first_line)
                first_line = line
            elif line and not line[0]:
                for word in line:
                    if word:
                        if not first_line:
                            first_line = []
                        first_line.append(word)

    if first_line:
        new_only_text.append(first_line)

    return new_only_text


def remove_prefix(line):
    # Removes useless prefix on data lines
    if line:
        new_line = line.copy()
        for word in line:
            if word.isnumeric():
                new_line.remove(word)
            else:
                break
        return new_line
    else:
        return None


def remove_suffix(line):
    # Removes useless suffixes on data lines
    new_line = line.copy()

    for idx, word in enumerate(reversed(new_line)):
        if word.isnumeric() or word == '' or ',' in word or word[-1] == 'P':
            continue
        else:
            new_line = new_line[:len(word) - idx]
            return new_line


def concat_promos(text_sequence: list):
    new_text_sequence = []
    skip= False
    for idx, line in enumerate(reversed(text_sequence)):
        if skip:
            skip = False
            continue
        if line[0] == 'ed extra':
            first_percentage = extract_percentage_from_promo_line(line)
            second_percentage = extract_percentage_from_promo_line(text_sequence[len(text_sequence) - 1 - idx - 1])
            final_percentage = first_percentage + second_percentage
            word_split = text_sequence[len(text_sequence) - 1 - idx - 1][0].split(' ')
            word_split[1] = final_percentage
            final_word = ' '.join(str(word) for word in word_split)
            final_line = final_word + text_sequence[len(text_sequence) - 1 - idx - 1][1]
            new_text_sequence.append(final_line)
            skip = True
        elif line[0].isnumeric():
            new_text_sequence.append(line)
        elif line[0].startswith('Extra'):
            new_text_sequence.append(' '.join(word for word in line))
        else:
            continue

    return [line for line in reversed(new_text_sequence)]

def extract_percentage_from_promo_line(line: list):
    for word in line:
        if '%' in word:
            word = re.sub('[A-Za-z]+', '', word)
            word = re.sub(',\d+', '', word).replace(' ', '').replace('%','')
            return int(word)


def useful_content(line):
    if len(line) >= 3 and line[0].isnumeric() and line[1].isnumeric() and line[2].lower().islower():
        return True
    for word in line:
        if not (word == '' or word.isnumeric()):
            break
    else:
        return True
    for word in line:
        if 'promo' in word:
            return True
    return False


def format_line(line):
    # make line ready to be correctly wrote on excel

    if 'promo' in line:
        return line
    else:
        line = remove_blank_elements(line)
        line = concat_alphanum_elements(line)
        return line[2:4]


def remove_blank_elements(line: list):
    new_line = []

    for word in line:
        if word:
            new_line.append(word)

    return new_line


def concat_alphanum_elements(line: list):
    new_line: list = line[:3].copy()

    for word in line[3:]:
        if word.upper().isupper():
            new_line[2] += ' ' + word
        else:
            new_line.append(word)

    return new_line


def append_promo(text_sequence: list):
    # append promo lines to data lines

    promo_line = None
    new_text_sequence = []

    for line in reversed(text_sequence):
        if not line:
            continue
        if 'promo' in line:
            promo_line = line
        else:
            line.append(promo_line)
            new_text_sequence.append(line)

    return [line for line in reversed(new_text_sequence)]


def generate_data(f: str):
    doc = fitz.Document(f)
    text = ''
    for page in doc:
        text += page.get_text("text")  # getting pdf in string form

    text_sequence = text.split('\n')  # getting pdf in lis
    relevant_datas = get_order_number_and_date(text_sequence)  # t form
    # text_sequence = filter_important_data(text_sequence)  # removes incipit and last part
    # text_sequence = concat_lines(text_sequence)  # concat
    text_sequence = [re.split('\s{2,}', line) for line in text_sequence]
    text_sequence = [line for line in text_sequence if useful_content(line)]
    text_sequence = concat_lines(text_sequence)  # concat
    text_sequence = concat_promos(text_sequence)
    text_sequence = [format_line(line) for line in text_sequence if text_sequence]
    text_sequence = append_promo(text_sequence)

    return text_sequence, relevant_datas
