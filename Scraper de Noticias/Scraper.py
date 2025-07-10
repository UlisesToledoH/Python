import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
import sys
import time


token = os.getenv("HF_TOKEN")
if not token:
    sys.exit(
        "No variable de entorno HF_TOKEN. "
        "Asegúrate de exportarla antes de ejecutar el script."
    )


def procesar_noticias(url_portada):
    registros = []
    # 1) Recorro la lista de titulares con su href
    for item in obtener_titulares(url_portada):
        titular = item["titular"]
        href = item["url"]

        # 2) Descargar el texto completo
        try:
            full_url, texto = extraer_texto_completo(url_portada, href)
        except Exception as e:
            print(f"  ! Error descargando {href}: {e}")
            continue

        # 3) Resumir
        try:
            resumen = resumir_con_IA(texto)
        except Exception as e:
            resumen = f"[Error al resumir: {e}]"

        registros.append({"titular": titular, "url": full_url, "resumen": resumen})

    return registros


def resumir_con_IA(texto, mxlen=60, minlen=20):
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # arrancamos con los primeros 2000 caracteres
    fragmento = texto[:2000]

    for intento in range(3):
        print(f"[DEBUG] Intento {intento+1}: enviando {len(fragmento)} caracteres")
        payload = {
            "inputs": fragmento,
            "parameters": {
                "max_length": mxlen,
                "min_length": minlen,
                "do_sample": False
            }
        }
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 400:
            # reduce a la mitad y reintenta tras un pequeño sleep
            fragmento = fragmento[: len(fragmento)//2 ]
            print(f"  * 400 Bad Request: reduciendo texto a {len(fragmento)} caracteres y reintentando…")
            time.sleep(1)
            continue
        resp.raise_for_status()
        data = resp.json()
        # si el modelo no está listo, HF devuelve {"error": "..."}
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(data["error"])
        # retorno seguro usando .get()
        return data[0].get("summary_text", "")

    # si tras 3 intentos sigue fallando, devolvemos vacío o aviso
    return "[Error al resumir tras varios intentos]"

def extraer_texto_completo(base_url, href):
    url_cmplt = urljoin(base_url, href)
    respuesta = requests.get(url_cmplt, headers={"User-Agent": "ScraperNoticias/1.0"})
    respuesta.raise_for_status()
    soup = BeautifulSoup(respuesta.text, "html.parser")

    parrafos = soup.select('p.sc__font-paragraph[itemprop="description"]')

    # ajuste de selector
    parrafos = soup.find_all('p')
    texto = "\n".join(p.get_text(strip=True) for p in parrafos)
    return url_cmplt, texto


def obtener_titulares(url):

    try:
        respuesta = requests.get(
            url,
            headers={
                "User-Agent": "ScraperNoticias/1.0 (https://www.eluniversal.com.mx/)"
            },
        )

        respuesta.raise_for_status()

        soup = BeautifulSoup(respuesta.text, "html.parser")

        titulares = []

        for titulo in soup.select("h2.cards-story-opener-fr__title"):
            texto = titulo.get_text(strip=True)

            liga = titulo.find_parent("a")
            href = liga["href"] if liga and liga.has_attr("href") else ""

            # conversiones de rutas relativas -> absolutas
            url_completa = urljoin(url, href)

            titulares.append({"titular": texto, "url": url_completa})

        return titulares

    except requests.exceptions.RequestException as errhttp:
        # Errores HTTP
        print(f"Error {errhttp}")


def main():
    url = "https://www.eluniversal.com.mx/"

    titulos = obtener_titulares(url)

    # df = pd.DataFrame(titulos)
    # df.to_csv('titulares.csv', index=False,encoding='utf-8-sig')
    # print(f"{len(titulos)} Titulares guardados en csv")

    datos = procesar_noticias(url)
    df = pd.DataFrame(datos)
    df.to_csv("noticias_resumidas.csv", index=False, encoding="utf-8-sig")
    print(f"{len(df)} artículos procesados y resumidos.")


if __name__ == "__main__":
    main()
