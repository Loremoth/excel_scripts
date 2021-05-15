import os

from utils.read_pdf import generate_data
from utils.write_excel import generate_excel

global_data_list = []

for f in os.listdir('.'):
    if os.path.isfile(f) and f.endswith('pdf'):
        global_data_list.append(generate_data(f))
directory = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
generate_excel(global_data_list, directory + '.xlsx')
