# Defina a URI do seu banco de dados MongoDB aqui
from produto import atualizar_produto_mongodb_e_redis, deletar_produto_redis, exportar_produtos_mongodb_para_redis, imprimir_produtos_redis
from vendedor import exportar_vendedores_mongodb_para_redis, imprimir_vendedores_redis 

# Configuração do MongoDB
MONGO_URI = ""

# Configuração do Redis
REDIS_HOST = ''
REDIS_PORT = 18140
REDIS_PASSWORD = ''

key = 0
sub = 0

while (key != 'S' and key != 's'):
    print("|---------------------Bem Vindo---------------------------------|")
    print("1-CRUD Produto")
    print("2-CRUD Vendedor")
    print("3-Login")
    print("|---------------------------------------------------------------|")
    key = input("Digite a opção desejada? (S para sair) ")
    print ("")
    
    if (key == '1'):
        print("|-------------------Menu de Produto-----------------------------|")
        print("1. Importação Produtos do MongoDB para o Redis")
        print("2. Listagem de Produtos")
        print("3. Editar Produto")
        print("4. Deletar Produtos")
        print("|---------------------------------------------------------------|")
        sub = input("Digite a opção desejada? (V para voltar) ")
        print ("")

        if (sub == "1"):
            exportar_produtos_mongodb_para_redis(MONGO_URI,REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
        elif (sub == "2"):
            imprimir_produtos_redis(REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
        elif (sub == "3"):
            atualizar_produto_mongodb_e_redis(MONGO_URI,REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
        elif (sub == "4"):
            deletar_produto_redis(REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)

    elif (key == '2'):
        print("|-------------------Menu de Vendedor-----------------------------|")
        print("1. Importação Vendedores do MongoDB para o Redis")
        print("2. Listagem de Vendedores")
        print("3. Editar Vendedor")
        print("4. Deletar Vendedor")
        print("|---------------------------------------------------------------|")
        sub = input("Digite a opção desejada? (V para voltar) ")
        print ("")

        if (sub == '1'):
            exportar_vendedores_mongodb_para_redis(MONGO_URI,REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
        elif (sub == '2'):
            imprimir_vendedores_redis(REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
  
print("Vlw Flw...")