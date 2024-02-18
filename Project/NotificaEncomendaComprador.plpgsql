create or replace procedure notificacaoEncomenda()
language plpgsql
as $$
declare
	id_notificacao integer;
	id_encomenda integer;
	id_comprador integer;

begin
	INSERT into notificacao(mensagem) VALUES ('Nova compra efetuada');
	
	SELECT max(id) into id_notificacao
	FROM notificacao;
	
	SELECT max(id) into id_encomenda
	FROM encomenda;
	
	INSERT into notificacao_encomenda(notificacao_id, encomenda_id) VALUES (id_notificacao, id_encomenda);
	
																
	SELECT comprador_pessoa_id into id_comprador
	FROM encomenda
	WHERE id = id_encomenda;
	
	INSERT into notificacao_pessoa(notificacao_id, pessoa_id) VALUES (id_notificacao, id_comprador);
	
end;
$$;


create or replace function F_trig1() returns trigger
language plpgsql
as $$
begin
	call notificacaoEncomenda();
	return new;
end;
$$;

create or replace trigger tai_encomenda
after insert on encomenda
for each statement
	execute procedure F_trig1();