create or replace procedure notificacaoVendedores()
language plpgsql
as $$
declare
	id_notificacao integer;
	id_vendedor integer;
	contador integer;
	
	c1 cursor for
		SELECT DISTINCT vendedor_pessoa_id
		FROM quantidade, produto
		WHERE quantidade.produto_id = produto.produto_id and quantidade.encomenda_id = (SELECT max(id) FROM encomenda);

begin
	SELECT max(id) into id_notificacao
	FROM notificacao;

	open c1;
	loop
		fetch c1 into id_vendedor;
		exit when not found;
		
		SELECT count(*) into contador
		FROM notificacao_pessoa
		WHERE pessoa_id = id_vendedor and notificacao_id = id_notificacao;
	
		if contador = 0 then
			INSERT into notificacao_pessoa(notificacao_id, pessoa_id) VALUES (id_notificacao, id_vendedor);
		end if;
	end loop;
	close c1;
	
end;
$$;


create or replace function F_trig2() returns trigger
language plpgsql
as $$
begin
	call notificacaoVendedores();
	return new;
end;
$$;

create or replace trigger tai_quantidade
after insert on quantidade
for each statement
	execute procedure F_trig2();