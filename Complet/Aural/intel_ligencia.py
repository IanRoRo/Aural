import ollama
import json
import os
import sys

def ruta_recurs(nom_fitxer):
    """Retorna la ruta absoluta d'un RECURS ESTÀTIC (només lectura)."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nom_fitxer)

def ruta_dades_usuari(nom_fitxer):
    """Retorna la ruta absoluta d'un FITXER WRITABLE (dades d'usuari).
    En mode exe: apunta a %APPDATA%\Aural per evitar permisos d'administrador.
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

def carregar_memoria():
    if os.path.exists(FITXER_MEMORIA):
        try:
            if os.path.getsize(FITXER_MEMORIA) == 0:
                return {"categories": {}, "correccions_ia": {}}
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                memoria = json.load(f)
            if "categories" not in memoria:
                memoria["categories"] = {}
            if "correccions_ia" not in memoria:
                memoria["correccions_ia"] = {}
            return memoria
        except Exception:
            return {"categories": {}, "correccions_ia": {}}
    return {"categories": {}, "correccions_ia": {}}

def guardar_memoria(memoria):
    with open(FITXER_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)

def assegurar_ollama():
    try:
        ollama.list()
    except Exception:
        print(" ERROR: Ollama no està actiu.")

def determinar_categoria_ia(objectiu_usuari):
    objectiu_min = objectiu_usuari.lower().strip()
    memoria = carregar_memoria()
    if objectiu_min in memoria.get("correccions_ia", {}):
        return memoria["correccions_ia"][objectiu_min]

    assegurar_ollama()
    try:
        prompt = f"""
        Analyze this user productivity goal: "{objectiu_usuari}"
        Generate a single-word generic category/profile name for it (lowercase, no spaces, no punctuation, alphanumeric only).
        Examples: python, blender, english, accounting, admin, gym.
        Reply ONLY with that single word.
        """
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        cat = response["message"]["content"].strip().lower()
        cat_neta = "".join(c for c in cat if c.isalnum() or c in ["-", "_"])
        return cat_neta if cat_neta else "general"
    except Exception:
        return "general"

def buscar_perfil_similar(objectiu_usuari):
    memoria = carregar_memoria()
    categories = list(memoria.get("categories", {}).keys())
    if not categories:
        return None

    objectiu_min = objectiu_usuari.lower().strip()
    if objectiu_min in memoria.get("correccions_ia", {}):
        return memoria["correccions_ia"][objectiu_min]

    assegurar_ollama()
    try:
        prompt = f"""
        User goal: "{objectiu_usuari}"
        Existing profiles: {json.dumps(categories)}
        Does any existing profile match this goal closely (same topic, same tool, same activity)?
        Reply ONLY with the exact profile name from the list, or the word NONE if there is no good match.
        """
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        cat = response["message"]["content"].strip()
        for c in categories:
            if c.lower() == cat.lower():
                return c
        return None
    except Exception:
        return None

def guardar_feedback_usuari(objectiu_usuari, categoria_correcta):
    memoria = carregar_memoria()
    objectiu_min = objectiu_usuari.lower().strip()
    memoria["correccions_ia"][objectiu_min] = categoria_correcta
    guardar_memoria(memoria)
    print(f" [FEEDBACK] '{objectiu_min}' -> categoria '{categoria_correcta}'.")

def extreure_nom_app(titol_finestra):
    if not titol_finestra or titol_finestra.strip() in ["", "Escriptori", "Desconegut"]:
        return None
    if titol_finestra.strip().lower().startswith("aural"):
        return None

    titol_min = titol_finestra.lower()
    navegadors = ["google chrome", "microsoft edge", "firefox", "brave"]
    if any(nav in titol_min for nav in navegadors):
        parts = [p.strip() for p in titol_min.split("-") if p.strip()]
        if len(parts) >= 3:
            nom_web = parts[-2]
            if any(nav in nom_web for nav in navegadors):
                nom_web = parts[0]
            return f"web: {nom_web}"
        elif len(parts) == 2:
            return f"web: {parts[0]}"
        return "web: navegació general"

    paraula = titol_min.split("-")[-1].strip() if "-" in titol_min else titol_min.split()[0]
    return paraula if len(paraula) >= 3 else titol_min[:12]

