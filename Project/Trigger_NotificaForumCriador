create or replace FUNCTION notificacaoResposta() 
returns TRIGGER
language plpgsql
as $$
	declare
		id_notificacao integer;	--id da notificação criada
		id_forum integer;
		num_post_forum integer;
		
		id_pessoa integer;
			
		BEGIN
			INSERT INTO notificacao(mensagem) VALUES ('Nova resposta à sua thread');
			
			SELECT max(id) into id_notificacao
			FROM notificacao;
			
			SELECT id INTO id_forum FROM forum WHERE id = NEW.id;
			SELECT num_post INTO num_post_forum FROM forum WHERE num_post = NEW.num_post;
			
			SELECT pessoa_id INTO id_pessoa FROM pessoa_forum WHERE forum_id = NEW.id;
			
			INSERT INTO notificacao_forum(notificacao_id, forum_id, forum_num_post) VALUES (id_notificacao, id_forum, num_post_forum);
			INSERT INTO notificacao_pessoa(notificacao_id, pessoa_id) VALUES (id_notificacao, id_pessoa);
			RETURN NEW;
		END;
	$$;
	
	DROP trigger IF EXISTS TF ON forum;
	
CREATE OR REPLACE TRIGGER TF
AFTER INSERT ON forum
FOR EACH ROW
	EXECUTE PROCEDURE notificacaoResposta();