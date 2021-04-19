CREATE TABLE tb_gastos (
	conta VARCHAR(50) NOT NULL,
	data_pagamento DATE NOT NULL,
	tipo_gasto VARCHAR(50) NOT NULL,
	data_vencimento DATE,
	valor_pago NUMERIC(9,2) NOT NULL,
	pagador VARCHAR(20),
	categoria VARCHAR(20),
	obs VARCHAR(255),
	PRIMARY KEY(conta, data_pagamento)
)