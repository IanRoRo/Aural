import pygetwindow as gw
import tkinter as tk
import customtkinter as ctk
import json
import os
from datetime import datetime
from fantasma import PERSONATGES
import sys

try:
    import winsound
    _TE_WINSOUND = True
except ImportError:
    _TE_WINSOUND = False


def ruta_recurs(nom_fitxer):
    """Retorna la ruta absoluta d'un RECURS ESTÀTIC (només lectura).
    En mode exe: apunta a sys._MEIPASS (carpeta temporal de PyInstaller).
    En mode script: apunta al directori del script.
    Ús: icones, plantilles JSON inicials, imatges, etc.
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nom_fitxer)


def ruta_dades_usuari(nom_fitxer):
    """Retorna la ruta absoluta d'un FITXER WRITABLE (dades d'usuari).
    En mode exe: apunta a %APPDATA%\\Aural per evitar permisos d'administrador.
    En mode script: apunta al directori del script.
    """
    if getattr(sys, 'frozen', False):
        appdata_dir = os.path.join(os.getenv('APPDATA'), 'Aural')
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, nom_fitxer)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nom_fitxer)

FITXER_MEMORIA = ruta_dades_usuari("memoria_aural.json")
FITXER_SESSIO = ruta_dades_usuari("session_state.json")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ---------------------------------------------------------------------
# PALETA I ESTILS
# ---------------------------------------------------------------------
COLOR_BG = "#1a1b26"
COLOR_CARD = "#242538"
COLOR_CARD_BORDER = "#34354f"
COLOR_INPUT = "#1e1f30"
COLOR_ACCENT = "#7c6cf0"
COLOR_ACCENT_HOVER = "#6a5ae0"
COLOR_SUCCESS = "#22c55e"
COLOR_SUCCESS_HOVER = "#16a34a"
COLOR_DANGER = "#ef4444"
COLOR_DANGER_HOVER = "#dc2626"
COLOR_WARNING = "#f59e0b"
COLOR_WARNING_HOVER = "#d97706"
COLOR_TEXT = "#e5e7eb"
COLOR_TEXT_MUTED = "#9399b2"

FONT_TITOL = ("Segoe UI", 26, "bold")
FONT_SECCIO = ("Segoe UI", 15, "bold")
FONT_SUBTITOL = ("Segoe UI", 12)
FONT_NORMAL = ("Segoe UI", 12)
FONT_BOTO = ("Segoe UI", 12, "bold")

# ---------------------------------------------------------------------
# UTILITATS INTERNES
# ---------------------------------------------------------------------
_ARREL_OCULTA = None


def _obtenir_arrel_oculta():
    global _ARREL_OCULTA
    if _ARREL_OCULTA is None or not _ARREL_OCULTA.winfo_exists():
        _ARREL_OCULTA = ctk.CTk()
        _ARREL_OCULTA.withdraw()
    return _ARREL_OCULTA


def _nova_finestra(titol, amplada, alcada, resizable=False):
    arrel = _obtenir_arrel_oculta()
    finestra = ctk.CTkToplevel(arrel)
    finestra.title(titol)
    finestra.configure(fg_color=COLOR_BG)
    finestra.resizable(resizable, resizable)
    finestra.attributes("-topmost", True)
    _centrar(finestra, amplada, alcada)
    return finestra


def _centrar(finestra, amplada, alcada):
    finestra.update_idletasks()
    ample_pantalla = finestra.winfo_screenwidth()
    alt_pantalla = finestra.winfo_screenheight()
    x = (ample_pantalla - amplada) // 2
    y = (alt_pantalla - alcada) // 2
    finestra.geometry(f"{amplada}x{alcada}+{x}+{y}")


def _llegir_categories():
    if os.path.exists(FITXER_MEMORIA) and os.path.getsize(FITXER_MEMORIA) > 0:
        try:
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                dades = json.load(f)
            return list(dades.get("categories", {}).keys())
        except Exception:
            pass
    return []


def _avis_curt(finestra_pare, missatge, tipus="info"):
    colors = {
        "info": COLOR_ACCENT,
        "warning": COLOR_WARNING,
        "error": COLOR_DANGER,
    }
    color = colors.get(tipus, COLOR_ACCENT)
    etiqueta = ctk.CTkLabel(
        finestra_pare, text=missatge, font=("Segoe UI", 11, "bold"),
        text_color=color,
    )
    etiqueta.pack(pady=4)
    finestra_pare.after(3000, etiqueta.destroy)


def _tancar_segur(finestra, retard=150):
    try:
        finestra.after(retard, finestra.destroy)
    except Exception:
        try:
            finestra.destroy()
        except Exception:
            pass


def _reproduir_so():
    try:
        if _TE_WINSOUND:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


# ---------------------------------------------------------------------
# GESTIÓ DE SESSIÓ
# ---------------------------------------------------------------------
def carregar_sessio():
    """Llegeix l'estat de la sessió anterior. Retorna None si no n'hi ha o està corrupte."""
    if not os.path.exists(FITXER_SESSIO):
        return None
    try:
        if os.path.getsize(FITXER_SESSIO) == 0:
            return None
        with open(FITXER_SESSIO, "r", encoding="utf-8") as f:
            dades = json.load(f)
        camps_essencials = ["objectiu", "categoria", "mode"]
        if not all(c in dades for c in camps_essencials):
            print("[SESSIO] Fitxer corrupte o incomplet. S'ignorarà.")
            return None
        return dades
    except (json.JSONDecodeError, Exception) as e:
        print(f"[SESSIO] Error llegint sessió: {e}. S'ignorarà.")
        return None


def guardar_sessio(dades_sessio):
    """Guarda l'estat actual de la sessió al JSON."""
    try:
        dades_sessio["timestamp"] = datetime.now().isoformat()
        with open(FITXER_SESSIO, "w", encoding="utf-8") as f:
            json.dump(dades_sessio, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SESSIO] Error guardant sessió: {e}")


