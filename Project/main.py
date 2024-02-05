import ast

import psycopg2, time
from flask import jsonify, request, Flask
import hmac, hashlib, base64, json  # token
from dotenv import load_dotenv
import os

app = Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

secret_key = '52d3f853c19f8b63c0918c126422aa2d99b1aef33ec63d41dea4fadf19406e54'


def gera_token(payload):
    payload = json.dumps(payload).encode()

    # header
    header = json.dumps({
        'typ': 'JWT',
        'alg': 'HS256'
    }).encode()
    b64_header = base64.urlsafe_b64encode(header).decode()

    # payload
    b64_payload = base64.urlsafe_b64encode(payload).decode()

    # signature
    signature = hmac.new(
        key=secret_key.encode(),
        msg=f'{b64_header}.{b64_payload}'.encode(),
        digestmod=hashlib.sha256
    ).digest()

    jwt = f'{b64_header}.{b64_payload}.{base64.urlsafe_b64encode(signature).decode()}'
    return jwt


def descodifica_token(jwt):
    b64_header, b64_payload, b64_signature = jwt.split('.')

    b64_signature_checker = base64.urlsafe_b64encode(
        hmac.new(
            key=secret_key.encode(),
            msg=f'{b64_header}.{b64_payload}'.encode(),
            digestmod=hashlib.sha256
        ).digest()
    ).decode()

    payload = json.loads(base64.urlsafe_b64decode(b64_payload))

    if b64_signature_checker != b64_signature:
        raise Exception('Assinatura inválida')

    return payload


##########################################################
# DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user = USER,
        password = PASSWORD,
        host = HOST,
        port = PORT,
        database = DATABASE)

    return db


##########################################################
# ENDPOINTS
##########################################################


@app.route('/')
def landing_page():
    return """

    Hello World (Python)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2022 Team<br/>
    <br/>
    """


