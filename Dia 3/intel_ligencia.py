import ollama
import json
import os

FITXER_MEMORIA = "memoria_aural.json"

def carregar_memoria():
    if os.path.exists(FITXER_MEMORIA):
        try:
            if os.path.getsize(FITXER_MEMORIA) == 0: return {"categories": {}, "correccions_ia": {}}
            with open(FITXER_MEMORIA, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                if "categories" not in memoria: memoria["categories"] = {}
                if "correccions_ia" not in memoria: memoria["correccions_ia"] = {}
                return memoria
        except Exception:
            return {"categories": {}, "correccions_ia": {}}
    return {"categories": {}, "correccions_ia": {}}

def guardar_memoria(memoria):
    with open(FITXER_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)

def assegurar_ollama():
    try: ollama.list()
    except Exception: print("⚠️ ERROR: Ollama no està actiu.")

def determinar_categoria_ia(objectiu_usuari):
    """Determina la categoria demanant a la IA que en generi una de personalitzada o mirant l'historial."""
    objectiu_min = objectiu_usuari.lower().strip()
    memoria = carregar_memoria()

    # 🧠 Historial de feedback (Evita tornar a preguntar el mateix)
    if objectiu_min in memoria.get("correccions_ia", {}):
        return memoria["correccions_ia"][objectiu_min]

    # 🤖 La IA inventa/proposa una categoria lògica a mida
    assegurar_ollama()
    try:
        prompt = f"""
        Analyze this user productivity goal: "{objectiu_usuari}"
        Generate a single-word generic category/profile name for it (lowercase, no spaces, no punctuation, alphanumeric only).
        Examples: python, blender, english, accounting, admin, gym.
        Reply ONLY with that single word.
        """
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0})
        cat = response['message']['content'].strip().lower()
        # Netegem espais o caràcters estranys per seguretat del JSON
        cat_neta = "".join(c for c in cat if c.isalnum() or c in ["-", "_"])
        return cat_neta if cat_neta else "general"
    except Exception:
        return "general"
    
def guardar_feedback_usuari(objectiu_usuari, categoria_correcta):
    """Guarda la correcció de l'usuari al JSON perquè la IA no torni a fallar."""
    memoria = carregar_memoria()
    objectiu_min = objectiu_usuari.lower().strip()
    
    memoria["correccions_ia"][objectiu_min] = categoria_correcta
    guardar_memoria(memoria)
    print(f"💾 [FEEDBACK] S'ha guardat que '{objectiu_min}' correspon a la categoria '{categoria_correcta}'.")

def extreure_nom_app(titol_finestra):
    """
    Neteja el títol de la finestra de forma 100% dinàmica.
    Si és un navegador, extreu automàticament el nom de la web/servei 
    sense necessitat de tenir una llista fixa a mà.
    """
    if not titol_finestra or titol_finestra.strip() in ["", "Escriptori", "Desconegut"]:
        return None
    
    titol_min = titol_finestra.lower()
    
    # 🌐 DETECTOR AUTOMÀTIC DE NAVEGADORS (Chrome, Edge, Firefox, Brave)
    navegadors = ["google chrome", "microsoft edge", "firefox", "brave"]
    if any(nav in titol_min for nav in navegadors):
        # Els navegadors solen estructurar el títol així: "Nom de la Pàgina - Nom del lloc - Google Chrome"
        # Per tant, si separem per guions ("-"), podem extreure les parts de la web.
        parts = [p.strip() for p in titol_min.split("-") if p.strip()]
        
        if len(parts) >= 3:
            # Cas típic: ["Pestanya actual", "Nom de la Web", "Google Chrome"]
            # Ens quedem amb el nom de la web (la penúltima part)
            nom_web = parts[-2]
            # Si el nom de la web és el mateix navegador (error de lectura), agafem la primera
            if any(nav in nom_web for nav in navegadors):
                nom_web = parts[0]
            return f"web: {nom_web}"
        elif len(parts) == 2:
            # Cas curt: ["Nom de la Web", "Google Chrome"]
            return f"web: {parts[0]}"
            
        return "web: navegació general"

    # 🖥️ SI ÉS UN PROGRAMA EXECUTABLE (VS Code, Discord, Spotify, etc.)
    # Ens quedem amb la part de l'executable del final o l'inici
    paraula = titol_min.split("-")[-1].strip() if "-" in titol_min else titol_min.split()[0]
    return paraula if len(paraula) >= 3 else titol_min[:12]

