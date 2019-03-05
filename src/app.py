from flask import Flask, render_template, request, redirect, url_for
import simplejson as json
import sys
import psycopg2
import datetime
import numbers

app = Flask(__name__)

def main(args):
	with open('./config/config.json') as content:
		configs = json.load(content)
	
	app.run(host = configs['host'], port = configs['port'], debug = configs['debug'])

@app.route("/home", methods = ['GET'])
def home():
	return render_template('home.html')

## Cadastro de conta
@app.route("/cadastrar-conta")
def cadastrarConta():
	result_str = getDataset("SELECT * FROM tb_all_contas")
	print(result_str, file=sys.stderr)
	return render_template('cadastrar_conta.html', contas = result_str)

@app.route("/submeter-conta", methods = ['GET'])
def submeterConta():
	conn, cur = load_config()
	params = {'conta': None, 'dia_vencimento': lambda x: x if len(x) > 1 else "0%s" % x, 'categoria': None, 'tipo_conta': None, 'qtd_parcelas': None, 'valor_igual': None, 'valor_conta': float}
	columns, values = build_statement(params)
	cur.execute('INSERT INTO %s (%s) values %s' % ('tb_all_contas', columns, values))
	conn.commit()

	return render_template("redirect.html", message = "'Conta cadastrada com sucesso'", page = "'/cadastrar-conta'")

# contas pendentes
@app.route("/contas-pendentes")
def contas_pendentes():
	current_month = datetime.datetime.now().month
	current_year = datetime.datetime.now().year
	query = "SELECT conta, dia_vencimento, tipo_conta, qtd_parcelas, valor_igual, valor_conta, categoria, obs, CONCAT(dia_vencimento, '/', REPEAT('0', 2 - LENGTH(CAST(EXTRACT(MONTH FROM CURRENT_DATE) AS TEXT))), EXTRACT(MONTH FROM CURRENT_DATE), '/', EXTRACT(YEAR FROM CURRENT_DATE)) as data_vencimento FROM tb_all_contas WHERE conta NOT in (SELECT conta FROM tb_gastos WHERE EXTRACT(YEAR FROM data_pagamento) = %s AND EXTRACT(MONTH FROM data_pagamento) = %s)" % (current_year, current_month)
	result_str = getDataset(query)
	return render_template('contas-pendentes.html', contas = result_str)

@app.route("/update-conta")
def update_conta():
	conn, cur = load_config()

	params = {'conta': None, 'data_pagamento': None, "tipo_gasto": None, "data_vencimento": None, "pagador": None, "valor_pago": float, "categoria": None, "obs": None}
	columns, values = build_statement(params)
	cur.execute('INSERT INTO %s (%s) VALUES %s' % ('tb_gastos', columns, values))
	conn.commit()

	return render_template("redirect.html", message = "'Conta atualizada com sucesso'", page = "'/contas-pendentes'")

@app.route("/gastos")
def gastos():
	result_str = getDataset("SELECT * FROM tb_gastos")
	return render_template("gastos.html", gastos = result_str)

@app.route("/submeter-gasto", methods = ['GET'])
def submeterGasto():
	conn, cur = load_config()
	
	params = {'conta': None, 'data_pagamento': None, 'tipo_gasto': None, 'data_vencimento': None, 'valor_pago': float, 'pagador': None, 'categoria': None, 'obs': None}
	columns, values = build_statement(params)
	print(columns, file=sys.stderr)
	print(values, file=sys.stderr)
	cur.execute('INSERT INTO %s (%s) values %s' % ('tb_gastos', columns, values))
	conn.commit()

	return render_template("redirect.html", message = "'Gasto cadastrado com sucesso'", page = "'/gastos'")	

@app.route("/redirect")
def redirect():
	message = request.args.get("message") if request.args.get("message") else ''
	page = request.args.get("page") if request.args.get("page") else ''
	return render_template('redirect.html', message = page, page = page)