# POST
@app.route('/dbproj/user', methods=['POST']) #DONE
def registaUtilizador():
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    print(payload)  # Print de todos os parametros passados pelo .json

    try:
        if "username" in payload and "password" in payload and "contacto" in payload:
            username = payload["username"]
            password = payload["password"]
            contacto = payload["contacto"]

            if "email" in payload:
                email = payload["email"]
            else:
                email = "-"

            if "cc" in payload and "morada" in payload:  # Comprador
                cc = payload["cc"]
                morada = payload["morada"]

                if "nif" in payload:
                    nif = payload["nif"]
                else:
                    nif = "-"

                querie = """INSERT INTO pessoa(username, password, contacto, email) VALUES(%s, %s, %s, %s);"""
                values = (username, password, contacto, email)

                cur.execute("BEGIN TRANSACTION;")
                cur.execute(querie, values)
                cur.execute("commit;")

                cur.execute("SELECT max(id) FROM pessoa;")
                rows = cur.fetchall()
                pessoa_id = int(rows[0][0])

                querie = """INSERT INTO comprador(cc, morada, nif, pessoa_id) VALUES(%s, %s, %s, %s);"""
                values = (cc, morada, nif, pessoa_id)

                cur.execute("BEGIN TRANSACTION;")
                cur.execute(querie, values)
                cur.execute("commit;")

                content = {'status': StatusCodes['success'], 'results': pessoa_id}
            elif "empresa" in payload and "nif" in payload and "morada" in payload:  # Vendedor
                if "token" in payload:
                    token = payload["token"]
                    print("ANTES: ", token)

                    aux_payload = descodifica_token(token)
                    print("DEPOIS: ", aux_payload)

                    cur.execute("""SELECT id FROM Pessoa WHERE username = %s and password = %s;""",
                                (aux_payload["username"], aux_payload["password"],))
                    aux_rows = cur.fetchall()
                    id = aux_rows[0][0]

                    cur.execute("""SELECT count(*) FROM Administrador WHERE pessoa_id = %s;""", (id,))
                    rows = cur.fetchall()
                    count = int(rows[0][0])

                    if count == 0:
                        content = {'results': 'invalid'}
                    else:
                        empresa = payload["empresa"]
                        nif = payload["nif"]
                        morada = payload["morada"]

                        querie = """INSERT INTO pessoa(username, password, contacto, email) VALUES(%s, %s, %s, %s);"""
                        values = (username, password, contacto, email)

                        cur.execute("BEGIN TRANSACTION;")
                        cur.execute(querie, values)
                        cur.execute("commit;")

                        cur.execute("SELECT max(id) FROM pessoa;")
                        rows = cur.fetchall()
                        pessoa_id = int(rows[0][0])

                        querie = """INSERT INTO vendedor(empresa, nif, morada, pessoa_id) VALUES(%s, %s, %s, %s);"""
                        values = (empresa, nif, morada, pessoa_id)

                        cur.execute("BEGIN TRANSACTION;")
                        cur.execute(querie, values)
                        cur.execute("commit;")

                        content = {'status': StatusCodes['success'], 'results': pessoa_id}
                else:
                    content = {'results': 'invalid'}
            elif "area" in payload:  # Administrador
                querie = """SELECT count(*) FROM Administrador;"""
                cur.execute(querie);

                rows = cur.fetchall()
                num = int(rows[0][0])
                print("Numero de admins: ", num);

                if num == 0:
                    area = payload["area"]

                    querie = """INSERT INTO pessoa(username, password, contacto, email) VALUES(%s, %s, %s, %s);"""
                    values = (username, password, contacto, email)

                    cur.execute("BEGIN TRANSACTION;")
                    cur.execute(querie, values)
                    cur.execute("commit;")

                    cur.execute("SELECT max(id) FROM pessoa;")
                    rows = cur.fetchall()
                    pessoa_id = int(rows[0][0])

                    querie = """INSERT INTO administrador(area, pessoa_id) VALUES(%s, %s);"""
                    values = (area, pessoa_id)

                    cur.execute("BEGIN TRANSACTION;")
                    cur.execute(querie, values)
                    cur.execute("commit;")

                    content = {'status': StatusCodes['success'], 'results': pessoa_id}
                else:
                    if "token" in payload:
                        token = payload["token"]
                        aux_payload = descodifica_token(token)

                        cur.execute("""SELECT id FROM Pessoa WHERE username = %s and password = %s;""",
                                    (aux_payload["username"], aux_payload["password"],))
                        aux_rows = cur.fetchall()
                        id = aux_rows[0][0]

                        cur.execute("""SELECT count(*) FROM Administrador WHERE pessoa_id = %s;""", (id,))
                        rows = cur.fetchall()
                        count = int(rows[0][0])

                        if count == 0:
                            content = {'results': 'invalid'}
                        else:
                            area = payload["area"]

                            querie = """INSERT INTO pessoa(username, password, contacto, email) VALUES(%s, %s, %s, %s);"""
                            values = (username, password, contacto, email)

                            cur.execute("BEGIN TRANSACTION;")
                            cur.execute(querie, values)
                            cur.execute("commit;")

                            cur.execute("SELECT max(id) FROM pessoa;")
                            rows = cur.fetchall()
                            pessoa_id = int(rows[0][0])

                            querie = """INSERT INTO administrador(area, pessoa_id) VALUES(%s, %s);"""
                            values = (area, pessoa_id)

                            cur.execute("BEGIN TRANSACTION;")
                            cur.execute(querie, values)
                            cur.execute("commit;")

                            content = {'status': StatusCodes['success'], 'results': pessoa_id}
                    else:
                        content = {'results': 'invalid'}
            else:
                content = {'results': 'invalid'}
        else:
            content = {'results': 'invalid'}
    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


