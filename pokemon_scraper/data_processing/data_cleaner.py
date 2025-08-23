import pandas as pd
import json
import numpy as np
from typing import List, Dict, Any

class PokemonDataCleaner:
    def __init__(self):
        self.pokemon_df = None
        self.abilities_df = None
    
    def load_data(self, pokemon_file: str, abilities_file: str):
        # carrega os dados do json
        try:
            with open(pokemon_file, 'r', encoding='utf-8') as f:
                pokemon_data = json.load(f)
            self.pokemon_df = pd.DataFrame(pokemon_data)
            
            with open(abilities_file, 'r', encoding='utf-8') as f:
                abilities_data = json.load(f)
            self.abilities_df = pd.DataFrame(abilities_data)
            
            print(f"Carregados {len(self.pokemon_df)} pokémons e {len(self.abilities_df)} habilidades")
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
        
        return True
    
    def clean_pokemon_data(self):
        # limpa e trata os dados
        if self.pokemon_df is None:
            print("Dados não carregados")
            return
        
        print("Iniciando limpeza dos dados de pokémons...")
        
        # remove duplicados baseado no id
        initial_count = len(self.pokemon_df)
        self.pokemon_df = self.pokemon_df.drop_duplicates(subset=['id'])
        print(f"Removidos {initial_count - len(self.pokemon_df)} pokémons duplicados")
        
        # limpa dados nulos ou inválidos
        self.pokemon_df = self.pokemon_df.dropna(subset=['id', 'nome', 'url'])
        
        # valida e limpa tamanho e peso
        self.pokemon_df['tamanho_cm'] = pd.to_numeric(self.pokemon_df['tamanho_cm'], errors='coerce')
        self.pokemon_df['peso_kg'] = pd.to_numeric(self.pokemon_df['peso_kg'], errors='coerce')
        
        # remove pokémons sem dados físicos válidos
        before_physical = len(self.pokemon_df)
        self.pokemon_df = self.pokemon_df.dropna(subset=['tamanho_cm', 'peso_kg'])
        print(f"Removidos {before_physical - len(self.pokemon_df)} pokémons sem dados físicos válidos")
        
        # limpa tipos
        self.pokemon_df['tipos'] = self.pokemon_df['tipos'].apply(self._clean_types)
        
        # limpa evoluções
        self.pokemon_df['evolucoes'] = self.pokemon_df['evolucoes'].apply(self._clean_evolutions)
        
        # limpa habilidades
        self.pokemon_df['habilidades'] = self.pokemon_df['habilidades'].apply(self._clean_abilities)
        
        print(f"Limpeza concluída. {len(self.pokemon_df)} pokémons restantes")
    
    def clean_abilities_data(self):
        # limpa e trata os dados de habilidades
        if self.abilities_df is None:
            print("Dados de habilidades não carregados")
            return
        
        print("Iniciando limpeza dos dados de habilidades...")
        
        # remove duplicados
        initial_count = len(self.abilities_df)
        self.abilities_df = self.abilities_df.drop_duplicates(subset=['url'])
        print(f"Removidas {initial_count - len(self.abilities_df)} habilidades duplicadas")
        
        # remove habilidades sem nome ou descrição
        self.abilities_df = self.abilities_df.dropna(subset=['nome'])
        
        # limpa descrições vazias
        self.abilities_df['descricao'] = self.abilities_df['descricao'].fillna('Descrição não disponível')
        
        print(f"Limpeza de habilidades concluída. {len(self.abilities_df)} habilidades restantes")
    
    def merge_abilities_data(self):
        # justa as habilidades dos pokémons com as descrições
        if self.pokemon_df is None or self.abilities_df is None:
            print("Dados não carregados completamente")
            return
        
        abilities_dict = self.abilities_df.set_index('url').to_dict('index')
        
        # atualiza as habilidades nos pokémons
        def update_pokemon_abilities(abilities_list):
            if not isinstance(abilities_list, list):
                return []
            
            updated_abilities = []
            for ability in abilities_list:
                if isinstance(ability, dict) and 'url' in ability:
                    url = ability['url']
                    if url in abilities_dict:
                        ability['descricao'] = abilities_dict[url].get('descricao', 'Descrição não disponível')
                    updated_abilities.append(ability)
            
            return updated_abilities
        
        self.pokemon_df['habilidades'] = self.pokemon_df['habilidades'].apply(update_pokemon_abilities)
        print("Dados de habilidades mesclados com sucesso")
    
    def _clean_types(self, types_list):
        
        if not isinstance(types_list, list):
            return []
        
        # remove tipos vazios ou inválidos
        clean_types = [t.strip() for t in types_list if t and isinstance(t, str)]
        return clean_types
    
    def _clean_evolutions(self, evolutions_list):
        # limpa a lista de evoluções
        if not isinstance(evolutions_list, list):
            return []
        
        clean_evolutions = []
        for evo in evolutions_list:
            if isinstance(evo, dict) and 'nome' in evo and 'url' in evo:
                if 'level' in evo and evo['level']:
                    try:
                        evo['level'] = int(evo['level'])
                    except:
                        evo['level'] = None
                
                clean_evolutions.append(evo)
        
        return clean_evolutions
    
    def _clean_abilities(self, abilities_list):
        # limpa a lista de habilidades
        if not isinstance(abilities_list, list):
            return []
        
        clean_abilities = []
        for ability in abilities_list:
            if isinstance(ability, dict) and 'nome' in ability and 'url' in ability:
                clean_abilities.append(ability)
        
        return clean_abilities
    
    def save_cleaned_data(self, output_file: str):
        # salva os dados limpos em um arquivo json
        if self.pokemon_df is None:
            print("Dados não disponíveis para salvar")
            return
        
        # converte o df pra uma lista de dicionários
        clean_data = self.pokemon_df.to_dict('records')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Dados limpos salvos em {output_file}")
    
    def get_data_summary(self):
        if self.pokemon_df is None:
            return "Dados não carregados"
        
        summary = {
            'total_pokemons': len(self.pokemon_df),
            'pokemons_com_evolucoes': len(self.pokemon_df[self.pokemon_df['evolucoes'].apply(len) > 0]),
            'tipos_unicos': set(),
            'total_habilidades_unicas': 0
        }
        
        # conta tipos únicos
        for types_list in self.pokemon_df['tipos']:
            if isinstance(types_list, list):
                summary['tipos_unicos'].update(types_list)
        
        summary['tipos_unicos'] = list(summary['tipos_unicos'])
        
        # conta habilidades únicas
        unique_abilities = set()
        for abilities_list in self.pokemon_df['habilidades']:
            if isinstance(abilities_list, list):
                for ability in abilities_list:
                    if isinstance(ability, dict) and 'nome' in ability:
                        unique_abilities.add(ability['nome'])
        
        summary['total_habilidades_unicas'] = len(unique_abilities)
        
        return summary

# função principal de limpeza (só pra chamar todas de uma vez)
def clean_all_data():
    cleaner = PokemonDataCleaner()
    
    # carregar dados
    if not cleaner.load_data('data/pokemon_list_data.json', 'data/abilities_data.json'):
        return
    
    # limpa dados
    cleaner.clean_pokemon_data()
    cleaner.clean_abilities_data()
    
    # junta os dados das habilidades
    cleaner.merge_abilities_data()
    
    # salva os dados limpos
    cleaner.save_cleaned_data('data/pokemon_clean.json')
    
    # mostrar um resumo
    summary = cleaner.get_data_summary()
    print("\nRESUMO DOS DADOS LIMPOS")
    print(f"Total de Pokémons: {summary['total_pokemons']}")
    print(f"Pokémons com evoluções: {summary['pokemons_com_evolucoes']}")
    print(f"Tipos únicos: {len(summary['tipos_unicos'])}")
    print(f"Habilidades únicas: {summary['total_habilidades_unicas']}")

if __name__ == "__main__":
    clean_all_data()