@app.route("/relatorios")
def relatorios():
	month_int, month_str = get_current_month(request)
	gastos_no_mes = json.loads(getDataset("SELECT pagador, SUM(valor_pago) AS total_gasto FROM tb_gastos WHERE EXTRACT(MONTH FROM data_pagamento) = %s GROUP BY pagador" % month_int))
	gastos_no_mes_data = [['pagador', 'total gasto no mes']]
	for i in gastos_no_mes:
		gastos_no_mes_data.append([i['pagador'], i['total_gasto']])

	gastos_por_mes_dict = {}
	gastos_por_mes = json.loads(getDataset("SELECT SUM(valor_pago) as total_pago, EXTRACT(MONTH FROM data_pagamento) - 1 as month_int, pagador FROM tb_gastos WHERE EXTRACT(YEAR FROM data_pagamento) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY EXTRACT(MONTH FROM data_pagamento), pagador"))
	todos_pagadores = json.loads(getDataset("SELECT DISTINCT pagador FROM tb_gastos WHERE EXTRACT(YEAR FROM data_pagamento) = EXTRACT(YEAR FROM CURRENT_DATE)"))
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

	return render_template("relatorios.html", gastos_no_mes = gastos_no_mes_data, gastos_por_mes = gastos_por_mes_data, month_int = month_int, month_str = month_str)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def load_config():
	with open('./config/config.json') as content:
		configs = json.load(content)
	
	conn_string = 'host={} dbname={} user={} password={}'.format(configs['hostdb'], configs['dbname'], configs['user'], configs['password'])
	conn = psycopg2.connect(conn_string)
	cur = conn.cursor()

	return conn, cur

def toBit(x):
	return "'1'" if x == 'true' else "'0'"

def getDataset(query):
	conn, cur = load_config()
	cur.execute(query)
	dataset = cur.fetchall()

	result = []
	item = {}

	for obj in dataset:
		item = {}
		for i in range(len(obj)):
			if isinstance(obj[i], datetime.date):
				item[cur.description[i][0]] = obj[i].strftime("%d/%m/%Y")
			elif (cur.description[i][0] in ["valor_pago", "valor_conta"]) and (isinstance(obj[i], numbers.Number)):
				print(cur.description[i][0], file=sys.stderr)	
				print(type(obj[i]), file=sys.stderr)
				print(obj[i], file=sys.stderr)
				item[cur.description[i][0]] = "%.2f" % obj[i]
			else:
				item[cur.description[i][0]] = obj[i]
		for key, it in item.items():
			if it is None:
				item[key] = ''

		result.append(item)
	print(type(result), file=sys.stderr)
	print(result, file=sys.stderr)
	result_str = json.dumps(result, use_decimal = True).replace("'0'","'nao'").replace("'1'", "'sim'")
	return result_str


def get_value_from_param(request, param, convert_param = None):
	placeholder = ""
	if convert_param == float:
		placeholder = "'%.2f'"
	else:
		placeholder = "'%s'"

	if convert_param == None:
		return placeholder % request.args.get(param) if request.args.get(param) else 'NULL'
	else:
		return placeholder % convert_param(request.args.get(param)) if request.args.get(param) else 'NULL'

def build_values(form, value, init_simbol, final_simbol):
	if value == "":
		return form + final_simbol

	if form == "":
		form += init_simbol
	else:
		form += ", "

	return form + value

def build_statement(params):
	values = ""
	columns = ""
	for param, convert_param in params.items():
		columns = build_values(columns, param, "", "")
		
		value = get_value_from_param(request, param, convert_param)
		values = build_values(values, value, "(", ")")

	values = build_values(values, "", "(", ")")
	values = values.replace("'NULL'", "NULL")
	return columns, values

def get_current_month(request):
	month_int = request.args.get("mes_busca") if request.args.get("mes_busca") else datetime.datetime.now().month
	months = ("''", "'Janeiro'", "'Fevereiro'", "'Março'", "'Abril'", "'Maio'", "'Junho'", "'Agosto'", "'Setembro'", "'Outubro'", "'Novembro'", "'Dezembro'")
	return month_int, months[month_int]

def get_month_str(month_int, start_zero = False):
	months = None
	if start_zero:
		months = ("'Janeiro'", "'Fevereiro'", "'Março'", "'Abril'", "'Maio'", "'Junho'", "'Agosto'", "'Setembro'", "'Outubro'", "'Novembro'", "'Dezembro'")
	else:
		months = ("''", "'Janeiro'", "'Fevereiro'", "'Março'", "'Abril'", "'Maio'", "'Junho'", "'Agosto'", "'Setembro'", "'Outubro'", "'Novembro'", "'Dezembro'")

	return months[int(month_int)]

if __name__ == "__main__":
	main(sys.argv[1:])