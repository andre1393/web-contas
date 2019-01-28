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

CREATE TABLE tb_gastos (
	conta VARCHAR(50) NOT NULL,
	data_pagamento DATE NOT NULL,
	valor NUMERIC(9,2) NOT NULL,
	pagador VARCHAR(20),
	categoria VARCHAR(20),
	obs VARCHAR(255),
	PRIMARY KEY(conta, data_pagamento)
)