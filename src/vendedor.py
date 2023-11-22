from pymongo import MongoClient
import redis
import json

def exportar_vendedores_mongodb_para_redis(mongo_uri, redis_host, redis_port, redis_password):
    # Conectar ao MongoDB
    cliente_mongo = MongoClient(mongo_uri)
    banco_de_dados_mongo = cliente_mongo.get_database("MercadoLivreRedis")
    colecao_vendedor_mongo = banco_de_dados_mongo.get_collection("Vendedor")

    # Conectar ao Redis
    cliente_redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    # Obter todos os documentos da coleção no MongoDB
    documentos_mongo = colecao_vendedor_mongo.find()

    # Iterar sobre os documentos e armazenar no Redis usando o nome do vendedor como chave
    for documento in documentos_mongo:
        nome_vendedor = documento['nome_vendedor']
        id_vendedor = str(documento['_id'])
        data_cadastro_vendedor = documento['data_cadastro']
        produtos = json.dumps(documento['produtos'])  # Convertendo a lista de produtos em uma string JSON

        # Armazenar no Redis usando o nome do vendedor como chave
        chave_redis = f"Vendedor:{nome_vendedor}"
        cliente_redis.hmset(chave_redis, {'_id': id_vendedor, 'nome_vendedor': nome_vendedor, 'data_cadastro': data_cadastro_vendedor, 'produtos': produtos})

    # Fechar as conexões
    cliente_mongo.close()
    cliente_redis.close()
    print("Importação concluída com sucesso")

def imprimir_vendedores_redis(redis_host, redis_port, redis_password):
    # Conectar ao Redis
    cliente_redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    # Obter todas as chaves no Redis (cada chave representa um vendedor)
    chaves_vendedores = cliente_redis.keys("Vendedor:*")

    # Verificar se há vendedores cadastrados
    if not chaves_vendedores:
        print("Nenhum vendedor cadastrado.")
    else:
        # Imprimir os nomes dos vendedores e obter a seleção do usuário
        print("Selecione um vendedor:")
        for i, chave_vendedor in enumerate(chaves_vendedores, start=1):
            nome_vendedor = cliente_redis.hget(chave_vendedor, 'nome_vendedor')
            print(f"{i}. {nome_vendedor}")

        # Pedir ao usuário para selecionar um vendedor pelo ID
        try:
            indice_selecionado = int(input("Digite o número correspondente ao vendedor que deseja visualizar: "))
        except ValueError:
            print("Entrada inválida. Digite um número válido.")
            return

        # Verificar se o índice está dentro dos limites
        if 1 <= indice_selecionado <= len(chaves_vendedores):
            # Obter a chave correspondente ao ID selecionado
            chave_vendedor_selecionado = chaves_vendedores[indice_selecionado - 1]
            dados_vendedor = cliente_redis.hgetall(chave_vendedor_selecionado)

            # Mostrar os dados do vendedor selecionado
            print(f"\nNome do vendedor: {dados_vendedor['nome_vendedor']}")
            print(f"Data de cadastro: {dados_vendedor['data_cadastro']}")

            # Converter a string JSON de produtos de volta em uma lista
            produtos = json.loads(dados_vendedor['produtos'])

            # Imprimir os detalhes de cada produto
            for produto in produtos:
                print(f"\nNome do Produto: {produto['nome_produto']}")
                print(f"Descrição: {produto['descricao']}")
                print(f"Preço: {produto['preco']}")
                print(f"Quantidade disponível: {produto['quantidade_disponivel']}")
            print("")
        else:
            print("Índice inválido. Selecione um número válido.")

    # Fechar a conexão
    cliente_redis.close()

