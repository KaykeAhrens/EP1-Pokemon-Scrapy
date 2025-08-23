import scrapy

class PokemonItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    nome = scrapy.Field()
    evolucoes = scrapy.Field()  
    tamanho_cm = scrapy.Field()
    peso_kg = scrapy.Field()
    tipos = scrapy.Field()  
    habilidades = scrapy.Field()  
    efetividade_tipos = scrapy.Field()  

class EvolucaoItem(scrapy.Item):
    id = scrapy.Field()
    nome = scrapy.Field()
    url = scrapy.Field()
    level = scrapy.Field()
    item = scrapy.Field()

class HabilidadeItem(scrapy.Item):
    url = scrapy.Field()
    nome = scrapy.Field()
    descricao = scrapy.Field()