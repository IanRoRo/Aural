import psutil
import pygetwindow as gw
import pyautogui
import tkinter as tk
from tkinter import messagebox

def AVISAR(missatge):
    """Pas 2.1: Mostra una notificació emergent."""
    # Fem servir una finestra de missatge simple de Tkinter
    root = tk.Tk()
    root.withdraw() # Amaga la finestra principal de tk
    messagebox.showwarning("AURAL ET VIGILA", missatge)
    root.destroy()

def TANCAR_FINESTRA():
    """Pas 2.2: Busca el procés de la finestra activa i el liquida."""
    try:
        window = gw.getActiveWindow()
        if window:
            titol = window.title.lower()
            print(f"--- Intentant tancar: {titol} ---")
            
            # Intentem el mètode suau primer
            window.close()
            
            # Si és un navegador, anem a pel procés (mètode fort)
            for proc in psutil.process_iter(['pid', 'name']):
                name = proc.info['name'].lower()
                # Si el títol conté Chrome i el procés es diu chrome...
                if ("chrome" in titol and "chrome" in name) or \
                   ("edge" in titol and "msedge" in name) or \
                   ("firefox" in titol and "firefox" in name):
                    proc.kill()
                    print(f"Procés {name} liquidat amb èxit.")
    except Exception as e:
        print(f"Error crític en tancar: {e}")

def BLOQUEJAR_INICI():
    """Pas 2.3: Pantalla de bloqueig inicial."""
    root = tk.Tk()
    root.title("AURAL - BLOQUEIG DE SEGURETAT")
    root.attributes("-fullscreen", True) # Pantalla completa
    root.attributes("-topmost", True)    # Sempre per sobre de tot
    
    objectiu = tk.StringVar()

    def enviar():
        if len(objectiu.get()) > 10: # Validació simple per ara
            root.destroy()
        else:
            label_error.config(text="Sigues més específic, no em prenguis el pèl.")

    label = tk.Label(root, text="Què faràs ara mateix?", font=("Arial", 24))
    label.pack(pady=50)
    
    entrada = tk.Entry(root, textvariable=objectiu, font=("Arial", 18), width=50)
    entrada.pack(pady=20)
    
    label_error = tk.Label(root, text="", fg="red", font=("Arial", 14))
    label_error.pack()

    boto = tk.Button(root, text="Establir Objectiu", command=enviar, font=("Arial", 14))
    boto.pack(pady=20)

    root.mainloop()
    return objectiu.get()