def editar_vendedor(mongo_uri, redis_host, redis_port, redis_password):
    # Conectar ao Redis
    cliente_redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    # Conectar ao MongoDB
    cliente_mongo = MongoClient(mongo_uri)
    banco_de_dados_mongo = cliente_mongo.get_database("MercadoLivreRedis")
    colecao_vendedor_mongo = banco_de_dados_mongo.get_collection("Vendedor")

    # Obter todas as chaves no Redis (cada chave representa um vendedor)
    chaves_vendedores = cliente_redis.keys("Vendedor:*")

    if not chaves_vendedores:
        print("Nenhum vendedor cadastrado.")
    else:
        # Mostrar os nomes dos vendedores e obter a seleção do usuário
        print("Selecione um vendedor para editar:")
        for i, chave_vendedor in enumerate(chaves_vendedores, start=1):
            nome_vendedor = cliente_redis.hget(chave_vendedor, 'nome_vendedor')
            print(f"{i}. {nome_vendedor}")

        # Pedir ao usuário para selecionar um vendedor pelo índice
        try:
            indice_selecionado = int(input("Digite o número correspondente ao vendedor que deseja editar: "))
        except ValueError:
            print("Entrada inválida. Digite um número válido.")
            return

        # Verificar se o índice está dentro dos limites
        if 1 <= indice_selecionado <= len(chaves_vendedores):
            # Obter a chave correspondente ao índice selecionado
            chave_vendedor_selecionado = chaves_vendedores[indice_selecionado - 1]
            dados_vendedor = cliente_redis.hgetall(chave_vendedor_selecionado)

            # Mostrar os dados do vendedor selecionado
            print(f"\nNome do vendedor: {dados_vendedor['nome_vendedor']}")
            print(f"Data de cadastro: {dados_vendedor['data_cadastro']}")

            # Opção de editar o nome do vendedor
            novo_nome_vendedor = input(f"Digite o novo nome para o vendedor '{dados_vendedor['nome_vendedor']}' (ou pressione Enter para manter): ")

            # Verificar se o usuário deseja manter o valor existente
            if not novo_nome_vendedor:
                novo_nome_vendedor = dados_vendedor['nome_vendedor']

            # Atualizar a chave do vendedor no Redis
            nova_chave_redis = f"Vendedor:{novo_nome_vendedor}"
            cliente_redis.rename(chave_vendedor_selecionado, nova_chave_redis)

            # Atualizar o nome do vendedor no Redis
            cliente_redis.hset(nova_chave_redis, 'nome_vendedor', novo_nome_vendedor)

            # Atualizar o nome do vendedor nos produtos associados
            produtos = json.loads(dados_vendedor['produtos'])
            for produto in produtos:
                produto['nome_vendedor'] = novo_nome_vendedor

            # Atualizar a string JSON de produtos no Redis
            cliente_redis.hset(nova_chave_redis, 'produtos', json.dumps(produtos))

            # Atualizar o nome do vendedor no MongoDB
            filtro = {'nome_vendedor': dados_vendedor['nome_vendedor']}
            atualizacao = {'$set': {'nome_vendedor': novo_nome_vendedor}}
            colecao_vendedor_mongo.update_one(filtro, atualizacao)

            # Opção de selecionar um produto para editar
            print("\nProdutos do vendedor:")
            for j, produto in enumerate(produtos, start=1):
                print(f"{j}. {produto['nome_produto']}  Preço: {produto['preco']}  Qtd: {produto['quantidade_disponivel']}")

            try:
                indice_produto_selecionado = int(input("Digite o número correspondente ao produto que deseja editar: "))
            except ValueError:
                print("Entrada inválida. Digite um número válido.")
                return

            # Verificar se o índice está dentro dos limites
            if 1 <= indice_produto_selecionado <= len(produtos):
                # Obter o produto correspondente ao índice selecionado
                produto_selecionado = produtos[indice_produto_selecionado - 1]

                # Solicitar a atualização do preço e da quantidade disponível
                novo_preco = input(f"Digite o novo preço para o produto '{produto_selecionado['nome_produto']}' (ou pressione Enter para manter): ")
                nova_quantidade = input(f"Digite a nova quantidade disponível para o produto '{produto_selecionado['nome_produto']}' (ou pressione Enter para manter): ")

                # Verificar se o usuário deseja manter os valores existentes
                if not novo_preco:
                    novo_preco = produto_selecionado['preco']
                if not nova_quantidade:
                    nova_quantidade = produto_selecionado['quantidade_disponivel']

                # Atualizar o produto no Redis
                produtos[indice_produto_selecionado - 1]['preco'] = novo_preco
                produtos[indice_produto_selecionado - 1]['quantidade_disponivel'] = nova_quantidade

                # Atualizar a string JSON de produtos no Redis
                cliente_redis.hset(nova_chave_redis, 'produtos', json.dumps(produtos))

                # Atualizar o produto no MongoDB
                filtro_produto = {
                    'nome_vendedor': novo_nome_vendedor,
                    'produtos': {'$elemMatch': {'nome_produto': produto_selecionado['nome_produto']}}
                }
                atualizacao_produto = {
                    '$set': {
                        'produtos.$.preco': novo_preco,
                        'produtos.$.quantidade_disponivel': nova_quantidade
                    }
                }
                colecao_vendedor_mongo.update_one(filtro_produto, atualizacao_produto)

                print(f"Vendedor '{novo_nome_vendedor}', produto '{produto_selecionado['nome_produto']}' atualizado com sucesso.")
            else:
                print("Índice inválido. Selecione um número válido.")
        else:
            print("Índice inválido. Selecione um número válido.")

    # Fechar as conexões
    cliente_redis.close()
    cliente_mongo.close()

def deletar_vendedor_redis(redis_host, redis_port, redis_password):
    # Conectar ao Redis
    cliente_redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    # Obter todas as chaves no Redis (cada chave representa um vendedor)
    chaves_vendedores = cliente_redis.keys("Vendedor:*")

    if not chaves_vendedores:
        print("Nenhum vendedor cadastrado.")
    else:
        # Mostrar os nomes dos vendedores e obter a seleção do usuário
        print("Selecione um vendedor para deletar:")
        for i, chave_vendedor in enumerate(chaves_vendedores, start=1):
            nome_vendedor = cliente_redis.hget(chave_vendedor, 'nome_vendedor')
            print(f"{i}. {nome_vendedor}")

        # Pedir ao usuário para selecionar um vendedor pelo índice
        try:
            indice_selecionado = int(input("Digite o número correspondente ao vendedor que deseja deletar: "))
        except ValueError:
            print("Entrada inválida. Digite um número válido.")
            return

        # Verificar se o índice está dentro dos limites
        if 1 <= indice_selecionado <= len(chaves_vendedores):
            # Obter a chave correspondente ao índice selecionado
            chave_vendedor_selecionado = chaves_vendedores[indice_selecionado - 1]

            # Obter o nome do vendedor
            nome_vendedor_selecionado = cliente_redis.hget(chave_vendedor_selecionado, 'nome_vendedor')

            # Deletar o vendedor no Redis
            cliente_redis.delete(chave_vendedor_selecionado)

            print(f"Vendedor '{nome_vendedor_selecionado}' deletado com sucesso do Redis.")
        else:
            print("Índice inválido. Selecione um número válido.")

    # Fechar a conexão
    cliente_redis.close()