import pymongo
from pymongo import MongoClient
import json
from typing import List, Dict, Any
import os

class MongoHandler:
    def __init__(self, connection_string: str = None, db_name: str = "pokemon_db"):
        # Usar MongoDB Atlas se fornecido, senão localhost
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = "mongodb+srv://senac:senac@cluster0.pms1duk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        self.db_name = db_name
        self.client = None
        self.db = None
        
    def connect(self):
        """Conecta ao MongoDB (Cloud ou Local)"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            
            # Testar conexão
            self.client.admin.command('ping')
            print(f"Conectado ao MongoDB: {self.db_name}")
            return True
            
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do MongoDB"""
        if self.client:
            self.client.close()
            print("Desconectado do MongoDB")
    
    def insert_pokemon_data(self, json_file: str):
        """Insere dados de pokémons no MongoDB"""
        if self.db is None:
            print("Não conectado ao banco")
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                pokemon_data = json.load(f)
            
            # Limpar coleção existente
            self.db.pokemons.drop()
            print("Coleção anterior removida")
            
            # Inserir dados
            if isinstance(pokemon_data, list):
                result = self.db.pokemons.insert_many(pokemon_data)
                print(f"Inseridos {len(result.inserted_ids)} pokémons no MongoDB")
                
                # Criar índices para melhor performance
                self.db.pokemons.create_index("numero")
                self.db.pokemons.create_index("nome")
                self.db.pokemons.create_index("tipos")
                print("🔍 Índices criados")
                
                return True
            else:
                print("Formato de dados inválido")
                return False
                
        except Exception as e:
            print(f"Erro ao inserir dados: {e}")
            return False
    
    def get_collection_stats(self):
        """Retorna estatísticas da coleção"""
        if self.db is None:
            return None
        
        try:
            stats = {
                'total_documents': self.db.pokemons.count_documents({}),
                'database_name': self.db_name,
                'collection_name': 'pokemons'
            }
            
            return stats
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return None

def setup_mongodb():
    """Configura e popula o MongoDB Cloud"""
    # Usando a string de conexão fornecida
    mongo_url = "mongodb+srv://senac:senac@cluster0.pms1duk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    handler = MongoHandler(connection_string=mongo_url)
    
    if not handler.connect():
        return False
    
    # Inserir dados limpos
    if os.path.exists('data/pokemon_clean.json'):
        success = handler.insert_pokemon_data('data/pokemon_clean.json')
        
        if success:
            stats = handler.get_collection_stats()
            print(f"Total de documentos: {stats['total_documents']}")
            print(f"Database: {stats['database_name']}")
            print(f"Collection: {stats['collection_name']}")
        
    else:
        print("Arquivo pokemon_clean.json não encontrado")
        print("Execute primeiro: python data_processing/data_cleaner.py")
        
    handler.disconnect()
    return success

if __name__ == "__main__":
    setup_mongodb()