def esborrar_sessio():
    """Elimina el fitxer de sessió (quan l'usuari vol començar de nou)."""
    try:
        if os.path.exists(FITXER_SESSIO):
            os.remove(FITXER_SESSIO)
    except Exception as e:
        print(f"[SESSIO] Error esborrant sessió: {e}")


def PREGUNTAR_REPRENDRE_SESSIO(dades_sessio):
    """Diàleg modal que pregunta si es vol reprendre la sessió anterior.
    Retorna True (reprendre) o False (començar de nou)."""
    finestra = _nova_finestra("Aural - Sessió anterior detectada", 520, 360)
    resultat = tk.BooleanVar(value=False)

    ctk.CTkLabel(finestra, text="💾", font=("Segoe UI Emoji", 40)).pack(pady=(18, 4))
    ctk.CTkLabel(
        finestra, text="Sessió anterior detectada",
        font=FONT_SECCIO, text_color=COLOR_TEXT,
    ).pack(pady=(0, 8))

    objectiu = dades_sessio.get("objectiu", "—")
    categoria = dades_sessio.get("categoria", "—").upper()
    timestamp = dades_sessio.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(timestamp)
        data_fmt = dt.strftime("%d/%m/%Y a les %H:%M")
    except Exception:
        data_fmt = "data desconeguda"

    pomodoro_info = ""
    pom = dades_sessio.get("pomodoro", {})
    if pom.get("actiu"):
        fase = "🍅 Treball" if pom.get("fase") == "treball" else "☕ Descans"
        segons = int(pom.get("segons_restants", 0))
        minuts, seg = divmod(max(0, segons), 60)
        pomodoro_info = f"\n🍅 Pomodoro: {fase} — {minuts:02d}:{seg:02d} restants"

    felicitat = dades_sessio.get("felicitat", 100)
    resum = (
        f'🎯 Objectiu: "{objectiu}"\n'
        f'📁 Perfil: {categoria}\n'
        f'💚 Felicitat: {felicitat}%\n'
        f'🕐 Última activitat: {data_fmt}'
        f'{pomodoro_info}'
    )

    ctk.CTkLabel(
        finestra, text=resum, font=FONT_NORMAL, text_color=COLOR_TEXT_MUTED,
        justify="left", wraplength=440,
    ).pack(pady=(0, 12), padx=30)

    ctk.CTkLabel(
        finestra, text="Vols continuar per on ho vas deixar?",
        font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT, justify="center",
    ).pack(pady=(0, 16))

    frame_botons = ctk.CTkFrame(finestra, fg_color="transparent")
    frame_botons.pack(pady=4)

    def si():
        resultat.set(True)
        _tancar_segur(finestra)

    def no():
        resultat.set(False)
        _tancar_segur(finestra)

    ctk.CTkButton(
        frame_botons, text="✅ Sí, continuar", command=si,
        width=180, height=42, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
        font=FONT_BOTO, corner_radius=8,
    ).pack(side="left", padx=8)
    ctk.CTkButton(
        frame_botons, text="❌ No, començar de nou", command=no,
        width=200, height=42, fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER,
        font=FONT_BOTO, corner_radius=8,
    ).pack(side="left", padx=8)

    finestra.protocol("WM_DELETE_WINDOW", no)
    finestra.wait_window()
    return resultat.get()


