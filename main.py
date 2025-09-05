from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd

chrome_options = Options()
chrome_options.add_argument('--start-maximized')  

driver = webdriver.Chrome(options=chrome_options)

try:
    
    driver.get('https://www.zoom.com.br')
    print("Acessando o site Zoom...")
    
    time.sleep(3)
    
    try:
        
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search'], input[type='text'], #search, .search-input"))
        )
        
        search_box.clear()
        search_box.send_keys("notebook")
        print("Digitando 'notebook' na barra de pesquisa...")
        
        search_box.send_keys(Keys.ENTER)
        print("Pressionando Enter...")
        
        time.sleep(5)
        
        html = driver.page_source
        site = BeautifulSoup(html, 'html.parser')
        
        produtos = site.find_all('div', class_=lambda x: x and ('product' in x or 'card' in x or 'item' in x))
        
        dados_produtos = []
        
        for produto in produtos[:10]:
            try:
                titulo_element = produto.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and ('title' in x or 'name' in x))
                titulo = titulo_element.text.strip() if titulo_element else 'Título não encontrado'
                
                preco_element = produto.find('span', class_=lambda x: x and ('price' in x or 'value' in x))
                preco = preco_element.text.strip() if preco_element else 'Preço não disponível'
                
                link_element = produto.find('a', href=True)
                link = link_element['href'] if link_element else 'Link não encontrado'
                if link and not link.startswith('http'):
                    link = 'https://www.zoom.com.br' + link
                
                dados_produtos.append({
                    'Título': titulo,
                    'Preço': preco,
                    'Link': link
                })
                
            except Exception as e:
                print(f"Erro ao extrair produto: {e}")
                continue
        
        if dados_produtos:
            df = pd.DataFrame(dados_produtos)
            print("\nResultados da busca por 'notebook':")
            print(df)
            
            df.to_csv('notebooks_zoom.csv', index=False, encoding='utf-8')
            print("\nDados salvos em 'notebooks_zoom.csv'")
        else:
            print("Nenhum produto encontrado!")
            
    except Exception as e:
        print(f"Erro ao localizar barra de pesquisa: {e}")
        print("HTML da página:")
        print(driver.page_source[:1000])



finally:

    driver.quit()
    print("Navegador fechado.")