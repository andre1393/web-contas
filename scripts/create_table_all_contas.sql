CREATE TABLE tb_all_contas (
                               conta VARCHAR(50) NOT NULL,
                               dia_vencimento VARCHAR(2) NOT NULL,
                               tipo_conta VARCHAR(30) NOT NULL,
                               qtd_parcelas SMALLINT,
                               valor_igual VARCHAR(3) NOT NULL,
                               valor_conta NUMERIC(9,2),
                               categoria VARCHAR(20),
                               obs VARCHAR(255),
                               PRIMARY KEY(conta, dia_vencimento)
)