# ---------------------------------------------------------------------
# AVÍS INVASIU 
# ---------------------------------------------------------------------
def AVISAR(missatge, segons=3, titol="⚠️ SISTEMA AURAL — DISTRACCIÓ DETECTADA"):
    print(f"\n\n{'='*60}\n NOTIFICACIÓ AURAL: {missatge}\n{'='*60}\n")

    arrel = _obtenir_arrel_oculta()
    root = ctk.CTkToplevel(arrel)
    root.title(titol)
    root.configure(fg_color="#8B0000")
    root.attributes("-topmost", True)
    root.overrideredirect(True)

    ample_pantalla = root.winfo_screenwidth()
    alt_pantalla = root.winfo_screenheight()
    root.geometry(f"{ample_pantalla}x{alt_pantalla}+0+0")

    after_ids = []

    frame = ctk.CTkFrame(root, fg_color="#8B0000", corner_radius=0)
    frame.pack(expand=True, fill="both")

    icona = ctk.CTkLabel(frame, text="🛑", font=("Segoe UI Emoji", 80),
                         text_color="white", fg_color="#8B0000")
    icona.pack(pady=(60, 20))

    titol_label = ctk.CTkLabel(frame, text=titol, font=("Arial", 30, "bold"),
                               text_color="white", fg_color="#8B0000")
    titol_label.pack(pady=10)

    msg_label = ctk.CTkLabel(frame, text=missatge, font=("Arial", 20),
                             text_color="white", fg_color="#8B0000",
                             wraplength=900, justify="center")
    msg_label.pack(pady=10)

    compte_label = ctk.CTkLabel(frame, text="", font=("Arial", 14),
                                text_color="#ffcccc", fg_color="#8B0000")
    compte_label.pack(pady=20)

    def _tancar_avis():
        for after_id in after_ids:
            try:
                root.after_cancel(after_id)
            except Exception:
                pass
        after_ids.clear()
        try:
            root.grab_release()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass

    boto_tancar = ctk.CTkButton(
        frame, text="Ho he entès, torno a la feina",
        font=("Arial", 14, "bold"),
        fg_color="white", text_color="#8B0000",
        hover_color="#e0e0e0",
        state="disabled",
        command=_tancar_avis,
    )
    boto_tancar.pack(pady=10)

    def flaix():
        try:
            if not root.winfo_exists():
                return
            actual = root.cget("fg_color")
            nou = "#1a0000" if actual == "#8B0000" else "#8B0000"
            root.configure(fg_color=nou)
            frame.configure(fg_color=nou)
            icona.configure(fg_color=nou)
            titol_label.configure(fg_color=nou)
            msg_label.configure(fg_color=nou)
            compte_label.configure(fg_color=nou)
            after_ids.append(root.after(400, flaix))
        except Exception:
            pass

    def compte_enrere(restant):
        try:
            if not root.winfo_exists():
                return
            if restant > 0:
                compte_label.configure(text=f"Es podrà tancar en {restant} s...")
                after_ids.append(root.after(1000, compte_enrere, restant - 1))
            else:
                compte_label.configure(text="Ja pots tancar aquest avís.")
                boto_tancar.configure(state="normal")
        except Exception:
            pass

    def so_repetit(vegades_restants):
        try:
            if not root.winfo_exists() or vegades_restants <= 0:
                return
            _reproduir_so()
            after_ids.append(root.after(700, so_repetit, vegades_restants - 1))
        except Exception:
            pass

    flaix()
    compte_enrere(segons)
    so_repetit(3)

    root.focus_force()
    root.grab_set()
    root.protocol("WM_DELETE_WINDOW", _tancar_avis)
    root.wait_window()


