create or replace FUNCTION notificacaoVendedor() 
returns TRIGGER
language plpgsql
as $$
	declare
		id_notificacao integer;	--id da notificação criada
		id_forum integer;
		num_post_forum integer;
		
		id_pessoa integer;		--do vendedor
		id_produto integer;
			
		BEGIN
			INSERT INTO notificacao(mensagem) VALUES ('Nova questão sobre um dos seus produtos');
			
			SELECT max(id) into id_notificacao
			FROM notificacao;
			
			SELECT id INTO id_forum FROM forum WHERE id = NEW.id;
			SELECT num_post INTO num_post_forum FROM forum WHERE num_post = NEW.num_post;
			
			--SELECT pessoa_id INTO id_pessoa FROM pessoa_forum WHERE forum_id = NEW.id;
			
			SELECT produto_id INTO id_produto FROM forum WHERE forum_id = NEW.id;
			
			SELECT vendedor_pessoa_id INTO id_pessoa FROM produto WHERE produto.id = NEW.produto_id;
			
			INSERT INTO notificacao_forum(notificacao_id, forum_id, forum_num_post) VALUES (id_notificacao, id_forum, num_post_forum);
			INSERT INTO notificacao_pessoa(notificacao_id, pessoa_id) VALUES (id_notificacao, id_pessoa);
			RETURN NEW;
		END;
	$$;
	
DROP trigger IF EXISTS TV ON forum;
	
CREATE OR REPLACE TRIGGER TV
AFTER INSERT ON forum
FOR EACH ROW
	EXECUTE PROCEDURE notificacaoVendedor();