import sys
import datetime

from flask import Flask, render_template, request, redirect, url_for
import simplejson as json
from psycopg2.errors import DuplicateTable

from sql_helper import get_dataset, build_statement
from settings import get_configs, load_config
from utils import get_current_month, get_month_str


app = Flask(__name__)


def main(args):
    configs = get_configs()
    app.run(host=configs['host'], port=configs['port'], debug=configs['debug'])


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


## Cadastro de conta
@app.route('/cadastrar-conta')
def cadastrar_conta():
    result_str = get_dataset("SELECT * FROM tb_all_contas")
    print(result_str, file=sys.stderr)
    return render_template('cadastrar_conta.html', contas=result_str)


@app.route("/submeter-conta", methods=['GET'])
def submeter_conta():
    conn, cur = load_config()
    params = {'conta': None, 'dia_vencimento': lambda x: x if len(x) > 1 else "0%s" % x, 'categoria': None,
              'tipo_conta': None, 'qtd_parcelas': None, 'valor_igual': None, 'valor_conta': float}
    columns, values = build_statement(params)
    cur.execute('INSERT INTO %s (%s) values %s' % ('tb_all_contas', columns, values))
    conn.commit()

    return render_template('redirect.html', message="'Conta cadastrada com sucesso'", page="'/cadastrar-conta'")


# contas pendentes
@app.route('/contas-pendentes')
def contas_pendentes():
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    query = ("SELECT conta, dia_vencimento, tipo_conta, qtd_parcelas, valor_igual, valor_conta, categoria, obs, "
             "CONCAT(dia_vencimento, '/', REPEAT('0', 2 - LENGTH(CAST(EXTRACT(MONTH FROM CURRENT_DATE) AS TEXT))), "
             "EXTRACT(MONTH FROM CURRENT_DATE), '/', EXTRACT(YEAR FROM CURRENT_DATE)) as data_vencimento "
             "FROM tb_all_contas "
             "WHERE conta NOT in (SELECT conta FROM tb_gastos WHERE EXTRACT(YEAR FROM data_pagamento) = %s AND "
             "EXTRACT(MONTH FROM data_pagamento) = %s)") % (current_year, current_month)
    result_str = get_dataset(query)
    return render_template('contas-pendentes.html', contas=result_str)


@app.route('/update-conta')
def update_conta():
    conn, cur = load_config()

    params = {'conta': None, 'data_pagamento': None, 'tipo_gasto': None, 'data_vencimento': None, 'pagador': None,
              'valor_pago': float, 'categoria': None, 'obs': None}
    columns, values = build_statement(params)
    cur.execute('INSERT INTO %s (%s) VALUES %s' % ('tb_gastos', columns, values))
    conn.commit()

    return render_template('redirect.html', message="'Conta atualizada com sucesso'", page="'/contas-pendentes'")


@app.route('/gastos')
def gastos():
    result_str = get_dataset('SELECT * FROM tb_gastos')
    return render_template('gastos.html', gastos=result_str)


@app.route('/submeter-gasto', methods=['GET'])
def submeterGasto():
    conn, cur = load_config()

    params = {'conta': None, 'data_pagamento': None, 'tipo_gasto': None, 'data_vencimento': None, 'valor_pago': float,
              'pagador': None, 'categoria': None, 'obs': None}
    columns, values = build_statement(params)
    print(columns, file=sys.stderr)
    print(values, file=sys.stderr)
    cur.execute('INSERT INTO %s (%s) values %s' % ('tb_gastos', columns, values))
    conn.commit()

    return render_template('redirect.html', message="'Gasto cadastrado com sucesso'", page="'/gastos'")


@app.route('/redirect')
def redirect():
    message = request.args.get('message') if request.args.get('message') else ''
    page = request.args.get('page') if request.args.get('page') else ''
    return render_template('redirect.html', message=page, page=page)


@app.route('/relatorios')
def relatorios():
    month_int, month_str = get_current_month(request)
    gastos_no_mes = json.loads(get_dataset((
        'SELECT pagador, SUM(valor_pago) AS total_gasto '
        'FROM tb_gastos '
        'WHERE EXTRACT(MONTH FROM data_pagamento) = %s '
        'GROUP BY pagador' % month_int)))
    gastos_no_mes_data = [['pagador', 'total gasto no mes']]
    for i in gastos_no_mes:
        gastos_no_mes_data.append([i['pagador'], i['total_gasto']])

    gastos_por_mes_dict = {}
    gastos_por_mes = json.loads(get_dataset((
        'SELECT SUM(valor_pago) as total_pago, EXTRACT(MONTH FROM data_pagamento) - 1 as month_int, pagador '
        'FROM tb_gastos '
        'WHERE EXTRACT(YEAR FROM data_pagamento) = EXTRACT(YEAR FROM CURRENT_DATE) '
        'GROUP BY EXTRACT(MONTH FROM data_pagamento), pagador'
    )))
    todos_pagadores = json.loads(get_dataset((
        'SELECT DISTINCT pagador '
        'FROM tb_gastos '
        'WHERE EXTRACT(YEAR FROM data_pagamento) = EXTRACT(YEAR FROM CURRENT_DATE)'
    )))
    for i in gastos_por_mes:
        if (i['month_int']) not in gastos_por_mes_dict.keys():
            gastos_por_mes_dict[i['month_int']] = {}
        gastos_por_mes_dict[i['month_int']][i['pagador']] = i['total_pago']

    # primeiro item
    gastos_por_mes_data = []
    first_item = ['Mes']
    for pagador in todos_pagadores:
        first_item.append(pagador['pagador'])
    gastos_por_mes_data.append(first_item)

    # preenche os outros items
    for k, v in gastos_por_mes_dict.items():
        current_item = [get_month_str(k)]

        for pagador in todos_pagadores:
            if pagador['pagador'] in v.keys():
                current_item.append(v[pagador['pagador']])
            else:
                current_item.append(0)

        gastos_por_mes_data.append(current_item)

    return render_template('relatorios.html', gastos_no_mes=gastos_no_mes_data, gastos_por_mes=gastos_por_mes_data,
                           month_int=month_int, month_str=month_str)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    try:
        conn, cur = load_config()
        cur.execute(open('scripts/create_table_all_contas.sql').read())
        cur.execute(open('scripts/create_table_gastos.sql').read())
        conn.commit()
    except DuplicateTable:
        pass
    main(sys.argv[1:])