# ---------------------------------------------------------------------
# VEURE / EDITAR LLISTES
# ---------------------------------------------------------------------
def VEURE_LLISTES(categoria):
    if not categoria:
        return
    memoria = {"categories": {}}
    if os.path.exists(FITXER_MEMORIA) and os.path.getsize(FITXER_MEMORIA) > 0:
        try:
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                memoria = json.load(f)
        except Exception:
            memoria = {"categories": {}}

    memoria.setdefault("categories", {})
    memoria["categories"].setdefault(categoria, {"llista_blanca": [], "llista_negra": []})
    cat_data = memoria["categories"][categoria]
    cat_data.setdefault("llista_blanca", [])
    cat_data.setdefault("llista_negra", [])

    def _desar():
        memoria["categories"][categoria] = cat_data
        with open(FITXER_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)

    finestra = _nova_finestra(f"AURAL - Llistes de {categoria}", 680, 560)
    ctk.CTkLabel(
        finestra, text=f"📋 Llistes del perfil: {categoria.upper()}",
        font=FONT_SECCIO, text_color=COLOR_TEXT,
    ).pack(pady=(18, 4))
    ctk.CTkLabel(
        finestra, text="Afegeix, mou o elimina aplicacions abans de començar",
        font=FONT_SUBTITOL, text_color=COLOR_TEXT_MUTED,
    ).pack(pady=(0, 12))

    frame_llistes = ctk.CTkFrame(finestra, fg_color="transparent")
    frame_llistes.pack(fill="both", expand=True, padx=20)
    frame_llistes.columnconfigure(0, weight=1)
    frame_llistes.columnconfigure(1, weight=1)
    frame_llistes.rowconfigure(0, weight=1)

    col_blanca = ctk.CTkFrame(
        frame_llistes, fg_color=COLOR_CARD, corner_radius=14,
        border_width=1, border_color=COLOR_CARD_BORDER,
    )
    col_blanca.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    ctk.CTkLabel(
        col_blanca, text="✅ Llista Blanca", font=("Segoe UI", 13, "bold"),
        text_color=COLOR_SUCCESS,
    ).pack(pady=(12, 8))
    scroll_blanca = ctk.CTkScrollableFrame(col_blanca, fg_color="transparent")
    scroll_blanca.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    col_negra = ctk.CTkFrame(
        frame_llistes, fg_color=COLOR_CARD, corner_radius=14,
        border_width=1, border_color=COLOR_CARD_BORDER,
    )
    col_negra.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    ctk.CTkLabel(
        col_negra, text="🚫 Llista Negra", font=("Segoe UI", 13, "bold"),
        text_color=COLOR_DANGER,
    ).pack(pady=(12, 8))
    scroll_negra = ctk.CTkScrollableFrame(col_negra, fg_color="transparent")
    scroll_negra.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    def _moure(app, a_blanca):
        if a_blanca:
            if app in cat_data["llista_negra"]:
                cat_data["llista_negra"].remove(app)
            if app not in cat_data["llista_blanca"]:
                cat_data["llista_blanca"].append(app)
        else:
            if app in cat_data["llista_blanca"]:
                cat_data["llista_blanca"].remove(app)
            if app not in cat_data["llista_negra"]:
                cat_data["llista_negra"].append(app)
        _refrescar()

    def _eliminar(app, de_blanca):
        llista = cat_data["llista_blanca"] if de_blanca else cat_data["llista_negra"]
        if app in llista:
            llista.remove(app)
        _refrescar()

    def _fila_app(contenidor, app, es_blanca):
        fila = ctk.CTkFrame(contenidor, fg_color=COLOR_INPUT, corner_radius=8)
        fila.pack(fill="x", pady=3, padx=2)
        ctk.CTkLabel(
            fila, text=app, font=FONT_NORMAL, text_color=COLOR_TEXT, anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(10, 4), pady=6)
        text_moure = "➡️" if es_blanca else "⬅️"
        ctk.CTkButton(
            fila, text=text_moure, width=32, height=26, corner_radius=6,
            fg_color=COLOR_WARNING, hover_color=COLOR_WARNING_HOVER,
            font=("Segoe UI", 11), command=lambda: _moure(app, not es_blanca),
        ).pack(side="left", padx=2, pady=4)
        ctk.CTkButton(
            fila, text="✕", width=28, height=26, corner_radius=6,
            fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER,
            font=("Segoe UI", 11, "bold"), command=lambda: _eliminar(app, es_blanca),
        ).pack(side="left", padx=(2, 6), pady=4)

    def _refrescar():
        for w in scroll_blanca.winfo_children():
            w.destroy()
        for w in scroll_negra.winfo_children():
            w.destroy()
        if not cat_data["llista_blanca"]:
            ctk.CTkLabel(
                scroll_blanca, text="(buida)", font=("Segoe UI", 10, "italic"),
                text_color=COLOR_TEXT_MUTED,
            ).pack(pady=10)
        for app in sorted(cat_data["llista_blanca"]):
            _fila_app(scroll_blanca, app, True)
        if not cat_data["llista_negra"]:
            ctk.CTkLabel(
                scroll_negra, text="(buida)", font=("Segoe UI", 10, "italic"),
                text_color=COLOR_TEXT_MUTED,
            ).pack(pady=10)
        for app in sorted(cat_data["llista_negra"]):
            _fila_app(scroll_negra, app, False)

    _refrescar()

    frame_afegir = ctk.CTkFrame(
        finestra, fg_color=COLOR_CARD, corner_radius=14,
        border_width=1, border_color=COLOR_CARD_BORDER,
    )
    frame_afegir.pack(fill="x", padx=20, pady=(14, 6))
    ctk.CTkLabel(
        frame_afegir, text="➕ Afegir aplicació manualment",
        font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT,
    ).pack(anchor="w", padx=14, pady=(10, 4))

    fila_entrada = ctk.CTkFrame(frame_afegir, fg_color="transparent")
    fila_entrada.pack(fill="x", padx=14, pady=(0, 12))
    nova_app_var = tk.StringVar()
    entrada = ctk.CTkEntry(
        fila_entrada, textvariable=nova_app_var, font=FONT_NORMAL,
        fg_color=COLOR_INPUT, border_color=COLOR_CARD_BORDER, corner_radius=8,
        placeholder_text="nom de l'aplicació...",
    )
    entrada.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def _afegir(a_blanca):
        nom = nova_app_var.get().strip().lower()
        if not nom:
            return
        _moure(nom, a_blanca)
        nova_app_var.set("")

    ctk.CTkButton(
        fila_entrada, text="🟢 Blanca", command=lambda: _afegir(True), width=90,
        fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, font=FONT_BOTO,
        corner_radius=8,
    ).pack(side="left", padx=3)
    ctk.CTkButton(
        fila_entrada, text="🔴 Negra", command=lambda: _afegir(False), width=90,
        fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER, font=FONT_BOTO,
        corner_radius=8,
    ).pack(side="left", padx=3)

    def _tancar():
        _desar()
        _tancar_segur(finestra)

    ctk.CTkButton(
        finestra, text="💾 Desar canvis i tancar", command=_tancar,
        fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_BOTO,
        corner_radius=8, height=40,
    ).pack(pady=(4, 16), padx=20, fill="x")

    finestra.protocol("WM_DELETE_WINDOW", _tancar)
    finestra.wait_window()


def TANCAR_FINESTRA(titol_exacte):
    if not titol_exacte or "aural" in titol_exacte.lower():
        return
    try:
        finestres = gw.getWindowsWithTitle(titol_exacte)
        for f in finestres:
            f.close()
    except Exception as e:
        print(f"[ERROR MANS] No s'ha pogut tancar: {e}")