@app.route('/dbproj/produto', methods=['POST']) #DONE
def addProduto():
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    print(payload) #Print de todos os parametros passados pelo .json

    try:
        if "marca" in payload and "stock" in payload and "preco" in payload and "titulo" in payload and "token" in payload:
            #id = payload["id"]
            marca = payload["marca"]
            stock = payload["stock"]
            preco = payload["preco"]
            titulo = payload["titulo"]
            token = payload["token"]

            #token related stuff
            aux_token = descodifica_token(token)

            cur.execute(""" SELECT id FROM pessoa WHERE username = %s AND password = %s;""", (aux_token["username"], aux_token["password"],))
            aux_rows = cur.fetchall()
            print(aux_rows)
            vendedor_id = aux_rows[0][0]

            if len(aux_rows) == 0:
                content = {'results': 'invalid'}
            else:
                print("vendedor id: " + str(vendedor_id))

                cur.execute("""SELECT COALESCE(max(id), 0)
                                FROM produto;""")

                aux_rows = cur.fetchall()
                currId = aux_rows[0][0] + 1

                print(currId)


                if ("descricao" in payload):
                    descricao = payload["descricao"]
                else:
                    descricao = "-"

                query = """ INSERT INTO 
                            produto(id, num_versao, titulo, marca, stock, descricao, preco, data, produto_id, produto_num_versao, vendedor_pessoa_id)
                            VALUES
                            (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values = (currId, 1, titulo, marca, stock, descricao, preco, currId, 1, vendedor_id)



                cur.execute("BEGIN TRANSACTION")
                cur.execute(query, values)
                cur.execute("COMMIT")


                if("processador" in payload and "sistema_operativo" in payload and "armazenamento" in payload and "camara" in payload):

                    processador = payload["processador"]
                    sistema_operativo = payload["sistema_operativo"]
                    armazenamento = payload["armazenamento"]
                    camara = payload["camara"]

                    query2 = """ INSERT INTO
                                computador(processador, sistema_operativo, armazenamento, camara, produto_id, produto_num_versao)
                                VALUES
                                (%s, %s, %s, %s, %s, %s)"""
                    values2 = (processador, sistema_operativo, armazenamento, camara, currId, 1)

                    cur.execute("BEGIN TRANSACTION")
                    cur.execute(query2, values2)
                    cur.execute("COMMIT")

                    content = {'status': StatusCodes['success'], 'results': currId}

                elif("comprimento" in payload and "largura" in payload and "peso" in payload and "resolucao" in payload):

                    comprimento = payload["comprimento"]
                    largura = payload["largura"]
                    peso = payload["peso"]
                    resolucao = payload["resolucao"]


                    query2 = """INSERT INTO
                                televisor(comprimento, largura, peso, resolucao, produto_id, produto_num_versao)
                                VALUES
                                (%s, %s, %s, %s, %s, %s)"""
                    values2 = (comprimento, largura, peso, resolucao, currId, 1)

                    cur.execute("BEGIN TRANSACTION")
                    cur.execute(query2, values2)
                    cur.execute("COMMIT")

                    content = {'status': StatusCodes['success'], 'results': currId}

                elif("modelo" in payload and "cor" in payload):

                    modelo = payload["modelo"]
                    cor = payload["cor"]


                    query2 = """INSERT INTO
                                smartphone(modelo, cor, produto_id, produto_num_versao)
                                VALUES
                                (%s, %s, %s, %s)"""
                    values2 = (modelo, cor, currId, 1)

                    cur.execute("BEGIN TRANSACTION")
                    cur.execute(query2, values2)
                    cur.execute("COMMIT")


                    content = {'status': StatusCodes['success'], 'results': currId}

                else:
                    content = {'results': 'invalid'}
        else:
            content = {'results': 'invalid'}
    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


@app.route('/dbproj/order', methods=['POST']) #DONE
def efetuaCompra():
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    print(payload)  # Print de todos os parametros passados pelo .json

    try:
        if "cart" in payload and "token" in payload:
            token = payload["token"]
            cart = payload["cart"]
            total = 0

            aux_payload = descodifica_token(token)

            # Verificar se é um Comprador, obtendo o ID da Pessoa
            cur.execute("""SELECT pessoa_id 
                            FROM Comprador 
                            WHERE pessoa_id = (SELECT id FROM Pessoa WHERE username = %s and password = %s);""",
                        (aux_payload["username"], aux_payload["password"],))
            aux_rows = cur.fetchall()

            if len(aux_rows) == 0:
                content = {'results': 'invalid'}
            else:
                pessoa_id = aux_rows[0][0]

                if len(cart) == 0:
                    content = {'results': 'invalid'}
                else:
                    #lista = ast.literal_eval(cart)
                    lista = cart #devido à nova atualização do enunciado
                    flag = False #Flag para inserir a encomenda assim que um par (produto_id, quantidade) seja válido
                    encomendaId = 0 #Guardar o id da encomenda atual

                    for i in range(len(lista)):
                        produtoId = lista[i][0]
                        quantidade = lista[i][1]

                        cur.execute("""SELECT stock 
                                        FROM Produto 
                                        WHERE id = %s and num_versao = (SELECT max(num_versao) FROM Produto WHERE id = %s);""",
                                    (produtoId, produtoId,))
                        rows = cur.fetchall()
                        if rows != 0:
                            stock = rows[0][0]
                            if stock >= quantidade:
                                if not flag:
                                    querie = """INSERT INTO encomenda(data, total, comprador_pessoa_id) VALUES(CURRENT_TIMESTAMP(0), 0, %s);"""
                                    values = (pessoa_id,)

                                    cur.execute("BEGIN TRANSACTION;")
                                    cur.execute(querie, values)
                                    cur.execute("commit;")

                                    cur.execute("""SELECT max(id) FROM encomenda""")
                                    rows = cur.fetchall()
                                    encomendaId = rows[0][0]
                                    flag = True

                                cur.execute("""SELECT max(num_versao) FROM Produto WHERE id = %s;""", (produtoId,))
                                rows = cur.fetchall()
                                numVersao = rows[0][0]

                                #Inserir na tabela 'Quantidade'
                                querie = """INSERT INTO quantidade(numero, encomenda_id, produto_id, produto_num_versao) 
                                                VALUES(%s, %s, %s, %s);"""
                                values = (quantidade, encomendaId, produtoId, numVersao,)

                                cur.execute("BEGIN TRANSACTION;")
                                cur.execute(querie, values)
                                cur.execute("commit;")


                                #Atualizar o stock produto na tabela 'Produto', inserindo um novo registo
                                querie1 = """ SELECT marca, descricao, preco, vendedor_pessoa_id, titulo
                                              FROM produto
                                              WHERE produto.id = %s and produto.num_versao = %s;"""
                                values = (produtoId, numVersao,)
                                cur.execute(querie1, values)
                                rows = cur.fetchall()
                                versaoNova = numVersao + 1
                                stockNovo = stock - quantidade
                                marca = rows[0][0]
                                descricao = rows[0][1]
                                preco = rows[0][2]
                                vendedor_pessoa_id = rows[0][3]
                                titulo = rows[0][4]

                                querie2 = """INSERT
                                            INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id, produto_id, produto_num_versao)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                                values = (produtoId, versaoNova, titulo, marca, stockNovo, descricao, preco, vendedor_pessoa_id, produtoId, numVersao)

                                cur.execute("BEGIN TRANSACTION")
                                cur.execute(querie2, values)
                                cur.execute("COMMIT")


                                total += (quantidade*preco)


                    if flag:
                        querie = """UPDATE encomenda SET total = %s WHERE encomenda.id = (SELECT max(id) 
                                                                                            FROM encomenda)"""
                        values = (total,)

                        cur.execute("BEGIN TRANSACTION;")
                        cur.execute(querie, values)
                        cur.execute("commit;")

                if flag:
                    content = {'status': StatusCodes['success'], 'results': encomendaId}
                else:
                    content = {'status': StatusCodes['success'], 'results': 'order denied'}
        else:
            content = {'results': 'invalid'}
    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