def registrar_app_manual(categoria, nom_app, estat):
    """Guarda l'app directament a la llista corresponent del JSON segons el que ha triat l'usuari."""
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
    """Control de recursos: Avalua primer en local (JSON) i només usa la IA en casos crítics (com Gemini xats)."""
    if not titol_finestra or titol_finestra.strip() == "":
        return "PRODUCTIU", "Mirant l'horitzó..."

    titol_min = titol_finestra.lower()
    categoria = determinar_categoria_ia(objectiu_usuari)
    memoria = carregar_memoria()

    # Si la categoria no existeix al JSON, la creem amb els jocs bàsics a la llista negra
    jocs_basics = ["minecraft", "fortnite", "roblox", "league of legends", "twitch", "netflix", "gta"]
    if categoria not in memoria["categories"]:
        memoria["categories"][categoria] = {"llista_blanca": [], "llista_negra": jocs_basics}
        guardar_memoria(memoria)

    subllista = memoria["categories"][categoria]

    # 🛑 SEGURETAT 1: Si conté qualsevol paraula de la llista negra de la categoria (0% recursos)
    if any(brossa in titol_min for brossa in subllista["llista_negra"]):
        return "DISTRET", f"Bloquejat per llista negra de la categoria [{categoria}]."

    # 🟢 SEGURETAT 2: Si està a la llista blanca i NO és un navegador (0% recursos)
    # Deixem fora els navegadors d'aquest filtre automàtic per poder analitzar els xats de Gemini
    if any(bona in titol_min for bona in subllista["llista_blanca"]) and not any(nav in titol_min for nav in ["chrome", "edge", "firefox", "brave"]):
        return "PRODUCTIU", "Eina de software validada per a aquest context."

    # 🤖 SEGURETAT 3: EL FILTRE INTEL·LIGENT (Només s'activa per a pàgines web / Gemini / dubtes)
    assegurar_ollama()
    try:
        prompt = f"""
        You are a strict monitor for the category: "{categoria}".
        USER GOAL: "{objectiu_usuari}"
        CURRENT WINDOW: "{titol_finestra}"
        
        CRITERIA:
        - If the window is Gemini/ChatGPT, read the title carefully. If the user is chatting about video games, movies, entertainment or general slacking, it is DISTRET. If it's about coding/learning, it is PRODUCTIU.
        - Any video game (Fortnite, Minecraft, etc.) or social media is strictly DISTRET.
        
        Reply ONLY in this format: STATUS | short message in Catalan
        """

        response = ollama.chat(
            model='llama3.2', 
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0}
        )
        
        contingut = response['message']['content'].strip()
        
        if "|" in contingut:
            estat, missatge = contingut.split("|", 1)
            estat = "PRODUCTIU" if "PRODUCTIU" in estat.upper() else "DISTRET"
            
            # Si la IA caça una distracció nova (com Fortnite), l'afegeix a la llista negra d'aquesta categoria
            if estat == "DISTRET":
                paraula_brossa = titol_min.split("-")[-1].strip() if "-" in titol_min else titol_min.split()[0]
                if len(paraula_brossa) > 3 and paraula_brossa not in subllista["llista_negra"]:
                    memoria["categories"][categoria]["llista_negra"].append(paraula_brossa)
                    guardar_memoria(memoria)
                    print(f"\n🛑 [LLISTA NEGRA] S'ha afegit '{paraula_brossa}' a la categoria '{categoria}'.")

            return estat, missatge.strip()
        
        return ("PRODUCTIU", "S'accepta") if "PRODUCTIU" in contingut.upper() else ("DISTRET", "Distracció.")

    except Exception as e:
        return "PRODUCTIU", f"Error de connexió: {e}"
    
