"""
intel_ligencia_lite.py
Versió de AURAL sense dependència d'IA local.
"""
import json
import os
import unicodedata
import sys

def ruta_dades_usuari(nom_fitxer):
    if getattr(sys, 'frozen', False):
        appdata_dir = os.path.join(os.getenv('APPDATA'), 'Aural')
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, nom_fitxer)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), nom_fitxer)

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

def normalitzar_nom_perfil(text):
    if not text:
        return "general"
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = text.replace(" ", "_")
    text = "".join(c for c in text if c.isalnum() or c in "-_")
    return text[:30] if text else "general"

def obtenir_o_crear_perfil(objectiu_usuari):
    nom_perfil = normalitzar_nom_perfil(objectiu_usuari)
    memoria = carregar_memoria()
    distraccions_basiques = [
        "minecraft", "fortnite", "roblox", "league of legends",
        "twitch", "netflix", "gta", "youtube", "tiktok", "instagram",
        "facebook", "twitter", "reddit",
    ]
    if nom_perfil not in memoria["categories"]:
        memoria["categories"][nom_perfil] = {
            "llista_blanca": [],
            "llista_negra": list(distraccions_basiques),
        }
        guardar_memoria(memoria)
        print(f"\n📁 [LITE] Creat perfil nou: '{nom_perfil}'")
    else:
        print(f"\n📁 [LITE] Perfil existent carregat: '{nom_perfil}'")
    return nom_perfil

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
        print(f"✅ [LITE] '{nom_app}' afegida a la llista blanca de '{categoria}'.")
    elif estat == "DISTRET" and nom_app not in subllista["llista_negra"]:
        subllista["llista_negra"].append(nom_app)
        print(f" [LITE] '{nom_app}' afegida a la llista negra de '{categoria}'.")
    guardar_memoria(memoria)

def avaluar_app_coneguda(categoria, nom_app):
    memoria = carregar_memoria()
    cat_data = memoria["categories"].get(categoria, {"llista_blanca": [], "llista_negra": []})
    if nom_app in cat_data["llista_blanca"]:
        return "PRODUCTIU", f"Eina productiva coneguda per a {categoria} ({nom_app})."
    if nom_app in cat_data["llista_negra"]:
        return "DISTRET", f"Aplicació prohibida per al perfil {categoria} ({nom_app})."
    return None, None