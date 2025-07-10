# Scraper de Noticias con Resumen Automático

Este proyecto es un _scraper_ en Python que:

1. Extrae los titulares y URLs de la portada de un medio (por defecto **El Universal**).  
2. Descarga el texto completo de cada noticia.  
3. Genera un breve resumen automático usando la API de Hugging Face.  
4. Guarda los resultados en un CSV con columnas: `titular`, `url`, `resumen`.

---

## Tecnologías

- Python 3.8+  
- [requests](https://pypi.org/project/requests/)  
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)  
- [pandas](https://pypi.org/project/pandas/)  

## Token
Regístrate en Hugging Face y crea un Access Token con scope read.

Ve a tu perfil → Settings → Access Tokens → New token (scope read).

[Windows]
Exporta el token en la consola y reinicia tu IDE para poder ejecutar el script
- setx HF_TOKEN "hf_XXXXXXXXXXXXXXXXXXXXXXXX"

## Uso

python scraper.py

- Por defecto:

    -Portada: https://www.eluniversal.com.mx/

    -Selector titulares: h2.cards-story-opener-fr__title
---

## Estructura de archivos

scraper.py # Script principal
requirements.txt # Dependencias
README.md # Este fichero
