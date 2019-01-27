from flask import Flask, render_template, request, redirect, url_for
import simplejson as json
from Contas import Contas
import sys
import psycopg2
import datetime
import time 
app = Flask(__name__)

def main(args):
	with open('./config/config.json') as content:
		configs = json.load(content)
	
	app.run(host = configs['host'], port = configs['port'], debug = configs['debug'])

@app.route("/cadastrar-conta")
def cadastrarConta():
	return render_template('conta_cadastrada.html')

@app.route("/submeter-conta", methods = ['GET'])
def submeterConta():
	conn, cur = load_config()
	conta = "'%s'" % request.args.get("conta") if request.args.get("conta") else 'NULL'
	data_vencimento = "'%s'" % request.args.get("data_vencimento") if request.args.get("data_vencimento") else 'NULL'
	data_pagamento = "'%s'" % request.args.get("data_pagamento") if request.args.get("data_pagamento") else 'NULL'
	valor_conta = "'%.2f'" % float(request.args.get("valor_conta")) if request.args.get("valor_conta") else 'NULL'
	valor_pago = "'%.2f'" % float(request.args.get("valor_pago")) if request.args.get("valor_pago") else 'NULL'
	pago = "'%s'" % request.args.get("pago") if request.args.get("pago") else 'NULL'
	pagador = "'%s'" % request.args.get("pagador") if request.args.get("pagador") else 'NULL'
	recorrente = "'%s'" % request.args.get("recorrente") if request.args.get("recorrente") else 'NULL'
	valor_igual = "'%s'" % request.args.get("valor_igual") if request.args.get("valor_igual") else 'NULL'
	parcelado = "'%s'" % request.args.get("parcelado") if request.args.get("parcelado") else 'NULL'
	qtd_parcelas = "'%s'" % request.args.get("qtd_parcelas") if request.args.get("qtd_parcelas") else 'NULL'

	form = "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (conta, data_vencimento, data_pagamento, valor_conta, valor_pago, pago, pagador, recorrente, valor_igual, parcelado, qtd_parcelas)
	print(form, file=sys.stderr)
	form = form.replace("'NULL'", "NULL")
	cur.execute('INSERT INTO %s (%s) values %s' % ('tb_all_contas', "conta, data_vencimento, data_pagamento, valor_conta, valor_pago, pago, pagador, recorrente, valor_igual, parcelado, qtd_parcelas", form))
	conn.commit()

	return render_template("redirect.html", message = "'Conta cadastrada com sucesso'", page = "'/home'")

@app.route("/home", methods = ['GET'])
def home():
	return render_template('home.html')	

@app.route("/listar-contas")
def listar_contas():
	conn, cur = load_config()
	cur.execute("SELECT * FROM tb_all_contas where pago = 'nao'")
	contas = cur.fetchall()
	result = []
	item = {}
	for conta in contas:
		item = {}
		for i in range(len(conta)):
			if isinstance(conta[i], datetime.date):
				item[cur.description[i][0]] = conta[i].strftime("%d/%m/%Y")
			else:
				item[cur.description[i][0]] = conta[i]
		for key, it in item.items():
			if it is None:
				item[key] = ''

		result.append(item)

	result_str = json.dumps(result).replace("'0'","'nao'").replace("'1'", "'sim'")
	return render_template('listar-contas.html', contas = result_str)	

@app.route("/update-conta")
def update_conta():
	conn, cur = load_config()
	conta = "'%s'" % request.args.get("conta") if request.args.get("conta") else 'NULL'
	data_vencimento = "'%s'" % request.args.get("data_vencimento") if request.args.get("data_vencimento") else 'NULL'
	data_pagamento = "'%s'" % request.args.get("data_pagamento") if request.args.get("data_pagamento") else 'NULL'
	pagador = "'%s'" % request.args.get("pagador") if request.args.get("pagador") else 'NULL'
	valor_pago = "'%.2f'" % float(request.args.get("valor_pago")) if request.args.get("valor_pago") else 'NULL'

	set_str = "%s = %s, %s = %s, %s = %s, %s = '%s'" % ('data_pagamento', data_pagamento, 'pagador', pagador, 'valor_pago', valor_pago, 'pago', 'sim')
	where_str = "%s = %s AND %s = %s" % ('conta', conta, 'data_vencimento', data_vencimento)
	print(set_str, file=sys.stderr)
	set_str = set_str.replace("'NULL'", "NULL")
	cur.execute('UPDATE %s SET %s WHERE %s' % ('tb_all_contas', set_str, where_str))
	conn.commit()

	return render_template("redirect.html", message = "'Conta atualizada com sucesso'", page = "'/listar-contas'")

@app.route("/redirect")
def redirect():
	message = request.args.get("message") if request.args.get("message") else ''
	page = request.args.get("page") if request.args.get("page") else ''
	return render_template('redirect.html', message = page, page = page)

def load_config():
	with open('./config/config.json') as content:
		configs = json.load(content)
	
	conn_string = 'host={} dbname={} user={} password={}'.format(configs['hostdb'], configs['dbname'], configs['user'], configs['password'])
	conn = psycopg2.connect(conn_string)
	cur = conn.cursor()

	return conn, cur

def toBit(x):
	return "'1'" if x == 'true' else "'0'"

if __name__ == "__main__":
	main(sys.argv[1:])