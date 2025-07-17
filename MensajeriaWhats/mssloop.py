import os
import sys
import time
import threading

import customtkinter as ctk
from tkinter import messagebox
from tkinter import font as tkfont

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Para etiquetar
from selenium.webdriver.common.keys import Keys

def resource_path(relative_path):
    """ Devuelve la ruta absoluta al recurso, ya sea en dev o en el exe one-file """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller extrae todo aquí
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)

# ——— Función para arrancar ChromeDriver con perfil y flags adecuados ———
def iniciar_driver():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver_exe = os.path.join(base_dir, "chromedriver-win64", "chromedriver.exe")
    profile = os.path.join(base_dir, "User_Data")

    if not os.path.isfile(driver_exe):
        raise FileNotFoundError(f"chromedriver.exe no encontrado en:\n{driver_exe}")

    opts = Options()
    opts.add_argument(f"--user-data-dir={profile}")
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--log-level=3")

    service = Service(executable_path=driver_exe, log_path=os.devnull)
    return webdriver.Chrome(service=service, options=opts)


# ——— Función que envía mensajes a los grupos listados ———
def enviar_a_grupos():
    # 1) Leer repeticiones, grupos y mensaje desde la UI
    try:
        repeticiones = int(entry_reps.get())
    except ValueError:
        messagebox.showwarning(
            "Dato inválido", "Introduce un número entero para repeticiones."
        )
        return
    if repeticiones < 1:
        messagebox.showwarning("Valor mínimo", "Debe enviar al menos 1 repetición.")
        return
    if repeticiones > 50:
        messagebox.showinfo(
            "Tope alcanzado", "El número de repeticiones se limitó a 50."
        )
        repeticiones = 50

    raw_grupos = txt_grupos.get("1.0", "end").strip()
    mensaje = txt_mensaje.get("1.0", "end").strip()
    if not raw_grupos or not mensaje:
        messagebox.showwarning(
            "Datos incompletos", "Ingresa nombres de grupos y mensaje."
        )
        return

    grupos = [g.strip() for g in raw_grupos.splitlines() if g.strip()]

    # 2) Arrancar navegador
    try:
        driver = iniciar_driver()
    except Exception as e:
        messagebox.showerror("Error al iniciar driver", str(e))
        return

    driver.get("https://web.whatsapp.com")
    # Esperar a que cargue la lista de chats
    try:
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[aria-label='Lista de chats']")
            )
        )
    except:
        messagebox.showerror("Timeout", "No se detectó la lista de chats a tiempo.")
        driver.quit()
        return

    messagebox.showinfo(
        "Listo", "Verifica que estés logueado en WhatsApp Web y pulsa OK."
    )

    # 3) Para cada grupo, clic sobre él y envío del mensaje X veces
    for idx, grupo in enumerate(grupos, start=1):
        # 3.1 Seleccionar el chat del grupo
        try:
            chat = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[@title='{grupo}']"))
            )
            chat.click()
        except Exception as e:
            print(f" Grupo “{grupo}” no encontrado: {e}")
            continue

        # 3.2 Enviar el mensaje las repeticiones indicadas
        for i in range(repeticiones):
            try:
                # Esto captura únicamente el input de mensaje que está en el footer
                caja = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "footer div[contenteditable='true']")
                    )
                )
                caja.click()
                caja.clear()
                caja.send_keys(mensaje)
                caja.send_keys(Keys.SHIFT, Keys.ENTER)

                send_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@aria-label='Enviar']")
                    )
                )
                send_btn.click()

                print(f"[{grupo}] Envío {i+1}/{repeticiones}")
                time.sleep(1)
            except Exception as e:
                print(f" Error envío {i+1} a {grupo}: {e}")
                break

        messagebox.showinfo(
            "Grupo procesado",
            f"Se enviaron hasta {repeticiones} mensajes a “{grupo}” ({idx}/{len(grupos)})",
        )

    # 4) Cerrar navegador al terminar
    driver.quit()
    messagebox.showinfo(
        "Terminado", "Todos los mensajes fueron enviados y WhatsApp Web se cerró."
    )


# ——— Construcción de la UI con CustomTkinter ———
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ventana = ctk.CTk()
ventana = ctk.CTk(fg_color="#E5DBCF")
ventana.title("Mensajeria Batch Whatsapp")
ventana.iconbitmap(resource_path("Icon/icono.ico"))
ventana.geometry("350x420")

ventana.resizable(False, False)

# Input: nombres de grupos
ctk.CTkLabel(ventana, text="Nombres de grupos/contactos (uno por línea):", text_color="#0F3B5F", font=("Consola", 14, "bold")).pack(pady=(20, 5))
txt_grupos = ctk.CTkTextbox(ventana, width=300, height=100, fg_color="#0F3B5F",  corner_radius=8, font=("Consola", 14, "bold"))
txt_grupos.pack(pady=(0, 10))

# Input: mensaje
ctk.CTkLabel(ventana, text="Mensaje a enviar:", text_color="#0F3B5F", font=("Consola", 14, "bold") ).pack(pady=(0, 2))
txt_mensaje = ctk.CTkTextbox(ventana, width=300, height=100, fg_color="#0F3B5F",  corner_radius=8,font=("Consola", 14, "bold"))
txt_mensaje.pack(pady=(0, 10))

# Input: repeticiones
ctk.CTkLabel(ventana, text="Repeticiones de mensaje [50 max]:", text_color="#0F3B5F", font=("Consola", 14, "bold")).pack(pady=(0, 2))
entry_reps = ctk.CTkEntry(ventana, width=100, justify="center", font=("Consola", 14, "bold"))
entry_reps.insert(0, "5")
entry_reps.pack(pady=(0, 10))

# Botón: lanzar en un hilo para no bloquear la UI
btn_enviar = ctk.CTkButton(
    ventana,
    text="Enviar",
    command=lambda: threading.Thread(target=enviar_a_grupos, daemon=True).start(),
    fg_color="#CC9752",
    text_color="#E5DBCF",
    hover_color="#0F3B5F",
    font=("Consola", 14, "bold")
)
btn_enviar.pack(pady=5)

ventana.mainloop()