def MOSTRAR_FINESTRA_OK(missatge):
    finestra = _nova_finestra("Aural", 380, 180)
    ctk.CTkLabel(finestra, text="✅", font=("Segoe UI Emoji", 40)).pack(pady=(20, 6))
    ctk.CTkLabel(
        finestra, text=missatge, font=FONT_NORMAL, text_color=COLOR_TEXT,
        wraplength=320, justify="center",
    ).pack(pady=(0, 16), padx=16)
    ctk.CTkButton(
        finestra, text="D'acord", command=lambda: _tancar_segur(finestra),
        fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_BOTO,
        corner_radius=8, width=120,
    ).pack(pady=(0, 16))
    finestra.wait_window()


# ---------------------------------------------------------------------
# MENÚ INICIAL
# ---------------------------------------------------------------------
def SELECCIONAR_OBJECTIU_INICIAL():
    import estadistiques_pro

    root = _nova_finestra("AURAL", 540, 840, resizable=True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    categories_existents = _llegir_categories()
    objectiu_var = tk.StringVar()
    categoria_triada = tk.StringVar()
    mode_final = tk.StringVar(value="RECONEIXEMENT")
    mascota_var = tk.StringVar(value="🎲 Aleatori")
    pomodoro_actiu_var = tk.BooleanVar(value=False)
    pomodoro_treball_var = tk.StringVar(value="25")
    pomodoro_descans_var = tk.StringVar(value="5")

    header = ctk.CTkFrame(root, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(30, 6))
    ctk.CTkLabel(
        header, text="👁️ AURAL", font=FONT_TITOL, text_color=COLOR_ACCENT,
    ).pack(anchor="w")
    ctk.CTkLabel(
        header, text="El teu sistema de concentració intel·ligent",
        font=FONT_SUBTITOL, text_color=COLOR_TEXT_MUTED,
    ).pack(anchor="w", pady=(2, 0))

    card_config = ctk.CTkFrame(
        root, fg_color=COLOR_CARD, corner_radius=16,
        border_width=1, border_color=COLOR_CARD_BORDER,
    )
    card_config.pack(fill="x", padx=30, pady=12)
    ctk.CTkLabel(
        card_config, text="👻 Tria la teva mascota", font=FONT_SECCIO,
        text_color=COLOR_TEXT,
    ).pack(anchor="w", padx=18, pady=(16, 2))

    noms_mascotes = ["🎲 Aleatori"] + [f'{p["emoji"]} {p["nom"]}' for p in PERSONATGES]
    ctk.CTkComboBox(
        card_config, values=noms_mascotes, variable=mascota_var,
        font=FONT_NORMAL, state="readonly", corner_radius=8, height=36,
        fg_color=COLOR_INPUT, border_color=COLOR_CARD_BORDER,
        button_color=COLOR_ACCENT, button_hover_color=COLOR_ACCENT_HOVER,
        dropdown_fg_color=COLOR_INPUT,
    ).pack(fill="x", padx=18, pady=(2, 14))

    ctk.CTkLabel(
        card_config, text="🍅 Mode Pomodoro (opcional)", font=FONT_SECCIO,
        text_color=COLOR_TEXT,
    ).pack(anchor="w", padx=18, pady=(2, 2))
    ctk.CTkLabel(
        card_config, text="Cicles de treball i descans amb bloqueig de pantalla",
        font=("Segoe UI", 10, "italic"), text_color=COLOR_TEXT_MUTED,
    ).pack(anchor="w", padx=18, pady=(0, 8))

    fila_pomodoro = ctk.CTkFrame(card_config, fg_color="transparent")
    fila_pomodoro.pack(fill="x", padx=18, pady=(0, 16))
    ctk.CTkSwitch(
        fila_pomodoro, text="Activar", variable=pomodoro_actiu_var,
        onvalue=True, offvalue=False, font=FONT_NORMAL,
        progress_color=COLOR_ACCENT,
    ).pack(side="left", padx=(0, 14))
    ctk.CTkLabel(
        fila_pomodoro, text="Treball (min)", font=("Segoe UI", 10),
        text_color=COLOR_TEXT_MUTED,
    ).pack(side="left", padx=(0, 4))
    ctk.CTkEntry(
        fila_pomodoro, textvariable=pomodoro_treball_var, width=48, height=32,
        font=FONT_NORMAL, corner_radius=8, fg_color=COLOR_INPUT,
        border_color=COLOR_CARD_BORDER, justify="center",
    ).pack(side="left", padx=(0, 10))
    ctk.CTkLabel(
        fila_pomodoro, text="Descans (min)", font=("Segoe UI", 10),
        text_color=COLOR_TEXT_MUTED,
    ).pack(side="left", padx=(0, 4))
    ctk.CTkEntry(
        fila_pomodoro, textvariable=pomodoro_descans_var, width=48, height=32,
        font=FONT_NORMAL, corner_radius=8, fg_color=COLOR_INPUT,
        border_color=COLOR_CARD_BORDER, justify="center",
    ).pack(side="left")

    card_directe = ctk.CTkFrame(
        root, fg_color=COLOR_CARD, corner_radius=16,
        border_width=1, border_color=COLOR_CARD_BORDER,
    )
    card_directe.pack(fill="x", padx=30, pady=12)
    ctk.CTkLabel(
        card_directe, text="🚀 Accés Directe", font=FONT_SECCIO,
        text_color=COLOR_TEXT,
    ).pack(anchor="w", padx=18, pady=(16, 2))

    if categories_existents:
        ctk.CTkLabel(
            card_directe, text="Perfils guardats", font=FONT_NORMAL,
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=18, pady=(4, 2))
        combo = ctk.CTkComboBox(
            card_directe, values=categories_existents, variable=categoria_triada,
            font=FONT_NORMAL, state="readonly", corner_radius=8, height=36,
            fg_color=COLOR_INPUT, border_color=COLOR_CARD_BORDER,
            button_color=COLOR_ACCENT, button_hover_color=COLOR_ACCENT_HOVER,
            dropdown_fg_color=COLOR_INPUT, dropdown_hover_color=COLOR_ACCENT,
        )
        combo.pack(fill="x", padx=18, pady=(2, 14))
        categoria_triada.set(categories_existents[0])

        frame_botons_directe = ctk.CTkFrame(card_directe, fg_color="transparent")
        frame_botons_directe.pack(fill="x", padx=18, pady=(0, 18))

        def iniciar_directe():
            cat = categoria_triada.get()
            if not cat:
                _avis_curt(root, "❌ Selecciona un perfil vàlid.", "error")
                return
            objectiu_var.set(f"Treballar en perfil conegut: {cat}")
            mode_final.set("GUARDIA")
            _tancar_segur(root)

        ctk.CTkButton(
            frame_botons_directe, text="⚡ Treballar Directe", command=iniciar_directe,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_BOTO,
            corner_radius=8, height=40,
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(
            frame_botons_directe, text="👁️ Llistes",
            command=lambda: VEURE_LLISTES(categoria_triada.get()),
            fg_color=COLOR_WARNING, hover_color=COLOR_WARNING_HOVER, font=FONT_BOTO,
            corner_radius=8, height=40, width=100,
        ).pack(side="left")
    else:
        ctk.CTkLabel(
            card_directe,
            text="Encara no tens cap perfil guardat.\nCrea'n un de nou aquí sota 👇",
            font=("Segoe UI", 11, "italic"), text_color=COLOR_TEXT_MUTED,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(4, 18))

    card_nou = ctk.CTkFrame(
        root, fg_color=COLOR_CARD, corner_radius=16,
        border_width=1, border_color=COLOR_CARD_BORDER,
    )
    card_nou.pack(fill="x", padx=30, pady=12)
    ctk.CTkLabel(
        card_nou, text="🧠 Crear o Calibrar Nou Perfil", font=FONT_SECCIO,
        text_color=COLOR_TEXT,
    ).pack(anchor="w", padx=18, pady=(16, 2))
    ctk.CTkLabel(
        card_nou, text="Quin és el teu objectiu de treball?", font=FONT_NORMAL,
        text_color=COLOR_TEXT_MUTED,
    ).pack(anchor="w", padx=18, pady=(4, 2))
    entrada = ctk.CTkEntry(
        card_nou, textvariable=objectiu_var, font=FONT_NORMAL, corner_radius=8,
        height=36, fg_color=COLOR_INPUT, border_color=COLOR_CARD_BORDER,
        placeholder_text="Ex: Estudiar per l'examen de Python",
    )
    entrada.pack(fill="x", padx=18, pady=(2, 14))

    def iniciar_nou_mode():
        text = objectiu_var.get().strip()
        if len(text) < 3:
            _avis_curt(root, "❌ Escriu un objectiu vàlid.", "error")
            return
        mode_final.set("RECONEIXEMENT")
        _tancar_segur(root)

    ctk.CTkButton(
        card_nou, text="🔍 Registrar Apps Noves", command=iniciar_nou_mode,
        fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, font=FONT_BOTO,
        corner_radius=8, height=40,
    ).pack(fill="x", padx=18, pady=(0, 18))

    def veure_estadistiques_click():
        estadistiques_pro.mostrar_grafics()

    ctk.CTkButton(
        root, text="📊 Veure Estadístiques de Rendiment",
        command=veure_estadistiques_click,
        fg_color="transparent", hover_color=COLOR_CARD, border_width=1,
        border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT, font=FONT_NORMAL,
        corner_radius=8, height=38,
    ).pack(fill="x", padx=30, pady=(4, 20))

    root.wait_window()

    mascota_sel = mascota_var.get()
    if mascota_sel.startswith("🎲"):
        mascota_final = None
    else:
        mascota_final = mascota_sel.split(" ", 1)[1] if " " in mascota_sel else mascota_sel

    pomodoro_cfg = (
        pomodoro_actiu_var.get(),
        pomodoro_treball_var.get(),
        pomodoro_descans_var.get(),
    )
    return (
        objectiu_var.get().strip(),
        mode_final.get(),
        categoria_triada.get(),
        mascota_final,
        pomodoro_cfg,
    )


# ---------------------------------------------------------------------
# NOVA APP DETECTADA
# ---------------------------------------------------------------------
def PREGUNTAR_TIPUS_APP(nom_app, objectiu):
    finestra = _nova_finestra("Aural - Nova App Detectada", 460, 260)
    resultat = tk.StringVar(value="DISTRET")
    ctk.CTkLabel(finestra, text="🔍", font=("Segoe UI Emoji", 34)).pack(pady=(20, 4))
    ctk.CTkLabel(
        finestra, text=f'Nova aplicació detectada:\n"{nom_app}"',
        font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT, justify="center",
    ).pack(pady=(0, 6))
    ctk.CTkLabel(
        finestra, text=f'Quin paper té per al teu objectiu:\n"{objectiu}"?',
        font=("Segoe UI", 11, "italic"), text_color=COLOR_TEXT_MUTED,
        justify="center", wraplength=380,
    ).pack(pady=(0, 18))

    frame_botons = ctk.CTkFrame(finestra, fg_color="transparent")
    frame_botons.pack(pady=6)

    def marcar_feina():
        resultat.set("PRODUCTIU")
        _tancar_segur(finestra)

    def marcar_distraccio():
        resultat.set("DISTRET")
        _tancar_segur(finestra)

    finestra.protocol("WM_DELETE_WINDOW", marcar_distraccio)
    ctk.CTkButton(
        frame_botons, text="🟢 Eina de Treball", command=marcar_feina,
        width=170, height=42, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
        font=FONT_BOTO, corner_radius=8,
    ).pack(side="left", padx=8)
    ctk.CTkButton(
        frame_botons, text="🔴 Distracció / Joc", command=marcar_distraccio,
        width=170, height=42, fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER,
        font=FONT_BOTO, corner_radius=8,
    ).pack(side="left", padx=8)

    finestra.wait_window()
    return resultat.get()


def PREGUNTAR_SEGUENT_PAS():
    finestra = _nova_finestra("Aural - Següent pas", 420, 220)
    resposta = tk.StringVar(value="TREBALLAR")
    ctk.CTkLabel(finestra, text="🤔", font=("Segoe UI Emoji", 34)).pack(pady=(20, 4))
    ctk.CTkLabel(
        finestra, text="Vols examinar una altra aplicació nova\no vols activar ja el Guardià?",
        font=FONT_NORMAL, text_color=COLOR_TEXT, justify="center",
    ).pack(pady=(0, 18))

    frame_botons = ctk.CTkFrame(finestra, fg_color="transparent")
    frame_botons.pack(pady=6)

    def examinar():
        resposta.set("EXAMINAR")
        _tancar_segur(finestra)

    def treballar():
        resposta.set("TREBALLAR")
        _tancar_segur(finestra)

    finestra.protocol("WM_DELETE_WINDOW", treballar)
    ctk.CTkButton(
        frame_botons, text="🔍 Examinar més", command=examinar, width=150, height=40,
        fg_color=COLOR_WARNING, hover_color=COLOR_WARNING_HOVER, font=FONT_BOTO,
        corner_radius=8,
    ).pack(side="left", padx=8)
    ctk.CTkButton(
        frame_botons, text="🛡️ Activar Guardià", command=treballar, width=150, height=40,
        fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_BOTO,
        corner_radius=8,
    ).pack(side="left", padx=8)

    finestra.wait_window()
    return resposta.get()


# ---------------------------------------------------------------------
# CONFIRMACIÓ INTERACTIVA D'APP NOVA EN MODE GUARDIA
# ---------------------------------------------------------------------
def PREGUNTAR_CONFIRMACIO_APP(nom_app, objectiu, suggeriment_ia, missatge_ia, timeout=25):
    finestra = _nova_finestra("Aural - App desconeguda detectada", 520, 340)
    resultat = tk.StringVar(value="")

    ctk.CTkLabel(finestra, text="🤔", font=("Segoe UI Emoji", 34)).pack(pady=(16, 4))
    ctk.CTkLabel(
        finestra, text=f'Aplicació no classificada:\n"{nom_app}"',
        font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT, justify="center",
    ).pack(pady=(0, 4))
    ctk.CTkLabel(
        finestra,
        text=f'La IA suggereix: {suggeriment_ia}\n"{missatge_ia}"\n\n'
             f'Confirmes aquesta classificació?',
        font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED,
        justify="center", wraplength=460,
    ).pack(pady=(0, 8))

    label_compte = ctk.CTkLabel(
        finestra, text=f"Temps restant: {timeout}s",
        font=("Segoe UI", 10, "italic"), text_color=COLOR_WARNING,
    )
    label_compte.pack(pady=(0, 8))

    frame_botons = ctk.CTkFrame(finestra, fg_color="transparent")
    frame_botons.pack(pady=4)

    def marcar_feina():
        resultat.set("PRODUCTIU")
        _tancar_segur(finestra)

    def marcar_distraccio():
        resultat.set("DISTRET")
        _tancar_segur(finestra)

    finestra.protocol("WM_DELETE_WINDOW", marcar_distraccio)

    ctk.CTkButton(
        frame_botons, text="🟢 Sí, és productiva", command=marcar_feina,
        width=180, height=42, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
        font=FONT_BOTO, corner_radius=8,
    ).pack(side="left", padx=6)
    ctk.CTkButton(
        frame_botons, text="🔴 Sí, és distracció", command=marcar_distraccio,
        width=180, height=42, fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER,
        font=FONT_BOTO, corner_radius=8,
    ).pack(side="left", padx=6)

    restant = [timeout]

    def tick():
        try:
            if not finestra.winfo_exists():
                return
            restant[0] -= 1
            if restant[0] <= 0:
                resultat.set(suggeriment_ia)
                _tancar_segur(finestra)
            else:
                label_compte.configure(text=f"Temps restant: {restant[0]}s")
                finestra.after(1000, tick)
        except Exception:
            pass

    finestra.after(1000, tick)
    finestra.wait_window()
    return resultat.get() or suggeriment_ia


# ---------------------------------------------------------------------
# VALIDACIÓ DE CATEGORIA IA
# ---------------------------------------------------------------------
def VALIDAR_CATEGORIA_IA(objectiu, categoria_proposada):
    finestra = _nova_finestra("Aural - Validació de Perfil", 500, 380)
    categories_globals = ["general"]
    if os.path.exists(FITXER_MEMORIA) and os.path.getsize(FITXER_MEMORIA) > 0:
        try:
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                dades = json.load(f)
                categories_globals = list(dades.get("categories", {}).keys()) or ["general"]
        except Exception:
            pass

    categoria_final = tk.StringVar(value=categoria_proposada)
    categoria_manual_var = tk.StringVar()

    frame_pregunta = ctk.CTkFrame(finestra, fg_color="transparent")
    frame_pregunta.pack(expand=True, fill="both")

    def es_correcte():
        _tancar_segur(finestra)

    def es_incorrecte():
        frame_pregunta.pack_forget()
        frame_correccio.pack(expand=True, fill="both", padx=10, pady=10)

    def desar_correccio():
        text_manual = categoria_manual_var.get().strip().lower()
        if text_manual:
            nom_net = "".join(c for c in text_manual if c.isalnum() or c in ["-", "_"])
            categoria_final.set(nom_net)
        _tancar_segur(finestra)

    finestra.protocol("WM_DELETE_WINDOW", es_correcte)

    ctk.CTkLabel(frame_pregunta, text="🤖", font=("Segoe UI Emoji", 40)).pack(pady=(24, 4))
    ctk.CTkLabel(
        frame_pregunta, text="Classificació Proposada per la IA",
        font=FONT_SECCIO, text_color=COLOR_TEXT,
    ).pack(pady=(0, 8))
    ctk.CTkLabel(
        frame_pregunta,
        text=f'Per a: "{objectiu}"\nLa IA suggereix el perfil: {categoria_proposada.upper()}',
        font=FONT_NORMAL, text_color=COLOR_TEXT_MUTED, justify="center",
        wraplength=420,
    ).pack(pady=(0, 20))

    frame_b = ctk.CTkFrame(frame_pregunta, fg_color="transparent")
    frame_b.pack()
    ctk.CTkButton(
        frame_b, text="✅ Sí, em va bé", command=es_correcte, width=160, height=40,
        fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, font=FONT_BOTO,
        corner_radius=8,
    ).pack(side="left", padx=8)
    ctk.CTkButton(
        frame_b, text="❌ No, vull canviar-ho", command=es_incorrecte, width=180, height=40,
        fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER, font=FONT_BOTO,
        corner_radius=8,
    ).pack(side="left", padx=8)

    frame_correccio = ctk.CTkFrame(finestra, fg_color="transparent")
    ctk.CTkLabel(
        frame_correccio, text="🛠️ Personalització del Perfil",
        font=FONT_SECCIO, text_color=COLOR_TEXT,
    ).pack(pady=(10, 14))
    ctk.CTkLabel(
        frame_correccio, text="Tria un perfil que ja tens creat:",
        font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED,
    ).pack(anchor="w", padx=20)
    ctk.CTkComboBox(
        frame_correccio, values=categories_globals, variable=categoria_final,
        font=FONT_NORMAL, state="readonly", corner_radius=8, height=34,
        fg_color=COLOR_INPUT, border_color=COLOR_CARD_BORDER,
        button_color=COLOR_ACCENT, button_hover_color=COLOR_ACCENT_HOVER,
        dropdown_fg_color=COLOR_INPUT,
    ).pack(fill="x", padx=20, pady=(2, 14))
    ctk.CTkLabel(
        frame_correccio, text="O escriu un nom nou completament a mà:",
        font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED,
    ).pack(anchor="w", padx=20)
    ctk.CTkEntry(
        frame_correccio, textvariable=categoria_manual_var, font=FONT_NORMAL,
        corner_radius=8, height=34, fg_color=COLOR_INPUT,
        border_color=COLOR_CARD_BORDER,
    ).pack(fill="x", padx=20, pady=(2, 16))
    ctk.CTkButton(
        frame_correccio, text="💾 Aplicar i Desar", command=desar_correccio,
        fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_BOTO,
        corner_radius=8, height=40,
    ).pack(padx=20, fill="x")

    finestra.wait_window()
    return categoria_final.get()