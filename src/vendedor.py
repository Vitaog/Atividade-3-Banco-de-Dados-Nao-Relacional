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