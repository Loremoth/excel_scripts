import openpyxl


def generate_excel(global_data_list: list, dir_name: str):
    mywb = openpyxl.Workbook()
    mysheet = mywb.get_sheet_by_name('Sheet')

    mysheet['A1'] = 'nr. Ordine'
    mysheet['B1'] = 'data ord.'
    mysheet['C1'] = 'consegna'
    mysheet['D1'] = 'articolo'
    mysheet['E1'] = 'cartoni'
    mysheet['F1'] = 'sell in promo'

    i = 2

    for data in global_data_list:
        order_number = data[1]["order"]
        order_date = data[1]["order date"]
        shipping_date = data[1]["shipping date"]

        for line in data[0]:
            mysheet['A' + str(i)] = str(order_number)
            mysheet['B' + str(i)] = str(order_date)
            mysheet['C' + str(i)] = str(shipping_date)
            mysheet['D' + str(i)] = str(line[0])
            mysheet['E' + str(i)] = str(line[1])
            if line[2]:
                mysheet['F' + str(i)] = str(line[2])
            i += 1

    mywb.save(dir_name)