@app.route('/dbproj/rating/<product_id>', methods=['POST']) #DONE
def deixaRating(product_id):
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    print(payload)  # Print de todos os parametros passados pelo .json
    print("product_id: ", product_id)

    try:
        if "rating" in payload and "comment" in payload and "token" in payload:
            token = payload["token"]

            aux_payload = descodifica_token(token)

            # Verificar se é um Comprador, obtendo o ID da Pessoa
            cur.execute("""SELECT pessoa_id 
                            FROM Comprador 
                            WHERE pessoa_id = (SELECT id FROM Pessoa WHERE username = %s and password = %s);""",
                        (aux_payload["username"], aux_payload["password"],))
            aux_rows = cur.fetchall()

            if len(aux_rows) == 0:
                content = {'results': 'invalid'}
            else:
                comment = payload["comment"]
                rating = payload["rating"]
                pessoa_id = aux_rows[0][0]

                if rating >= 0 and rating <= 5:
                    #Selecionar a última encomenda da pessoa em questão
                    cur.execute("""SELECT coalesce(max(id),0) 
									FROM encomenda
									WHERE comprador_pessoa_id = %s""", (pessoa_id,))
                    rows = cur.fetchall()
                    last_order = rows[0][0]

                    #A pessoa em questão já fez pelo menos uma encomenda
                    if last_order != 0:
                        cur.execute("""SELECT produto_num_versao
                                        FROM quantidade
                                        WHERE produto_id = %s and encomenda_id = %s;""",
                                    (product_id, last_order,))
                        rows = cur.fetchall()

                        #O produto em questão está presente na última encomenda
                        if len(rows) != 0:
                            versao = rows[0][0]

                            #Ver se o comprador já fez um rating relativo ao produto em questão presente na última encomenda do mesmo
                            cur.execute("""SELECT count(*)
                                            FROM rating
                                            WHERE comprador_pessoa_id = %s and produto_id = %s and produto_num_versao = %s""",
                                        (pessoa_id, product_id, versao,))
                            rows = cur.fetchall()
                            res1 = rows[0][0]

                            if res1 == 0:
                                querie = """INSERT INTO rating(classificacao, comentario, comprador_pessoa_id, produto_id, produto_num_versao) 
                                            VALUES(%s, %s, %s, %s, %s);"""
                                values = (rating, comment, pessoa_id, product_id, versao,)

                                cur.execute("BEGIN TRANSACTION;")
                                cur.execute(querie, values)
                                cur.execute("commit;")

                                content = {'status': StatusCodes['success']}
                            else:
                                content = {'results': 'considering your last order, you already post a rating of that product'}
                        else:
                            content = {'results': 'your last order does not contain the product that you selected'}
                    else:
                        content = {'results': 'you have not done yet any order'}
                else:
                    content = {'results': 'invalid rating'}
        else:
            content = {'results': 'invalid'}
    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)

