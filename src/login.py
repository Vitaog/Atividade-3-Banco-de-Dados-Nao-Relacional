from pymongo import MongoClient
import redis
import time

def exportar_usuarios_mongodb_para_redis(mongo_uri, redis_host, redis_port, redis_password):
    # Conectar ao MongoDB
    cliente_mongo = MongoClient(mongo_uri)
    banco_de_dados_mongo = cliente_mongo.get_database("MercadoLivreRedis")
    colecao_usuario_mongo = banco_de_dados_mongo.get_collection("Usuario")

    # Conectar ao Redis
    cliente_redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    # Obter todos os documentos da coleção no MongoDB
    documentos_mongo = colecao_usuario_mongo.find()

    # Iterar sobre os documentos e armazenar no Redis usando o CPF do usuário como chave
    for documento in documentos_mongo:
        login_usuario = documento['login']
        id_usuario = str(documento['_id'])
        nome_usuario = documento['nome']
        sobrenome_usuario = documento['sobrenome']
        cpf_usuario = documento['cpf']
        senha_usuario = documento['senha']

        # Armazenar no Redis usando o CPF do usuário como chave
        chave_redis = f"Usuario:CPF:{cpf_usuario}"
        cliente_redis.hmset(chave_redis, {'_id': id_usuario, 'nome': nome_usuario, 'sobrenome': sobrenome_usuario, 'cpf': cpf_usuario, 'login': login_usuario ,'senha': senha_usuario})

    # Fechar as conexões
    cliente_mongo.close()
    cliente_redis.close()
    print("Exportação de usuários concluída com sucesso")

def listar_e_autenticar_usuarios(redis_host, redis_port, redis_password):
    # Conectar ao Redis
    cliente_redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    # Obter todas as chaves no Redis (cada chave representa um usuário)
    chaves_usuarios = cliente_redis.keys("Usuario:CPF:*")

    # Verificar se há usuários cadastrados
    if not chaves_usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        # Imprimir os nomes dos usuários e obter a seleção do usuário
        print("Selecione um usuário:")
        for i, chave_usuario in enumerate(chaves_usuarios, start=1):
            dados_usuario = cliente_redis.hgetall(chave_usuario)
            print(f"{i}. Nome: {dados_usuario['nome']} {dados_usuario['sobrenome']}, CPF: {dados_usuario['cpf']}")

        # Pedir ao usuário para selecionar um usuário pelo ID
        try:
            indice_selecionado = int(input("Digite o número correspondente ao usuário que deseja autenticar: "))
        except ValueError:
            print("Entrada inválida. Digite um número válido.")
            return

        # Verificar se o índice está dentro dos limites
        if 1 <= indice_selecionado <= len(chaves_usuarios):
            # Obter a chave correspondente ao ID selecionado
            chave_usuario_selecionado = chaves_usuarios[indice_selecionado - 1]
            dados_usuario = cliente_redis.hgetall(chave_usuario_selecionado)

            # Mostrar os dados do usuário selecionado
            print(f"\nNome do usuário: {dados_usuario['nome']} {dados_usuario['sobrenome']}")
            print(f"CPF: {dados_usuario['cpf']}")
            
            # Pedir ao usuário para digitar o login e a senha
            login_digitado = input("Digite o login: ")
            senha_digitada = input("Digite a senha: ")

            # Verificar se o login e a senha estão corretos
            if login_digitado == dados_usuario['login'] and senha_digitada == dados_usuario['senha']:
                print("Login e senha corretos. Autenticando...")

                # Simular autenticação com um expire de 10 segundos
                cliente_redis.expire(chave_usuario_selecionado, 10)
                print("Autenticação bem-sucedida. Você está autenticado.")
                
                # Verificar continuamente se a chave ainda existe no Redis
                while cliente_redis.exists(chave_usuario_selecionado):
                    print("Você está conectado.")
                    time.sleep(1)  # Aguardar 1 segundo antes de verificar novamente

                # Quando a chave não existir mais, a sessão expirou
                print("Sessão expirada. Você foi desconectado.")
            else:
                print("Login ou senha inválidos.")
        else:
            print("Índice inválido. Selecione um número válido.")

    # Fechar a conexão
    cliente_redis.close()
