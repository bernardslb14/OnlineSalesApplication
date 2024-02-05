DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE vendedor (
	empresa	 VARCHAR(512) NOT NULL,
	nif	 NUMERIC(9,0) NOT NULL,
	morada	 VARCHAR(512) NOT NULL,
	pessoa_id INTEGER,
	PRIMARY KEY(pessoa_id)
);

CREATE TABLE produto (
	id		 INTEGER,
	num_versao	 INTEGER,
	titulo		 VARCHAR(512) NOT NULL,
	marca		 VARCHAR(512) NOT NULL,
	stock		 INTEGER NOT NULL,
	descricao		 VARCHAR(512),
	preco		 NUMERIC(8,2) NOT NULL,
	data		 TIMESTAMP NOT NULL,
	produto_id	 INTEGER NOT NULL,
	produto_num_versao INTEGER NOT NULL,
	vendedor_pessoa_id INTEGER NOT NULL,
	PRIMARY KEY(id,num_versao)
);

CREATE TABLE computador (
	processador	 VARCHAR(512) NOT NULL,
	sistema_operativo	 VARCHAR(512) NOT NULL,
	armazenamento	 VARCHAR(512) NOT NULL,
	camara		 BOOL NOT NULL,
	produto_id	 INTEGER,
	produto_num_versao INTEGER,
	PRIMARY KEY(produto_id,produto_num_versao)
);

CREATE TABLE televisor (
	comprimento	 NUMERIC(6,2) NOT NULL,
	largura		 NUMERIC(6,2) NOT NULL,
	peso		 NUMERIC(4,2) NOT NULL,
	resolucao		 VARCHAR(512) NOT NULL,
	produto_id	 INTEGER,
	produto_num_versao INTEGER,
	PRIMARY KEY(produto_id,produto_num_versao)
);

CREATE TABLE smartphone (
	modelo		 VARCHAR(512) NOT NULL,
	cor		 VARCHAR(512) NOT NULL,
	produto_id	 INTEGER,
	produto_num_versao INTEGER,
	PRIMARY KEY(produto_id,produto_num_versao)
);

CREATE TABLE administrador (
	area	 VARCHAR(512) NOT NULL,
	pessoa_id INTEGER,
	PRIMARY KEY(pessoa_id)
);

CREATE TABLE comprador (
	cc	 VARCHAR(12) NOT NULL,
	morada	 VARCHAR(512) NOT NULL,
	nif	 NUMERIC(9,0),
	pessoa_id INTEGER,
	PRIMARY KEY(pessoa_id)
);

CREATE TABLE pessoa (
	id	 SERIAL,
	username VARCHAR(512) UNIQUE NOT NULL,
	password VARCHAR(512) NOT NULL,
	contacto NUMERIC(9,0) NOT NULL,
	email	 VARCHAR(512),
	PRIMARY KEY(id)
);

CREATE TABLE encomenda (
	id			 Serial,
	data		 TIMESTAMP NOT NULL,
	total		 NUMERIC(8,2) NOT NULL,
	comprador_pessoa_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE rating (
	classificacao	 INTEGER NOT NULL,
	comentario		 VARCHAR(512),
	comprador_pessoa_id	 INTEGER,
	produto_id		 INTEGER,
	produto_num_versao	 INTEGER,
	PRIMARY KEY(comprador_pessoa_id,produto_id,produto_num_versao)
);

CREATE TABLE forum (
	id		 INTEGER,
	num_post		 INTEGER,
	post		 VARCHAR(512) NOT NULL,
	forum_id		 INTEGER NOT NULL,
	forum_num_post	 INTEGER NOT NULL,
	produto_id	 INTEGER NOT NULL,
	produto_num_versao INTEGER NOT NULL,
	PRIMARY KEY(id,num_post)
);

CREATE TABLE notificacao (
	id	 Serial,
	mensagem VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE quantidade (
	numero		 NUMERIC(8,0) NOT NULL,
	encomenda_id	 INTEGER,
	produto_id	 INTEGER,
	produto_num_versao INTEGER,
	PRIMARY KEY(encomenda_id,produto_id,produto_num_versao)
);

CREATE TABLE notificacao_encomenda (
	notificacao_id INTEGER,
	encomenda_id	 INTEGER NOT NULL,
	PRIMARY KEY(notificacao_id)
);

CREATE TABLE notificacao_forum (
	notificacao_id INTEGER,
	forum_id	 INTEGER NOT NULL,
	forum_num_post INTEGER NOT NULL,
	PRIMARY KEY(notificacao_id)
);

CREATE TABLE notificacao_pessoa (
	notificacao_id INTEGER,
	pessoa_id	 INTEGER,
	PRIMARY KEY(notificacao_id,pessoa_id)
);

CREATE TABLE pessoa_forum (
	pessoa_id	 INTEGER,
	forum_id	 INTEGER,
	forum_num_post INTEGER,
	PRIMARY KEY(pessoa_id,forum_id,forum_num_post)
);

ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE produto ADD CONSTRAINT produto_fk1 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE produto ADD CONSTRAINT produto_fk3 FOREIGN KEY (vendedor_pessoa_id) REFERENCES vendedor(pessoa_id);
ALTER TABLE computador ADD CONSTRAINT computador_fk1 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE televisor ADD CONSTRAINT televisor_fk1 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE smartphone ADD CONSTRAINT smartphone_fk1 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE encomenda ADD CONSTRAINT encomenda_fk1 FOREIGN KEY (comprador_pessoa_id) REFERENCES comprador(pessoa_id);
ALTER TABLE rating ADD CONSTRAINT rating_fk1 FOREIGN KEY (comprador_pessoa_id) REFERENCES comprador(pessoa_id);
ALTER TABLE rating ADD CONSTRAINT rating_fk2 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE forum ADD CONSTRAINT forum_fk1 FOREIGN KEY (forum_id, forum_num_post) REFERENCES forum(id, num_post);
ALTER TABLE forum ADD CONSTRAINT forum_fk3 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE quantidade ADD CONSTRAINT quantidade_fk1 FOREIGN KEY (encomenda_id) REFERENCES encomenda(id);
ALTER TABLE quantidade ADD CONSTRAINT quantidade_fk2 FOREIGN KEY (produto_id, produto_num_versao) REFERENCES produto(id, num_versao);
ALTER TABLE notificacao_encomenda ADD CONSTRAINT notificacao_encomenda_fk1 FOREIGN KEY (notificacao_id) REFERENCES notificacao(id);
ALTER TABLE notificacao_encomenda ADD CONSTRAINT notificacao_encomenda_fk2 FOREIGN KEY (encomenda_id) REFERENCES encomenda(id);
ALTER TABLE notificacao_forum ADD CONSTRAINT notificacao_forum_fk1 FOREIGN KEY (notificacao_id) REFERENCES notificacao(id);
ALTER TABLE notificacao_forum ADD CONSTRAINT notificacao_forum_fk2 FOREIGN KEY (forum_id, forum_num_post) REFERENCES forum(id, num_post);
ALTER TABLE notificacao_pessoa ADD CONSTRAINT notificacao_pessoa_fk1 FOREIGN KEY (notificacao_id) REFERENCES notificacao(id);
ALTER TABLE notificacao_pessoa ADD CONSTRAINT notificacao_pessoa_fk2 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE pessoa_forum ADD CONSTRAINT pessoa_forum_fk1 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE pessoa_forum ADD CONSTRAINT pessoa_forum_fk2 FOREIGN KEY (forum_id, forum_num_post) REFERENCES forum(id, num_post);