@app.route('/dbproj/questions/<product_id>', methods=['POST']) #DONE
def motherComment(product_id):
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()

    numPost = 1

    # got get the max(id) of forum posts here for id
    cur.execute("""SELECT COALESCE(max(id), 0)
                    FROM forum;""")
    aux_rows = cur.fetchall()
    print(aux_rows[0][0])
    threadId = aux_rows[0][0] + 1
    print(threadId)


    #cur.execute(""" SELECT max(id)
     #               FROM forum
      #              WHERE forum.produto_id = %s AND forum.produto_num_versao = %s;""",)

    #aux_rows = cur.fetchall()

    #if(len(aux_rows) == 0):
     #   id = 1

    #else:
     #   id = aux_rows[0][0] + 1

    # got get the max(id) of forum posts here for id


    #cur.execute(""" SELECT max(versao)
     #               FROM produto
      #              WHERE produto.id = %s""", (product_id))

    #aux_rows = cur.fetchall()
    #versionNr = aux_rows[0][0]


    try:
        if "post" in payload and "token" in payload:

            aux_payload = descodifica_token(payload["token"])



            cur.execute(""" SELECT pessoa_id 
                            FROM Comprador 
                            WHERE pessoa_id = (SELECT id FROM Pessoa WHERE username = %s and password = %s);""",
                        (aux_payload["username"], aux_payload["password"],))
            aux_rows = cur.fetchall()
            print(aux_rows[0][0])

            if len(aux_rows) == 0:
                content = {'results': 'invalid'}
            else:
                post = payload["post"]
                pessoa_id = aux_rows[0][0]

                versionNr = payload["produto_num_versao"]

                query = """ INSERT INTO 
                            forum(id, num_post, post, forum_id, forum_num_post, produto_id, produto_num_versao)
                            VALUES
                            (%s, %s, %s, %s, %s, %s, %s);
                            """
                values = (threadId, numPost, post, threadId, numPost, product_id, versionNr)


                queryAux = """  INSERT INTO
                                pessoa_forum(pessoa_id, forum_id, forum_num_post)
                                VALUES
                                (%s, %s, %s);"""
                valuesAux = (pessoa_id, threadId, numPost)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(query, values)
                cur.execute(queryAux, valuesAux)
                cur.execute("COMMIT;")

                content = {'status': StatusCodes['success'], 'results': threadId}

        else:
            content = {'results': 'no post'}

    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)

