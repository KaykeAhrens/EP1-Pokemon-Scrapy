import subprocess
import time
import os
from data_processing.data_cleaner import clean_all_data
from data_processing.mongo_handler import setup_mongodb
from queries.pokemon_queries import executar_consultas

def run_command(command, description):
   # execução de um comando shell
    print(f"{description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{description} - Concluído com sucesso!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print(f"{description} - Erro!")
            if result.stderr:
                print("Erro:")
                print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Erro ao executar {description}: {e}")
        return False

def main():
    # execução do pipeline completo
    print("INICIANDO SCRAPING DE POKÉMONS")
    
    # cria os diretórios necessários
    os.makedirs('data', exist_ok=True)
    
    # scraping da lista de pokémons
    success = run_command(
        "scrapy crawl pokemon_list",
        "Extraindo lista de pokémons e dados detalhados"
    )
    
    if not success:
        print("Falha no scraping de pokémons. Abortando...")
        return
    
    time.sleep(2)
    
    # scraping das habilidades
    success = run_command(
        "scrapy crawl abilities",
        "Extraindo dados das habilidades"
    )
    
    if not success:
        print("Falha no scraping de habilidades, mas continuando...")
    
    time.sleep(2)
    
    # limpeza e tratamento de dados
    print("Limpando e tratando dados com Pandas...")
    try:
        clean_all_data()
        print("Dados limpos com sucesso!")
    except Exception as e:
        print(f"Erro na limpeza de dados: {e}")
        return
    
    time.sleep(1)
    
    # inserir no MongoDB
    print("Inserindo dados no MongoDB...")
    try:
        if setup_mongodb():
            print("Dados inseridos no MongoDB com sucesso!")
        else:
            print("Falha ao inserir dados no MongoDB")
            return
    except Exception as e:
        print(f"Erro no MongoDB: {e}")
        return
    
    time.sleep(1)
    
    # executar queries
    print("Executando consultas...")
    try:
        executar_consultas()
        print("Consultas executadas com sucesso!")
    except Exception as e:
        print(f"Erro nas consultas: {e}")
    
    print("\nPROCESSO CONCLUÍDO!")
    print("Arquivos gerados:")
    print("  - data/pokemon_list_data.json - Dados brutos dos pokémons")
    print("  - data/abilities_data.json - Dados brutos das habilidades")
    print("  - data/pokemon_clean.json - Dados limpos e tratados")
    print("  - MongoDB collection 'pokemons' - Dados no banco")

if __name__ == "__main__":
    main()