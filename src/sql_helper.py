import sys
import datetime
import numbers

import simplejson as json
from flask import request

from settings import load_config


def get_dataset(query):
    conn, cur = load_config()
    cur.execute(query)
    dataset = cur.fetchall()

    result = []
    item = {}

    for obj in dataset:
        item = {}
        for i in range(len(obj)):
            if isinstance(obj[i], datetime.date):
                item[cur.description[i][0]] = obj[i].strftime('%d/%m/%Y')
            elif (cur.description[i][0] in ['valor_pago', 'valor_conta']) and (isinstance(obj[i], numbers.Number)):
                print(cur.description[i][0], file=sys.stderr)
                print(type(obj[i]), file=sys.stderr)
                print(obj[i], file=sys.stderr)
                item[cur.description[i][0]] = '%.2f' % obj[i]
            else:
                item[cur.description[i][0]] = obj[i]
        for key, it in item.items():
            if it is None:
                item[key] = ''

        result.append(item)
    print(type(result), file=sys.stderr)
    print(result, file=sys.stderr)
    result_str = json.dumps(result, use_decimal=True).replace("'0'", "'nao'").replace("'1'", "'sim'")
    return result_str


def get_value_from_param(request, param, convert_param=None):
    placeholder = ""
    if convert_param == float:
        placeholder = "'%.2f'"
    else:
        placeholder = "'%s'"

    if convert_param is None:
        return placeholder % request.args.get(param) if request.args.get(param) else 'NULL'
    else:
        return placeholder % convert_param(request.args.get(param)) if request.args.get(param) else 'NULL'


def build_values(form, value, init_symbol, final_symbol):
    if value == '':
        return form + final_symbol

    if form == '':
        form += init_symbol
    else:
        form += ', '

    return form + value


def build_statement(params):
    values = ''
    columns = ''
    for param, convert_param in params.items():
        columns = build_values(columns, param, '', '')

        value = get_value_from_param(request, param, convert_param)
        values = build_values(values, value, '(', ')')

    values = build_values(values, '', '(', ')')
    values = values.replace("'NULL'", 'NULL').replace("'None'", 'NULL')
    return columns, values