@app.route('/dbproj/questions/<product_id>/<parent_question_id>', methods=['POST']) #DONE
def childComment(product_id, parent_question_id):
    print("yo")
    conn = db_connection()
    cur = conn.cursor()

    print("im here early")

    payload = request.get_json()

    print("im here")

    cur.execute(""" SELECT COALESCE(max(num_post), 0), produto_num_versao
                    FROM forum
                    WHERE forum.id = %s GROUP BY produto_num_versao""", (parent_question_id,))

    aux_rows = cur.fetchall()

    try:
        if (len(aux_rows) > 0):
            numPost = aux_rows[0][0] + 1
            print(numPost)
            prodVersao = aux_rows[0][1]
            print(prodVersao)

            if("post" in payload and "token" in payload):

                post = payload["post"]

                aux_payload = descodifica_token(payload["token"])


                cur.execute(""" SELECT id 
                                FROM pessoa 
                                WHERE username = %s and password = %s;""",
                            (aux_payload["username"], aux_payload["password"],))

                aux_rows = cur.fetchall()

                if(len(aux_rows) == 0):
                    content = {'results': 'invalid'}
                else:

                    pessoa_id = aux_rows[0][0]
                    print(pessoa_id)

                    query = """ INSERT INTO 
                                forum(id, num_post, post, forum_id, forum_num_post, produto_id, produto_num_versao)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s);"""
                    values = (parent_question_id, numPost, post, parent_question_id, numPost, product_id, prodVersao,)

                    queryAux = """  INSERT INTO
                                    pessoa_forum(pessoa_id, forum_id, forum_num_post)
                                    VALUES
                                    (%s, %s, %s);"""
                    valuesAux = (pessoa_id, parent_question_id, numPost,)

                    cur.execute("BEGIN TRANSACTION")
                    cur.execute(query, values)
                    cur.execute(queryAux, valuesAux)
                    cur.execute("COMMIT;")

                    content = {'status': StatusCodes['success'], 'results': parent_question_id}

            else:
                content = {'results': 'no post'}

        else:
            content = {'results': 'no parent thread found'}

    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)

# PUT
@app.route('/dbproj/user', methods=['PUT']) #DONE
def autenticaUtilizador():
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()

    try:
        if "username" in payload and "password" in payload:
            username = payload["username"]
            password = payload["password"]

            querie = """SELECT id FROM pessoa WHERE pessoa.username = %s AND pessoa.password = %s;"""
            values = (username, password)

            cur.execute(querie, values)
            rows = cur.fetchall()

            if (len(rows) > 0):
                token = gera_token(payload)
                content = {'token': token}
            else:
                content = {'results': 'invalid'}
        else:
            content = {'results': 'invalid'}
    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


