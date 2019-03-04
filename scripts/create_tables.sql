CREATE TABLE tb_all_contas (
	conta VARCHAR(50) NOT NULL,
	dia_vencimento SMALLINT NOT NULL,
	tipo_conta VARCHAR(30) NOT NULL,
	qtd_parcelas SMALLINT,
	valor_igual VARCHAR(3) NOT NULL,
	valor_conta NUMERIC(9,2),
	categoria VARCHAR(20),
	PRIMARY KEY(conta, dia_vencimento)
)

CREATE TABLE tb_contas_pagas (
	conta VARCHAR(50) NOT NULL,
	data_pagamento DATE NOT NULL,
	data_vencimento DATE,
	pagador VARCHAR(20),
	valor_pago NUMERIC(9, 2) NOT NULL,
	categoria VARCHAR(20),
	obs VARCHAR(255),
	PRIMARY KEY(conta, data_pagamento)
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