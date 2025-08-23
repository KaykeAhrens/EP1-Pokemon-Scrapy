import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any

class PokemonQueries:
    def __init__(self, connection_string: str = None, db_name: str = "pokemon_db"):
        # usa a string de conexão do MongoDB
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = "mongodb+srv://senac:senac@cluster0.pms1duk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[db_name]
            
            # testa a conexão
            self.client.admin.command('ping')
            print(f"Conectado para consultas: {db_name}")
        except Exception as e:
            print(f"Erro na conexão: {e}")
            self.client = None
            self.db = None
    
    def close(self):
        # fecha a conexão com o MongoDB
        if self.client:
            self.client.close()
            print("Conexão fechada")
    
    def pokemons_multiplos_tipos(self):
        # qnts pokémons têm 2 ou mais tipos?
        if self.db is None:
            print("Sem conexão com banco")
            return 0
            
        try:
            # agrega para contar pokémons com 2 ou mais tipos
            pipeline = [
                {
                    "$project": {
                        "nome": 1,
                        "tipos": 1,
                        "num_tipos": {"$size": "$tipos"}
                    }
                },
                {
                    "$match": {
                        "num_tipos": {"$gte": 2}
                    }
                },
                {
                    "$count": "total"
                }
            ]
            
            result = list(self.db.pokemons.aggregate(pipeline))
            
            if result:
                total = result[0]['total']
                print(f"Pokémons com 2 ou mais tipos: {total}")
                
                # mostra alguns exemplos
                exemplos = list(self.db.pokemons.find(
                    {"$expr": {"$gte": [{"$size": "$tipos"}, 2]}},
                    {"nome": 1, "tipos": 1, "_id": 0}
                ).limit(5))
                
                print("   Exemplos:")
                for ex in exemplos:
                    tipos_str = ", ".join(ex['tipos'])
                    print(f"   - {ex['nome']}: {tipos_str}")
                
                return total
            else:
                print("Nenhum pokémon encontrado com 2+ tipos")
                return 0
                
        except Exception as e:
            print(f"Erro na consulta: {e}")
            return 0
    
    def agua_evolucoes_level_30_plus(self):
        # quais pokémons do tipo água evoluem após level 30?
        if self.db is None:
            print("Sem conexão com banco")
            return []
            
        try:
            # busca pokémons do tipo água
            pokemons_agua = list(self.db.pokemons.find({
                "$or": [
                    {"tipos": {"$in": ["Water", "Água", "water", "água"]}},
                    {"tipos": {"$regex": "(?i)water|água"}}
                ]
            }))
            
            print(f"Encontrados {len(pokemons_agua)} pokémons do tipo água")
            
            resultado = []
            
            for pokemon in pokemons_agua:
                # verifica se este pokémon é evolução de alguém
                pokemon_name = pokemon['nome']
                
                # busca pokémons que evoluem para este com level > 30
                evolving_pokemon = list(self.db.pokemons.find({
                    "evolucoes": {
                        "$elemMatch": {
                            "nome": pokemon_name,
                            "level": {"$gt": 30}
                        }
                    }
                }))
                
                for evo_pokemon in evolving_pokemon:
                    # encontra a evolução específica
                    for evolucao in evo_pokemon.get('evolucoes', []):
                        if (evolucao.get('nome') == pokemon_name and 
                            evolucao.get('level', 0) > 30):
                            resultado.append({
                                'pokemon_agua': pokemon_name,
                                'evolui_de': evo_pokemon['nome'],
                                'level_evolucao': evolucao['level'],
                                'numero': pokemon.get('numero'),
                                'tipos': pokemon.get('tipos', [])
                            })
                            break
            
            print(f"Pokémons do tipo água que evoluem após level 30:")
            
            if resultado:
                for item in resultado:
                    tipos_str = ", ".join(item['tipos'])
                    print(f"  - {item['pokemon_agua']} (#{item['numero']}) - {tipos_str}")
                    print(f"    Evolui de: {item['evolui_de']} (Level {item['level_evolucao']})")
            else:
                print("Nenhum pokémon encontrado com esses critérios")
                print("\nDiagnóstico - Alguns pokémons de água encontrados:")
                for pokemon in pokemons_agua[:5]:
                    print(f"  - {pokemon['nome']}: {pokemon.get('tipos', [])}")
            
            return resultado
            
        except Exception as e:
            print(f"Erro na consulta: {e}")
            return []
    
    def estatisticas_gerais(self):
        # estatísticas gerais dos pokémons
        if self.db is None:
            print("Sem conexão com banco")
            return None
            
        try:
            # total de pokémons
            total_pokemons = self.db.pokemons.count_documents({})
            
            # pokémons por tipo
            pipeline_tipos = [
                {"$unwind": "$tipos"},
                {"$group": {"_id": "$tipos", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            tipos_stats = list(self.db.pokemons.aggregate(pipeline_tipos))
            
            # pokémons com mais habilidades
            pipeline_habilidades = [
                {
                    "$project": {
                        "nome": 1,
                        "num_habilidades": {"$size": {"$ifNull": ["$habilidades", []]}}
                    }
                },
                {"$sort": {"num_habilidades": -1}},
                {"$limit": 5}
            ]
            top_habilidades = list(self.db.pokemons.aggregate(pipeline_habilidades))
            
            # pokémons mais pesados
            top_pesados = list(self.db.pokemons.find(
                {"peso_kg": {"$ne": None}}, 
                {"nome": 1, "peso_kg": 1, "_id": 0}
            ).sort("peso_kg", -1).limit(5))
            
            print("ESTATÍSTICAS GERAIS")
            print(f"Total de Pokémons: {total_pokemons}")
            
            print(f"\nTop 5 tipos mais comuns:")
            for tipo in tipos_stats[:5]:
                print(f"  - {tipo['_id']}: {tipo['count']} pokémons")
            
            print(f"\nTop 5 pokémons com mais habilidades:")
            for pokemon in top_habilidades:
                print(f"  - {pokemon['nome']}: {pokemon['num_habilidades']} habilidades")
            
            print(f"\nTop 5 pokémons mais pesados:")
            for pokemon in top_pesados:
                peso = pokemon.get('peso_kg', 0)
                print(f"  - {pokemon['nome']}: {peso} kg")
            
            return {
                'total_pokemons': total_pokemons,
                'tipos_stats': tipos_stats,
                'top_habilidades': top_habilidades,
                'top_pesados': top_pesados
            }
            
        except Exception as e:
            print(f"Erro nas estatísticas: {e}")
            return None

def executar_consultas():
    # pra executar as consultas todas de uma vez
    mongo_url = "mongodb+srv://senac:senac@cluster0.pms1duk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    queries = PokemonQueries(connection_string=mongo_url)
    
    if queries.db is None:
        print("Não foi possível conectar ao MongoDB")
        print("Verifique se os dados foram inseridos com: python data_processing/mongo_handler.py")
        return
    
    print("EXECUTANDO QUERIES NO MONGODB\n")
    
    # query 1: pokémons com 2+ tipos
    queries.pokemons_multiplos_tipos()
    
    # query 2: pokémons água que evoluem após level 30
    queries.agua_evolucoes_level_30_plus()
    queries.estatisticas_gerais()
    
    queries.close()

if __name__ == "__main__":
    executar_consultas()