def registrar_app_manual(categoria, nom_app, estat):
    memoria = carregar_memoria()
    if categoria not in memoria["categories"]:
        memoria["categories"][categoria] = {"llista_blanca": [], "llista_negra": []}
    subllista = memoria["categories"][categoria]
    if estat == "PRODUCTIU" and nom_app not in subllista["llista_blanca"]:
        subllista["llista_blanca"].append(nom_app)
    elif estat == "DISTRET" and nom_app not in subllista["llista_negra"]:
        subllista["llista_negra"].append(nom_app)
    guardar_memoria(memoria)

def avaluar_amb_ia(objectiu_usuari, titol_finestra):
    if not titol_finestra or titol_finestra.strip() == "":
        return "PRODUCTIU", "Mirant l'horitzó..."

    titol_min = titol_finestra.lower()
    categoria = determinar_categoria_ia(objectiu_usuari)
    memoria = carregar_memoria()

    jocs_basics = [
        "minecraft", "fortnite", "roblox", "league of legends",
        "twitch", "netflix", "gta", "youtube", "tiktok", "instagram",
    ]

    if categoria not in memoria["categories"]:
        memoria["categories"][categoria] = {"llista_blanca": [], "llista_negra": jocs_basics}
        guardar_memoria(memoria)

    subllista = memoria["categories"][categoria]

    if any(brossa in titol_min for brossa in subllista["llista_negra"]):
        return "DISTRET", f"Bloquejat per llista negra de la categoria [{categoria}]."

    if any(bona in titol_min for bona in subllista["llista_blanca"]) and not any(
        nav in titol_min for nav in ["chrome", "edge", "firefox", "brave"]
    ):
        return "PRODUCTIU", "Eina de software validada per a aquest context."

    assegurar_ollama()
    try:
        prompt = f"""
        You are a strict monitor for the category: "{categoria}".
        USER GOAL: "{objectiu_usuari}"
        CURRENT WINDOW: "{titol_finestra}"
        CRITERIA:
        - If the window is Gemini/ChatGPT, read the title carefully. If the user is chatting about video games, movies, entertainment or general slacking, it is DISTRET. If it's about coding/learning, it is PRODUCTIU.
        - Any video game (Fortnite, Minecraft, etc.) or social media is strictly DISTRET.
        - Productive tools (IDEs, documentation, study material related to the goal) are PRODUCTIU.
        Reply ONLY in this format: STATUS | short message in Catalan
        """
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        contingut = response["message"]["content"].strip()

        if "|" in contingut:
            estat, missatge = contingut.split("|", 1)
            estat = "PRODUCTIU" if "PRODUCTIU" in estat.upper() else "DISTRET"
            if estat == "DISTRET":
                paraula_brossa = (
                    titol_min.split("-")[-1].strip()
                    if "-" in titol_min
                    else titol_min.split()[0]
                )
                if (
                    len(paraula_brossa) > 3
                    and paraula_brossa not in subllista["llista_negra"]
                ):
                    memoria["categories"][categoria]["llista_negra"].append(paraula_brossa)
                    guardar_memoria(memoria)
                    print(f"\n [LLISTA NEGRA] Afegit '{paraula_brossa}' a '{categoria}'.")
            return estat, missatge.strip()

        return (
            ("PRODUCTIU", "S'accepta")
            if "PRODUCTIU" in contingut.upper()
            else ("DISTRET", "Distracció.")
        )
    except Exception as e:
        return "PRODUCTIU", f"Error de connexió: {e}"