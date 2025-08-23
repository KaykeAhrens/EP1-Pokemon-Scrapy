import json
import os
from itemadapter import ItemAdapter

class JsonPipeline:
    def __init__(self):
        self.items = []
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.items.append(dict(adapter))
        return item
        
    def close_spider(self, spider):
        # cria o diretório data se não existir
        os.makedirs('data', exist_ok=True)
        
        # salva os dados em um json
        filename = f'data/{spider.name}_data.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        spider.logger.info(f'Dados salvos em {filename}')