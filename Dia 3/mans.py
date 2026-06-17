import pygetwindow as gw
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Per al menú desplegable
import json
import os

FITXER_MEMORIA = "memoria_aural.json"

def AVISAR(missatge, segons=3):
    print(f"\n\n{'='*60}\n⚠️  NOTIFICACIÓ AURAL: {missatge}\n{'='*60}\n")

def TANCAR_FINESTRA(titol_exacte):
    try:
        finestres = gw.getWindowsWithTitle(titol_exacte)
        for f in finestres:
            f.close()
    except Exception as e:
        print(f"[ERROR MANS] No s'ha pogut tancar: {e}")

def MOSTRAR_FINESTRA_OK(missatge):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Aural", missatge)
    root.destroy()

def SELECCIONAR_OBJECTIU_INICIAL():
    """Finestra inicial intel·ligent per triar mètode directe o calibratge."""
    root = tk.Tk()
    root.title("AURAL - Menú Inicial")
    root.geometry("480x380")
    root.config(bg="#f4f4f4")
    root.eval('tk::PlaceWindow . center')
    root.attributes("-topmost", True)

    # Llegim les categories existents de la memòria
    categories_existents = []
    if os.path.exists(FITXER_MEMORIA) and os.path.getsize(FITXER_MEMORIA) > 0:
        try:
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                dades = json.load(f)
                categories_existents = list(dades.get("categories", {}).keys())
        except Exception:
            pass

    # Variables de Tkinter
    objectiu_var = tk.StringVar()
    categoria_triada = tk.StringVar()
    mode_final = tk.StringVar(value="RECONEIXEMENT")

    def iniciar_directe():
        cat = categoria_triada.get()
        if not cat or cat == "Tria un perfil guardat...":
            label_error.config(text="❌ Selecciona un perfil vàlid per entrar directe.")
            return
        objectiu_var.set(f"Treballar en perfil conegut: {cat}")
        mode_final.set("GUARDIA") # Forcem a saltar directament al vigilant
        root.destroy()

    def iniciar_nou_mode():
        text = objectiu_var.get().strip()
        if len(text) < 3:
            label_error.config(text="❌ Escriu un objectiu vàlid per al nou mode.")
            return
        mode_final.set("RECONEIXEMENT") # Forcem a calibrar
        root.destroy()

    tk.Label(root, text="AURAL SYSTEM", font=("Arial", 18, "bold"), bg="#f4f4f4", fg="#333").pack(pady=15)

    # SECCIÓ 1: ENTRADA DIRECTA (Si hi ha memòria històrica)
    frame_directe = tk.LabelFrame(root, text="🚀 Accés Directe (Perfils Guardats)", font=("Arial", 10, "bold"), bg="#f4f4f4", pady=10, padx=10)
    frame_directe.pack(fill="x", padx=20, pady=5)

    if categories_existents:
        desplegable = ttk.Combobox(frame_directe, textvariable=categoria_triada, font=("Arial", 11), state="readonly", width=25)
        desplegable['values'] = categories_existents
        desplegable.set("Tria un perfil guardat...")
        desplegable.pack(side="left", padx=10)
        
        tk.Button(frame_directe, text="⚡ Treballar Directe", command=iniciar_directe, font=("Arial", 10, "bold"), bg="#2196F3", fg="white").pack(side="left", padx=5)
    else:
        tk.Label(frame_directe, text="No tens cap perfil guardat encara. Usa el mode nou 👇", font=("Arial", 10, "italic"), bg="#f4f4f4", fg="#777").pack()

    # SECCIÓ 2: CREAR NOU PERFIL O CALIBRAR
    frame_nou = tk.LabelFrame(root, text="🧠 Crear o Calibrar Nou Perfil", font=("Arial", 10, "bold"), bg="#f4f4f4", pady=10, padx=10)
    frame_nou.pack(fill="x", padx=20, pady=10)

    tk.Label(frame_nou, text="Quin és el nou objectiu de treball?", font=("Arial", 10), bg="#f4f4f4").pack(anchor="w", padx=10)
    entrada = tk.Entry(frame_nou, textvariable=objectiu_var, font=("Arial", 11), width=35)
    entrada.pack(pady=5, padx=10)

    tk.Button(frame_nou, text="🔍 Registrar Apps Noves", command=iniciar_nou_mode, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white").pack(pady=5)

    label_error = tk.Label(root, text="", fg="red", bg="#f4f4f4", font=("Arial", 10, "bold"))
    label_error.pack(pady=5)

    root.mainloop()
    return objectiu_var.get().strip(), mode_final.get(), categoria_triada.get()

# Reutilitzem les altres funcions que ja tenies de Tkinter...
def PREGUNTAR_TIPUS_APP(nom_app, objectiu):
    root = tk.Tk()
    root.title("Aural - Nova App Detectada")
    root.geometry("450x220")
    root.config(bg="#f4f4f4")
    root.eval('tk::PlaceWindow . center')
    root.attributes("-topmost", True)
    resultat = tk.StringVar(value="DISTRET")

    def marcar_feina():
        resultat.set("PRODUCTIU"); root.destroy()
    def marcar_distracció():
        resultat.set("DISTRET"); root.destroy()

    tk.Label(root, text=f"🔍 Nova aplicació detectada:\n\"{nom_app}\"", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#333").pack(pady=15)
    tk.Label(root, text=f"Quin paper té per al teu objectiu:\n\"{objectiu}\"?", font=("Arial", 10, "italic"), bg="#f4f4f4", fg="#666").pack()
    frame_botons = tk.Frame(root, bg="#f4f4f4"); frame_botons.pack(pady=20)
    tk.Button(frame_botons, text="🟢 Eina de Treball", command=marcar_feina, font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", width=16).pack(side="left", padx=10)
    tk.Button(frame_botons, text="🔴 Distracció / Joc", command=marcar_distracció, font=("Arial", 11, "bold"), bg="#f44336", fg="white", width=16).pack(side="left", padx=10)
    root.mainloop()
    return resultat.get()

def PREGUNTAR_SEGUENT_PAS():
    root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
    resposta = messagebox.askyesno("Aural - Següent pas", "Vols examinar una altra aplicació nova o vols activar ja el Guardià?")
    root.destroy()
    return "EXAMINAR" if resposta else "TREBALLAR"

def VALIDAR_CATEGORIA_IA(objectiu, categoria_proposada):
    """Pregunta si la categoria de la IA és bona. Si no, permet triar una existent o escriure-la a mà."""
    root = tk.Tk()
    root.title("Aural - Validació de Perfil")
    root.geometry("480x320")
    root.config(bg="#f4f4f4")
    root.eval('tk::PlaceWindow . center')
    root.attributes("-topmost", True)

    # Llegim les teves categories actuals del JSON per omplir el desplegable
    categories_globals = ["general"]
    if os.path.exists(FITXER_MEMORIA) and os.path.getsize(FITXER_MEMORIA) > 0:
        try:
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                dades = json.load(f)
                categories_globals = list(dades.get("categories", {}).keys())
        except Exception:
            pass

    categoria_final = tk.StringVar(value=categoria_proposada)
    categoria_manual_var = tk.StringVar()

    def es_correcte():
        root.destroy()

    def es_incorrecte():
        frame_pregunta.pack_forget()
        frame_correccio.pack(pady=15, fill="x", padx=20)

    def desar_correccio():
        text_manual = categoria_manual_var.get().strip().lower()
        # Si l'usuari ha escrit alguna cosa a la caixa manual, té preferència absoluta
        if text_manual:
            nom_net = "".join(c for c in text_manual if c.isalnum() or c in ["-", "_"])
            categoria_final.set(nom_net)
        root.destroy()

    # INTERFÍCIE 1: PANEL DE PREGUNTA SÍ/NO
    frame_pregunta = tk.Frame(root, bg="#f4f4f4")
    frame_pregunta.pack(pady=30)

    tk.Label(frame_pregunta, text="🤖 Classificació Proposada per la IA", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#333").pack(pady=5)
    tk.Label(frame_pregunta, text=f"Per a: \"{objectiu}\"\nLa IA suggereix el perfil: {categoria_proposada.upper()}", font=("Arial", 11), bg="#f4f4f4", fg="#555").pack(pady=10)
    
    tk.Button(frame_pregunta, text="✅ Sí, em va bé", command=es_correcte, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", width=15).pack(side="left", padx=10, pady=10)
    tk.Button(frame_pregunta, text="❌ No, vull canviar-ho", command=es_incorrecte, font=("Arial", 10, "bold"), bg="#f44336", fg="white", width=15).pack(side="left", padx=10, pady=10)

    # INTERFÍCIE 2: PANEL DE CORRECCIÓ TOTALMENT DINÀMIC
    frame_correccio = tk.Frame(root, bg="#f4f4f4")
    
    tk.Label(frame_correccio, text="🛠️ Personalització del Perfil", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#333").pack(pady=5)
    
    # Opció A: Triar una que ja tinguis al JSON
    tk.Label(frame_correccio, text="Tria un perfil que ja tens creat:", font=("Arial", 9), bg="#f4f4f4", fg="#666").pack(anchor="w")
    opcions = ttk.Combobox(frame_correccio, textvariable=categoria_final, font=("Arial", 10), state="readonly", width=35)
    opcions['values'] = categories_globals
    opcions.pack(pady=2)
    
    tk.Label(frame_correccio, text="O escriu un nom nou completament a mà:", font=("Arial", 9), bg="#f4f4f4", fg="#666").pack(anchor="w", pady=(8,0))
    entrada_manual = tk.Entry(frame_correccio, textvariable=categoria_manual_var, font=("Arial", 10), width=38)
    entrada_manual.pack(pady=2)
    
    tk.Button(frame_correccio, text="💾 Aplicar i Desar", command=desar_correccio, font=("Arial", 10, "bold"), bg="#2196F3", fg="white", width=18).pack(pady=15)

    root.mainloop()
    return categoria_final.get()