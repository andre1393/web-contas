from flask import Flask, render_template, request, redirect, url_for
import simplejson as json
import sys
import psycopg2
import datetime

app = Flask(__name__)

def main(args):
	with open('./config/config.json') as content:
		configs = json.load(content)
	
	app.run(host = configs['host'], port = configs['port'], debug = configs['debug'])

@app.route("/cadastrar-conta")
def cadastrarConta():
	result_str = getDataset("SELECT * FROM tb_all_contas")
	print(result_str, file=sys.stderr)
	return render_template('cadastrar_conta.html', contas = result_str)

@app.route("/submeter-conta", methods = ['GET'])
def submeterConta():
	conn, cur = load_config()
	conta = "'%s'" % request.args.get("conta") if request.args.get("conta") else 'NULL'
	dia_vencimento = "'%s'" % request.args.get("dia_vencimento") if request.args.get("dia_vencimento") else 'NULL'
	categoria = "'%s'" % request.args.get("categoria") if request.args.get("categoria") else 'NULL'
	tipo_conta = "'%s'" % request.args.get("tipo_conta") if request.args.get("tipo_conta") else 'NULL'
	qtd_parcelas = "'%s'" % request.args.get("qtd_parcelas") if request.args.get("qtd_parcelas") else 'NULL'
	valor_igual = "'%s'" % request.args.get("valor_igual") if request.args.get("valor_igual") else 'NULL'
	valor_conta = "'%.2f'" % float(request.args.get("valor_conta")) if request.args.get("valor_conta") else 'NULL'

	form = "(%s, %s, %s, %s, %s, %s, %s)" % (conta, dia_vencimento, categoria, tipo_conta, qtd_parcelas, valor_igual, valor_conta)
	#print(form, file=sys.stderr)
	form = form.replace("'NULL'", "NULL")
	cur.execute('INSERT INTO %s (%s) values %s' % ('tb_all_contas', "conta, dia_vencimento, categoria, tipo_conta, qtd_parcelas, valor_igual, valor_conta", form))
	conn.commit()

	return render_template("redirect.html", message = "'Conta cadastrada com sucesso'", page = "'/home'")

@app.route("/home", methods = ['GET'])
def home():
	return render_template('home.html')	

@app.route("/listar-contas")
def listar_contas():
	current_month = datetime.datetime.now().month
	current_year = datetime.datetime.now().year
	query = "SELECT * FROM tb_all_contas WHERE conta NOT in (SELECT conta FROM tb_contas_pagas WHERE EXTRACT(YEAR FROM data_pagamento) = %s AND EXTRACT(MONTH FROM data_pagamento) = %s)" % (current_year, current_month)
	result_str = getDataset(query)
	return render_template('listar-contas.html', contas = result_str)

@app.route("/update-conta")
def update_conta():
	conn, cur = load_config()
	conta = "'%s'" % request.args.get("conta") if request.args.get("conta") else 'NULL'
	data_pagamento = "'%s'" % request.args.get("data_pagamento") if request.args.get("data_pagamento") else 'NULL'
	data_vencimento = "'%s'" % request.args.get("data_vencimento") if request.args.get("data_vencimento") else 'NULL'
	pagador = "'%s'" % request.args.get("pagador") if request.args.get("pagador") else 'NULL'
	valor_pago = "'%.2f'" % float(request.args.get("valor_pago")) if request.args.get("valor_pago") else 'NULL'
	categoria = "'%s'" % request.args.get("categoria") if request.args.get("categoria") else 'NULL'
	obs = "'%s'" % request.args.get("obs") if request.args.get("obs") else 'NULL'

	form = "(%s, %s, %s, %s, %s, %s, %s)" % (conta, data_pagamento, data_vencimento, pagador, valor_pago, categoria, obs)
	form = form.replace("'NULL'", "NULL")
	cur.execute('INSERT INTO %s (%s) VALUES %s' % ('tb_contas_pagas', "conta, data_pagamento, data_vencimento, pagador, valor_pago, categoria, obs", form))
	conn.commit()

	return render_template("redirect.html", message = "'Conta atualizada com sucesso'", page = "'/listar-contas'")

@app.route("/gastos")
def gastos():
	result_str = getDataset("SELECT * FROM tb_contas_pagas")
	return render_template("gastos.html", gastos = result_str)

@app.route("/submeter-gasto", methods = ['GET'])
def submeterGasto():
	conn, cur = load_config()
	conta = "'%s'" % request.args.get("conta") if request.args.get("conta") else 'NULL'
	data_pagamento = "'%s'" % request.args.get("data_pagamento") if request.args.get("data_pagamento") else 'NULL'
	valor_pago = "'%.2f'" % float(request.args.get("valor_pago")) if request.args.get("valor_pago") else 'NULL'
	pagador = "'%s'" % request.args.get("pagador") if request.args.get("pagador") else 'NULL'
	obs = "'%s'" % request.args.get("obs") if request.args.get("obs") else 'NULL'
	categoria = "'%s'" % request.args.get("categoria") if request.args.get("categoria") else 'NULL'

	form = "(%s, %s, %s, %s, %s, %s)" % (conta, data_pagamento, valor_pago, pagador, categoria, obs)
	print(form, file=sys.stderr)
	form = form.replace("'NULL'", "NULL")
	cur.execute('INSERT INTO %s (%s) values %s' % ('tb_contas_pagas', "conta, data_pagamento, valor_pago, pagador, categoria, obs", form))
	conn.commit()

	return render_template("redirect.html", message = "'Gasto cadastrado com sucesso'", page = "'/gastos'")	

@app.route("/redirect")
def redirect():
	message = request.args.get("message") if request.args.get("message") else ''
	page = request.args.get("page") if request.args.get("page") else ''
	return render_template('redirect.html', message = page, page = page)

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

if __name__ == "__main__":
	main(sys.argv[1:])