@app.route('/dbproj/produto/<id>', methods=['PUT']) #DONE
def atualizar_produto(id: str):
    if not id.isdigit():
        return jsonify({'error' : 'Invalid product Id was provided', 'code': StatusCodes['api_error']})

    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()

    try:
        find_product_stmt = """ SELECT id
                                FROM produto
                                WHERE produto.id = %s;"""
        cur.execute(find_product_stmt, [id])
        rows = cur.fetchall()
        if(len(rows) > 0):


            versions = list()
            #find max version since through sql seems ill have to use cursors
            for row in rows:
                versions.append(row[1])
                titulo = row[2]
                marca = row[3]
                stock = row[4]
                descricao = row[5]
                preco = row[6]
                vendedor_pessoa_id = row[10]

            new_ver = int(max(versions)) + 1


            if("stock" in payload and "preco" in payload and "descricao" in payload):   #vem com tudo   #TODO nao adicionei produto_id porque o jo tirou
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, produto_id, produto_num_versao, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = ([id], new_ver, titulo, marca, payload["stock"], payload["descricao"], payload["preco"], [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif("stock" in payload and "preco" in payload and "descricao" not in payload): #nao vem com descricao
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %S, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = ([id], new_ver, titulo, marca, payload["stock"], descricao, payload["preco"], [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif("stock" in payload and "preco" not in payload and "descricao" in payload): #nao vem com preço
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %S, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = ([id], new_ver, titulo, marca, payload["stock"], payload["descricao"], preco, [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif("stock" in payload and "preco" not in payload and "descricao" not in payload): #so vem com stock
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %S, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = (
                [id], new_ver, titulo, marca, payload["stock"], descricao, preco, [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif("stock" not in payload and "preco" in payload and "descricao" in payload): #nao vem com stock
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %S, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = (
                    [id], new_ver, titulo, marca, stock, payload["descricao"], payload["preco"], [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif ("stock" not in payload and "preco" in payload and "descricao" not in payload): #so vem com preço
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %S, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = (
                    [id], new_ver, titulo, marca, stock, descricao, payload["preco"], [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif ("stock" not in payload and "preco" not in payload and "descricao" in payload):    #so vem com descriçao
                add_version_stmt = """  INSERT
                                        INTO produto(id, num_versao, titulo, marca, stock, descricao, preco, data, vendedor_pessoa_id)
                                        VALUES
                                        (%s, %s, %s, %s, %s, %S, %s, CURRENT_TIMESTAMP(0), %s, %s, %s)"""
                values_update = (
                    [id], new_ver, titulo, marca, stock, payload["descricao"], payload["preco"], [id], int(max(versions)), vendedor_pessoa_id)

                cur.execute("BEGIN TRANSACTION")
                cur.execute(add_version_stmt, values_update)
                cur.execute("COMMIT")

                content = {'status': StatusCodes['success'], 'results': [id]}

            elif ("stock" not in payload and "preco" not in payload and "descricao" not in payload):    #nao vem com nada manda erro
                content = {"code": StatusCodes['api_error']}

            """
            #TODO not sure if user needs to also input old values to update everything even if still the same or only one value, consult after
            add_version_stmt = """  """INSERT INTO
                                    produto(id, marca, stock, descricao, preco, data, produto_id)
                                    VALUES
                                    """"""(%s, %s, %s, %s, %s, TIMESTAMP, %s)""""""
            values_update = ([id], payload["marca"], payload["stock"], payload["descricao"], payload["preco"], payload["produto_id"])
            cur.execute("BEGIN TRANSACTION")
            cur.execute(add_version_stmt, values_update)
            cur.execute("COMMIT")
            content = {'status': StatusCodes['success'], 'results': [id]}
            """

        else:
            content = {"code": StatusCodes['api_error']}

    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


#GET
@app.route('/dbproj/produto/<produto_id>', methods=['GET']) #DONE
def detalhes_produto(produto_id: str):
    #logger.info(f"Detalhes e histórico para produto com id {produto_id}")
    if not produto_id.isdigit():
        #logger
        return jsonify({'error' : 'Invalid product Id was provided', 'code': StatusCodes['api_error']})

    conn = db_connection()
    cur = conn.cursor()

    try:

        find_if_product = """   SELECT id
                                FROM produto
                                WHERE id = %s"""
        cur.execute(find_if_product, [produto_id])
        rows = cur.fetchall()
        if(rows.len > 0):   #produto existe

            #Do query to find if any of the subtables have a product with provided Id, if yes, do query also using data from that table
            find_comp_stmt =    """     SELECT produto_id
                                        FROM computador
                                        WHERE produto_id = %s;
                                """

            cur.execute(find_comp_stmt, [produto_id])
            rows = cur.fetchall()

            if(rows.len() > 0):
                comp_details_stmt = """  SELECT produto.titulo "Titulo", produto.stock "Stock", produto.preco "Preço", produto.num_versao "Versão", produto.marca "Marca", computador.processador "Processador", computador.sistema_operativo "SO", computador.armazenamento "Armazenamento", computador.camara "Câmara", produto.descricao "Descricao", produto.data "Data alteração"
                                            FROM produto, computador
                                            WHERE id = %s AND produto.id = computador.produto_id
                                            ORDER BY data ASC;"""

                cur.execute("BEGIN TRANSACTION")
                cur.execute(comp_details_stmt, [produto_id])
                cur.execute("COMMIT")

                rows = cur.fetchall()

                if (rows.len() > 0):
                    content = {"code": StatusCodes['success']}
                else:
                    content = {"code": StatusCodes['api_error']}

            else:
                find_tel_stmt = """     SELECT produto_id
                                        FROM televisor
                                        WHERE produto_id = %s;"""

                cur.execute(find_tel_stmt, [produto_id])
                rows = cur.fetchall()
                if (rows.len() > 0):
                    tel_details_stmt = """  SELECT produto.titulo "Titulo", produto.stock "Stock", produto.preco "Preço", produto.num_versao "Versão", produto.marca "Marca", televisor.comprimento "Comprimento", televisor.largura "Largura", televisor.peso "Peso", televisor.resolucao "Resolução", produto.descricao "Descricao", produto.data "Data alteração"
                                            FROM produto, televisor
                                            WHERE id = %s AND produto.id = televisor.produto_id
                                            ORDER BY data ASC;"""

                    cur.execute("BEGIN TRANSACTION")
                    cur.execute(tel_details_stmt, [produto_id])
                    cur.execute("COMMIT")

                    rows = cur.fetchall()

                    if (rows.len() > 0):
                        content = {"code": StatusCodes['success']}
                    else:
                        content = {"code": StatusCodes['api_error']}

                else:
                    find_phone_stmt = """   SELECT produto_id
                                            FROM smartphone
                                            WHERE produto_id = %s;"""

                    cur.execute(find_phone_stmt, [produto_id])
                    rows = cur.fetchall()
                    if (rows.len() > 0):
                        phone_details_stmt = """  SELECT produto.titulo "Titulo", produto.stock "Stock", produto.preco "Preço", produto.num_versao "Versão", produto.marca "Marca", smartphone.modelo "Modelo", smartphone.cor "Cor", produto.descricao "Descricao", produto.data "Data alteração"
                                                FROM produto, smartphone
                                                WHERE id = %s AND produto.id = smartphone.produto_id
                                                ORDER BY data ASC;"""

                        cur.execute("BEGIN TRANSACTION")
                        cur.execute(phone_details_stmt, [produto_id])
                        cur.execute("COMMIT")

                        rows = cur.fetchall()

                        if (rows.len() > 0):
                            content = {"code": StatusCodes['success']}
                        else:
                            content = {"code": StatusCodes['api_error']}

                    else:
                        #if not a specific type of product, prints general table
                        produto_details_stmt = """  SELECT titulo "Titulo", stock "Stock", marca "Marca", preco "Preço", num_versao "Versão", descricao "Descricao", data "Data alteração"
                                                    FROM produto
                                                    WHERE id = %s 
                                                    ORDER BY data ASC;"""

                        cur.execute("BEGIN TRANSACTION")
                        cur.execute(produto_details_stmt, [produto_id])
                        cur.execute("COMMIT")

                        rows = cur.fetchall()

                        if (rows.len() > 0):
                            content = {"code": StatusCodes['success']}
                        else:
                            content = {"code": StatusCodes['api_error']}

        else:
            #TODO error message for product not found
            print("no error")


    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


@app.route('/proj/report/year', methods=['GET']) #DONE
def obterEstatisticas():
    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    print(payload) #Print de todos os parametros passados pelo .json

    try:
        if "token" in payload:
            token = payload["token"]
            print("ANTES: ", token)

            aux_payload = descodifica_token(token)
            print("DEPOIS: ", aux_payload)


            cur.execute("""SELECT count(*) FROM Administrador WHERE pessoa_id = (SELECT id 
                                                                                    FROM Pessoa 
                                                                                    WHERE username = %s and password = %s);""",
                        (aux_payload["username"], aux_payload["password"],))
            rows = cur.fetchall()
            count = int(rows[0][0])

            if count == 0:
                content = {'results': 'invalid'}
            else:
                cur.execute("""SELECT extract(month from data), sum(total), count(*)
                                FROM encomenda
                                WHERE data > CURRENT_DATE - INTERVAL '12 months'
                                GROUP BY extract(month from data), extract(year from data)
                                ORDER BY extract(year from data) asc, extract(month from data) asc""",
                            (aux_payload["username"], aux_payload["password"],))
                rows = cur.fetchall()

                content = {'status': StatusCodes['success'], 'results': rows}


    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)

#GET
@app.route('/dbproj/user/<user_id>', methods=['GET']) #DONE
def consultaNotificacoes(user_id):

    conn = db_connection()
    cur = conn.cursor()


    try:
        payload = request.get_json()

        if "token" in payload:
            aux_payload = descodifica_token(payload["token"])
            cur.execute(""" SELECT id 
                            FROM pessoa
                            WHERE %s = (SELECT id FROM Pessoa WHERE username = %s and password = %s);""",(user_id, aux_payload["username"], aux_payload["password"],))

            aux_rows = cur.fetchall()
            if(len(aux_rows) == 0):
                content = {'results': 'invalid'}
            else:

                #TODO error is in query
                cur.execute("SELECT id, mensagem FROM notificacao, notificacao_pessoa WHERE notificacao.id = notificacao_pessoa.notificacao_id AND notificacao_pessoa.pessoa_id = %s;", (user_id,))


                retRows = cur.fetchall()
                print(retRows)      #is coming out empty

                if (len(retRows) > 0):
                    content = {"code": StatusCodes['success'], "return" : retRows}
                else:
                    content = {"code": StatusCodes['api_error'], "return" : retRows}

        else:
            content = {'results': 'invalid'}

    except (Exception, psycopg2.DatabaseError) as error:
        content = {'error:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(content)


# MAIN
if __name__ == "__main__":
    time.sleep(1)  # just to let the DB start before this print :-)
    
    load_dotenv()
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    DATABASE = os.getenv('DATABASE')

    app.run(host="localhost", port=8080, debug=True, threaded=True)
