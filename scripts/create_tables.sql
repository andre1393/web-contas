CREATE TABLE tb_all_contas (
	conta VARCHAR(50) NOT NULL,
	data_vencimento DATE NOT NULL,
	data_pagamento DATE,
	valor_conta NUMERIC(9,2),
	valor_pago NUMERIC(9,2),
	pago VARCHAR(3) NOT NULL,
	pagador VARCHAR(20),
	recorrente VARCHAR(3) NOT NULL,
	valor_igual VARCHAR(3) NOT NULL,
	parcelado VARCHAR(3) NOT NULL,
	qtd_parcelas SMALLINT,
	PRIMARY KEY(conta, data_vencimento)
)