import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin


def obtener_titulares(url):
    
    try:
        respuesta = requests.get(url,headers={
            'User-Agent' : 'ScraperNoticias/1.0 (https://www.eluniversal.com.mx/)'
            
        })
        
        respuesta.raise_for_status()
       
        soup = BeautifulSoup(respuesta.text, 'html.parser')
     
        titulares = []
        
        for titulo in soup.select('h2.cards-story-opener-fr__title'):
            texto = titulo.get_text(strip=True)
            
            liga = titulo.find_parent('a')
            href = liga['href'] if liga and liga.has_attr('href') else ''
            
            #conversiones de rutas relativas -> absolutas
            url_completa = urljoin(url,href)
            
            titulares.append({'titular': texto, 'url':url_completa})
        
        return titulares

    except requests.exceptions.RequestException as errhttp:
        #Errores HTTP
        print(f"Error {errhttp}")


def main():
    url = 'https://www.eluniversal.com.mx/'
    titulos = obtener_titulares(url)
    
    
    
    df = pd.DataFrame(titulos)
    df.to_csv('titulares.csv', index=False,encoding='utf-8-sig')
    
    print(f"{len(titulos)} Titulares guardados en csv")

if __name__ == '__main__':
    main()
