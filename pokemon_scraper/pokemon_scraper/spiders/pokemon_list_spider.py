import scrapy
from pokemon_scraper.items import PokemonItem
import re

class PokemonListSpider(scrapy.Spider):
    name = 'pokemon_list'
    allowed_domains = ['pokemondb.net']
    start_urls = ['https://pokemondb.net/pokedex/all'] 
    
    def parse(self, response):
        # extrai todos os pokémons da tabela
        pokemon_rows = response.css('#pokedex > tbody > tr')
        
        for row in pokemon_rows:
            # extrai dados básicos da lista
            id = row.css('span.infocard-cell-data::text').get()
            nome_link = row.css('td.cell-name a.ent-name::attr(href)').get()
            nome = row.css('td.cell-name a.ent-name::text').get()
            tipos = row.css('td.cell-icon a.type-icon::text').getall()
            
            if id and nome_link and nome:
                # cria a URL completa
                pokemon_url = response.urljoin(nome_link)
                
                # cria o item básico
                pokemon_item = PokemonItem()
                pokemon_item['id'] = int(id.strip('#'))
                pokemon_item['url'] = pokemon_url
                pokemon_item['nome'] = nome.strip()
                pokemon_item['tipos'] = [tipo.strip() for tipo in tipos]
                
                # faz uma requisição para página de detalhes
                yield scrapy.Request(
                    url=pokemon_url,
                    callback=self.parse_pokemon_detail,
                    meta={'pokemon_item': pokemon_item}
                )
    
    def parse_pokemon_detail(self, response):
        pokemon_item = response.meta['pokemon_item']
        
        # extrai dados detalhados
        self.extract_physical_data(response, pokemon_item)
        self.extract_abilities(response, pokemon_item)
        self.extract_evolutions(response, pokemon_item)
        self.extract_type_effectiveness(response, pokemon_item)
        
        yield pokemon_item
    
    def extract_physical_data(self, response, pokemon_item):
        # extrai dados físicos como tamanho e peso
        # procura por Height e Weight nas tabelas
        vitals_table = response.css('table.vitals-table')
        
        for row in vitals_table.css('tr'):
            header = row.css('th::text').get()
            if header:
                header = header.strip()
                value = row.css('td::text').get()
                
                if 'Height' in header and value:
                    # extrai apenas cm (converter de feet/inches se necessário)
                    match = re.search(r'(\d+\.?\d*)\s*m', value)
                    if match:
                        pokemon_item['tamanho_cm'] = int(float(match.group(1)) * 100)
                
                elif 'Weight' in header and value:
                    # extrai apenas kg
                    match = re.search(r'(\d+\.?\d*)\s*kg', value)
                    if match:
                        pokemon_item['peso_kg'] = float(match.group(1))
    
    def extract_abilities(self, response, pokemon_item):
        # extrai habilidades
        abilities = []
        ability_links = response.css('table.vitals-table tr:contains("Abilities") td a')
        
        for link in ability_links:
            ability_name = link.css('::text').get()
            ability_url = link.css('::attr(href)').get()
            
            if ability_name and ability_url:
                abilities.append({
                    'nome': ability_name.strip(),
                    'url': response.urljoin(ability_url),
                    'descricao': None  # será preenchido por outro spider
                })
        
        pokemon_item['habilidades'] = abilities
    
    def extract_evolutions(self, response, pokemon_item):
        # extrai cadeia de evolução
        evolutions = []
        
        # procura pela seção de evolução
        evolution_chart = response.css('.infocard-list-evo')
        
        if evolution_chart:
            evolution_links = evolution_chart.css('.ent-name')
            
            # tratamento especial para Eevee
            if pokemon_item['nome'].lower() == 'eevee':
                evolutions = self.extract_eevee_evolutions(response, pokemon_item)
            else:
                # tratamento normal para outros pokémons
                for link in evolution_links:
                    evo_name = link.css('::text').get()
                    evo_url = link.css('::attr(href)').get()
                    
                    if evo_name and evo_url and evo_name != pokemon_item['nome']:
                        # extrai número do pokémon da URL
                        evo_number = self.extract_pokemon_number_from_url(evo_url)
                        
                        # procura por level ou item de evolução
                        evo_container = link.xpath('./ancestor::div[contains(@class, "infocard")]')
                        level_text = evo_container.css('.infocard-lg-data small::text').get()
                        
                        level = None
                        item = None
                        
                        if level_text:
                            level_match = re.search(r'Level (\d+)', level_text)
                            if level_match:
                                level = int(level_match.group(1))
                            
                            # verifica se há item
                            if 'Stone' in level_text or 'Item' in level_text:
                                item = level_text.strip()
                        
                        evolutions.append({
                            'id': evo_number,
                            'nome': evo_name.strip(),
                            'url': response.urljoin(evo_url),
                            'level': level,
                            'item': item
                        })
        
        pokemon_item['evolucoes'] = evolutions

    def extract_eevee_evolutions(self, response, pokemon_item):
        # extrai evoluções do Eevee com condições especiais
        eevee_evolutions = []
        
        # procura todas as evoluções do Eevee na página
        evolution_chart = response.css('.infocard-list-evo')
        
        if evolution_chart:
            # busca todos os cards de evolução
            evo_cards = evolution_chart.css('.infocard')
            
            for card in evo_cards:
                evo_link = card.css('.ent-name')
                if evo_link:
                    evo_name = evo_link.css('::text').get()
                    evo_url = evo_link.css('::attr(href)').get()
                    
                    if evo_name and evo_url and evo_name.lower() != 'eevee':
                        evo_number = self.extract_pokemon_number_from_url(evo_url)
                        
                        # procurar condições específicas de evolução
                        condition_text = card.css('.infocard-lg-data small::text').get()
                        
                        level = None
                        item = None
                        condition = None
                        
                        if condition_text:
                            condition = condition_text.strip()
                            
                            # verificar diferentes tipos de condição
                            level_match = re.search(r'Level (\d+)', condition)
                            if level_match:
                                level = int(level_match.group(1))
                            
                            # stones e itens específicos
                            if any(stone in condition for stone in ['Stone', 'stone']):
                                item = condition
                            
                            # condições especiais (felicidade, local, etc.)
                            elif any(word in condition.lower() for word in ['happiness', 'friendship', 'location', 'time']):
                                item = condition
                        
                        eevee_evolutions.append({
                            'id': evo_number,
                            'nome': evo_name.strip(),
                            'url': response.urljoin(evo_url),
                            'level': level,
                            'item': item,
                            'condition': condition  # campo extra para Eevee
                        })
        
        # se não encontrou evoluções pelo método normal, tentar método alternativo
        if not eevee_evolutions:
            eevee_evolutions = self.extract_eevee_evolutions_alternative(response)
        
        return eevee_evolutions

    def extract_eevee_evolutions_alternative(self, response):
        # Método alternativo para extrair evoluções do Eevee
        # Lista conhecida das evoluções do Eevee
        known_eevee_evolutions = [
            'Vaporeon', 'Jolteon', 'Flareon', 'Espeon', 'Umbreon', 
            'Leafeon', 'Glaceon', 'Sylveon'
        ]
        
        eevee_evolutions = []
        
        # procura links para essas evoluções na página
        for evo_name in known_eevee_evolutions:
            # busca link específico
            evo_link = response.css(f'a[href*="{evo_name.lower()}"]').first()
            
            if evo_link:
                evo_url = evo_link.css('::attr(href)').get()
                if evo_url:
                    evo_number = self.extract_pokemon_number_from_url(evo_url)
                    
                    eevee_evolutions.append({
                        'id': evo_number,
                        'nome': evo_name,
                        'url': response.urljoin(evo_url),
                        'level': None,
                        'item': 'Condição especial',  # genérico para Eevee
                        'condition': 'Evolução do Eevee'
                    })
        
        return eevee_evolutions
    
    def extract_type_effectiveness(self, response, pokemon_item):
        effectiveness = {}

        type_tables = response.css('table.type-table-pokedex')

        for table in type_tables:
            headers = table.css('tr th a::attr(title)').getall()
            values = table.css('tr + tr td')

            for i, header in enumerate(headers):
                if i < len(values):
                    cell = values[i]
                    text_value = cell.css('::text').get(default="").strip()
                    class_value = cell.attrib.get("class", "")

                    # Converter diretamente
                    if text_value == "2":
                        numeric_value = 2.0
                    elif text_value in ["½", "1/2"]:
                        numeric_value = 0.5
                    elif text_value in ["¼", "1/4"]:
                        numeric_value = 0.25
                    elif text_value == "0":
                        numeric_value = 0.0
                    elif text_value == "":
                        if "type-fx-200" in class_value:
                            numeric_value = 2.0
                        elif "type-fx-50" in class_value:
                            numeric_value = 0.5
                        elif "type-fx-25" in class_value:
                            numeric_value = 0.25
                        elif "type-fx-0" in class_value:
                            numeric_value = 0.0
                        else:
                            numeric_value = 1.0
                    else:
                        numeric_value = 1.0

                    effectiveness[header] = numeric_value

        # Salva todos os tipos, sem filtrar
        pokemon_item["efetividade_tipos"] = effectiveness


    def extract_pokemon_number_from_url(self, url):
        # extrai o número do pokémon da URL
        # URLs são como: /pokedex/bulbasaur ou /pokedex/001
        match = re.search(r'/pokedex/(\d+)', url)
        if match:
            return int(match.group(1))
        return None