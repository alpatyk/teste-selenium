from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from collections import Counter
import json
import random

class ZoomScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.all_products = []
        self.product_counter = Counter()

    def accept_cookies(self):
        """Aceita cookies se aparecer"""
        try:
            cookie_selectors = [
                "button[aria-label*='cookie']",
                "button[aria-label*='Cookie']",
                ".cookie-accept",
                ".accept-cookies",
                "#acceptCookies",
                "button:contains('Aceitar')",
                "button:contains('aceitar')"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_btn.click()
                    print("Cookies aceitos")
                    time.sleep(1)
                    return True
                except:
                    continue
            print("Botão de cookies não encontrado")
            return False
        except Exception as e:
            print(f"Erro ao aceitar cookies: {e}")
            return False

    def find_search_box(self):
        """Encontra a barra de pesquisa com múltiplos seletores"""
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='pesquisar']",
            "input[placeholder*='buscar']",
            "input[placeholder*='procurar']",
            "#search",
            ".search-input",
            ".search-box",
            "input[name='q']",
            "input[name='search']",
            "form[role='search'] input",
            ".header-search input"
        ]
        
        for selector in search_selectors:
            try:
                search_box = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Barra de pesquisa encontrada com seletor: {selector}")
                return search_box
            except:
                continue
        
        print("Barra de pesquisa não encontrada com seletores comuns")
        return None

    def search_product(self, product_name):
        """Realiza uma pesquisa no site"""
        try:
            print("Procurando barra de pesquisa...")
            
            search_box = self.find_search_box()
            
            if not search_box:
                print("Tentando método alternativo...")
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for input_elem in inputs:
                        try:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                input_type = input_elem.get_attribute("type")
                                placeholder = input_elem.get_attribute("placeholder") or ""
                                if input_type in ["search", "text"] and any(word in placeholder.lower() for word in ["pesquisar", "buscar", "procurar"]):
                                    search_box = input_elem
                                    break
                        except:
                            continue
                except:
                    pass
            
            if search_box:
                search_box.clear()
                search_box.send_keys(product_name)
                search_box.send_keys(Keys.ENTER)
                print(f"Busca por '{product_name}' realizada!")
                
                time.sleep(5)
                
                current_url = self.driver.current_url
                if "search" in current_url.lower() or "q=" in current_url.lower():
                    print("Parece que estamos na página de resultados!")
                    return True
                else:
                    print("Possível problema na pesquisa. URL atual:", current_url)
                    return False
            else:
                print("Não foi possível encontrar a barra de pesquisa")
                return False
                
        except Exception as e:
            print(f"Erro na pesquisa: {e}")
            return False

    def debug_page(self):
        """Debug: mostra informações da página atual"""
        print("\n=== DEBUG DA PÁGINA ===")
        print("URL:", self.driver.current_url)
        print("Título:", self.driver.title)
        
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print("HTML salvo em debug_page.html")
        
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"Inputs encontrados: {len(inputs)}")
            for i, input_elem in enumerate(inputs[:5]):
                try:
                    input_type = input_elem.get_attribute("type") or "sem tipo"
                    placeholder = input_elem.get_attribute("placeholder") or "sem placeholder"
                    print(f"  Input {i+1}: type={input_type}, placeholder={placeholder}")
                except:
                    print(f"  Input {i+1}: não pode ser lido")
        except Exception as e:
            print(f"Erro ao analisar inputs: {e}")

    def manual_search_fallback(self, product_name):
        """Método alternativo manual para pesquisa"""
        try:
            print("Tentando método manual de pesquisa...")
            
            with open('manual_debug.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"Forms encontrados: {len(forms)}")
            
            for form in forms:
                try:
                    form_action = form.get_attribute("action") or ""
                    form_method = form.get_attribute("method") or ""
                    
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    search_input = None
                    
                    for input_elem in inputs:
                        input_type = input_elem.get_attribute("type") or ""
                        if input_type in ["search", "text"]:
                            search_input = input_elem
                            break
                    
                    if search_input:
                        search_input.clear()
                        search_input.send_keys(product_name)
                        search_input.send_keys(Keys.ENTER)
                        print("Pesquisa manual realizada!")
                        time.sleep(5)
                        return True
                        
                except Exception as e:
                    continue
            
            print("Método manual também falhou")
            return False
            
        except Exception as e:
            print(f"Erro no método manual: {e}")
            return False

    def extract_products_from_page(self):
        """Extrai produtos da página atual - versão simplificada"""
        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            products = []
            
            product_candidates = soup.find_all(['div', 'article', 'section'], 
                class_=lambda x: x and any(word in str(x).lower() for word in ['product', 'card', 'item', 'produto']))
            
            print(f"Candidatos a produtos encontrados: {len(product_candidates)}")
            
            for candidate in product_candidates:
                try:
                    title_elem = candidate.find(['h2', 'h3', 'h4', 'a'])
                    title = title_elem.text.strip() if title_elem else 'Sem título'
                    
                    price_elem = candidate.find(string=re.compile(r'R\$\s*\d'))
                    if not price_elem:
                        price_elems = candidate.find_all('span', string=re.compile(r'R\$\s*\d'))
                        price_elem = price_elems[0] if price_elems else None
                    
                    price = price_elem.strip() if price_elem else 'Sem preço'
                    
                    link_elem = candidate.find('a', href=True)
                    link = link_elem['href'] if link_elem else None
                    if link and not link.startswith('http'):
                        link = 'https://www.zoom.com.br' + link
                    
                    product_data = {
                        'title': title,
                        'price': price,
                        'link': link,
                        'filter': getattr(self, 'current_filter', 'default')
                    }
                    
                    products.append(product_data)
                    self.product_counter[title] += 1
                    
                except Exception as e:
                    continue
            
            return products
            
        except Exception as e:
            print(f"Erro ao extrair produtos: {e}")
            return []

    def run_complete_analysis(self, product_name):
        """Executa a análise completa"""
        print("Iniciando análise completa...")
        
        self.driver.get('https://www.zoom.com.br')
        print("Site carregado")
        time.sleep(3)
        
        self.accept_cookies()
        
        self.debug_page()
        
        if not self.search_product(product_name):
            print("Pesquisa automática falhou, tentando método manual...")
            if not self.manual_search_fallback(product_name):
                print("Falha completa na pesquisa. Verifique o arquivo debug_page.html")
                return []
        
        print("\n=== PÁGINA DE RESULTADOS ===")
        self.debug_page()
        
        produtos = self.extract_products_from_page()
        print(f"Produtos extraídos: {len(produtos)}")
        
        if produtos:
            results = []
            for i, produto in enumerate(produtos, 1):
                results.append({
                    'rank': i,
                    'name': produto['title'],
                    'price': produto['price'],
                    'url': produto['link'],
                    'specifications': {}  # Placeholder
                })
            
            self.save_results(results)
            return results
        else:
            print("Nenhum produto encontrado")
            return []

    def save_results(self, products_data):
        """Salva os resultados em arquivos"""
        try:
            with open('zoom_analysis_results.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            
            csv_data = []
            for product in products_data:
                csv_data.append({
                    'Rank': product['rank'],
                    'Produto': product['name'],
                    'Preço': product['price'],
                    'URL': product['url']
                })
            
            df = pd.DataFrame(csv_data)
            df.to_csv('zoom_products.csv', index=False, encoding='utf-8')
            
            print("\nResultados salvos em:")
            print("- zoom_analysis_results.json")
            print("- zoom_products.csv")
            
        except Exception as e:
            print(f"Erro ao salvar resultados: {e}")

    def close(self):
        """Fecha o navegador"""
        self.driver.quit()
        print("Navegador fechado.")

if __name__ == "__main__":
    scraper = ZoomScraper()
    
    try:
        product_name = "notebook"
        print("Iniciando scraping do Zoom...")
        print("Este processo pode demorar alguns minutos")
        
        results = scraper.run_complete_analysis(product_name)
        
        if results:
            print(f"\n✅ Análise concluída! {len(results)} produtos encontrados.")
            print("\nTop produtos:")
            for i, product in enumerate(results[:5], 1):
                print(f"{i}. {product['name']} - {product['price']}")
        else:
            print("\n❌ Nenhum produto encontrado. Verifique os arquivos de debug.")
            
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()