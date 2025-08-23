import scrapy
from pokemon_scraper.items import HabilidadeItem
import json
import os

class AbilitySpider(scrapy.Spider):
    name = 'abilities'
    allowed_domains = ['pokemondb.net']
    
    def start_requests(self):
        # le URLs de habilidades do arquivo de pokémons
        pokemon_file = 'data/pokemon_list_data.json'
        
        if not os.path.exists(pokemon_file):
            self.logger.error(f'Arquivo {pokemon_file} não encontrado. Execute primeiro o spider pokemon_list')
            return
        
        with open(pokemon_file, 'r', encoding='utf-8') as f:
            pokemons = json.load(f)
        
        # coleta todas as URLs de habilidades únicas
        ability_urls = set()
        for pokemon in pokemons:
            if 'habilidades' in pokemon and pokemon['habilidades']:
                for ability in pokemon['habilidades']:
                    if 'url' in ability and ability['url']:
                        ability_urls.add(ability['url'])
        
        # faz requisições para cada URL de habilidade
        for url in ability_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        # extrai dados da habilidade
        ability_item = HabilidadeItem()
        
        ability_item['url'] = response.url
        
        # nome da habilidade
        name = response.css('main h1::text').get()
        if name:
            ability_item['nome'] = name.strip()
        
        # desc do efeito
        # procura pela seção de descrição
        description = response.css('.grid-row p::text').get()
        if not description:
            description = response.css('.sv-tabs-panel p::text').get()
        
        if description:
            ability_item['descricao'] = description.strip()
        
        yield ability_item