# EP1 - Pokémon Scraper

Este projeto coleta e processa dados de Pokémon de forma automatizada.

## Como rodar o projeto

Siga os passos abaixo para configurar e executar o scraper:

1. Clone este repositório:

   ```bash
   git clone https://github.com/KaykeAhrens/EP1-Pokemon-Scrapy.git
   ```

2. Crie um ambiente virtual:

   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual:

   - **Windows (PowerShell):**

     > Se aparecer erro de permissão, rode este comando **antes** (como administrador ou no próprio PowerShell do usuário):

     ```bash
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
     ```

     Depois ative o ambiente:

     ```bash
     venv\Scripts\Activate.ps1
     ```

   - **Windows (CMD):**

     ```bash
     venv\Scripts\activate.bat
     ```

   - **Linux/MacOS:**
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

5. Acesse a pasta principal:

   ```bash
   cd pokemon_scraper
   ```

6. Execute o scraper:
   ```bash
   python run_scrapers.py
   ```

---

## Observações

- Certifique-se de estar com o **Python 3.10+** instalado.
- O comando `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` só precisa ser feito uma vez no Windows.
