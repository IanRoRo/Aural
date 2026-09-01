from ulls import AuralMonitor
from mans import (
    AVISAR, TANCAR_FINESTRA, SELECCIONAR_OBJECTIU_INICIAL,
    PREGUNTAR_TIPUS_APP, PREGUNTAR_SEGUENT_PAS, MOSTRAR_FINESTRA_OK,
    VALIDAR_CATEGORIA_IA, PREGUNTAR_CONFIRMACIO_APP,
    carregar_sessio, guardar_sessio, esborrar_sessio, PREGUNTAR_REPRENDRE_SESSIO,
)
from intel_ligencia import (
    carregar_memoria, determinar_categoria_ia, extreure_nom_app,
    registrar_app_manual, avaluar_amb_ia, guardar_feedback_usuari,
)
import time
import os
import csv
import json
import subprocess
import sys
import atexit
import signal

# =====================================================================
# GESTIÓ DE RUTES (compatibilitat amb Auto PY to Exe)
# =====================================================================
def ruta_recurs(nom_fitxer):
    """Retorna la ruta absoluta d'un RECURS ESTÀTIC (només lectura).
    En mode exe: apunta a sys._MEIPASS (carpeta temporal de PyInstaller).
    En mode script: apunta al directori del script.
    """
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

# =====================================================================
# CONSTANTS DE FITXERS (tots writables → ruta_dades_usuari)
# =====================================================================
FITXER_SESSIO = ruta_dades_usuari("session_state.json")
FITXER_ESTIL = ruta_dades_usuari("estat_felicitat.json")
FITXER_CSV = ruta_dades_usuari("registre_activitat.csv")
FITXER_FANTASMA = ruta_dades_usuari("estat_fantasma.json")
INTERVAL_GUARDAT = 6
_ULTIM_GUARDAT = 0

# =====================================================================
# VERIFICACIÓ I INSTAL·LACIÓ AUTOMÀTICA DE DEPENDÈNCIES (LLAMA 3.2)
# =====================================================================
def verificar_i_instal·lar_llama():
    print("\n" + "=" * 60)
    print("🔍 VERIFICANT DEPENDÈNCIES D'AURAL")
    print("=" * 60)
    
    print("\n[1/2] Verificant Ollama...")
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Ollama detectat: {result.stdout.strip()}")
        else:
            print("Ollama no està instal·lat o no funciona correctament")
            print("\n Obre el navegador per descarregar Ollama...")
            subprocess.Popen(["start", "https://ollama.com/download"])
            input("\n Prem ENTER quan tinguis Ollama instal·lat...")
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                print(" Error: Ollama no s'ha instal·lat correctament.")
                sys.exit(1)
            print(f" Ollama instal·lat: {result.stdout.strip()}")
    except FileNotFoundError:
        print(" Ollama no trobat al sistema")
        print("\n Obre el navegador per descarregar Ollama...")
        subprocess.Popen(["start", "https://ollama.com/download"])
        input("\n Prem ENTER quan tinguis Ollama instal·lat...")
    except Exception as e:
        print(f" Error verificant Ollama: {e}")
        sys.exit(1)
    
    print("\n[2/2] Verificant model llama3.2...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        models_disponibles = result.stdout.lower()
        if "llama3.2" in models_disponibles:
            print(" Model llama3.2 detectat")
        else:
            print("  Model llama3.2 no trobat")
            print("\n Descarregant llama3.2 (això pot trigar uns minuts)...")
            print("   Mida aproximada: ~2GB")
            try:
                proc = subprocess.Popen(
                    ["ollama", "pull", "llama3.2"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                for line in proc.stdout:
                    if line.strip():
                        print(f"   {line.strip()}")
                proc.wait()
                if proc.returncode == 0:
                    print("\n Model llama3.2 descarregat correctament!")
                else:
                    print("\n Error descarregant el model")
                    print("   Intenta executar manualment: ollama pull llama3.2")
                    sys.exit(1)
            except Exception as e:
                print(f"\n Error durant la descàrrega: {e}")
                print("   Intenta executar manualment: ollama pull llama3.2")
                sys.exit(1)
    except Exception as e:
        print(f" Error verificant models: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(" TOTES LES DEPENDÈNCIES ESTAN LLESTES")
    print("=" * 60 + "\n")
    time.sleep(2)

# =====================================================================
# LLANÇAMENT DEL FANTASMA (compatible amb mode .exe)
# =====================================================================
def llancar_fantasma(mascota=None, pomodoro_actiu=False, treball_min=25,
                     descans_min=5, resume=None):
    try:
        if getattr(sys, 'frozen', False):
            fantasma_exe = os.path.join(
                os.path.dirname(sys.executable), "fantasma.exe"
            )
            if not os.path.exists(fantasma_exe):
                print(f"[AVÍS] No s'ha trobat fantasma.exe a: {fantasma_exe}")
                return None
            comanda = [fantasma_exe]
        else:
            script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "fantasma.py"
            )
            comanda = [sys.executable, script]

        if mascota:
            comanda += ["--personatge", mascota]
        if pomodoro_actiu:
            comanda += ["--pomodoro", str(treball_min), str(descans_min)]
        if resume:
            fase, segons = resume
            comanda += ["--resume", str(fase), str(int(segons))]

        proces = subprocess.Popen(comanda)
        atexit.register(proces.terminate)
        return proces
    except Exception as e:
        print(f"[AVÍS] No s'ha pogut llançar el fantasma: {e}")
        return None

# =====================================================================
# SINCRONITZACIÓ AMB LA MASCOTA (felicitat visual)
# =====================================================================
def actualitzar_estat_felicitat(felicitat):
    try:
        dades = {"felicitat": max(0, min(100, int(felicitat)))}
        with open(FITXER_ESTIL, "w", encoding="utf-8") as f:
            json.dump(dades, f, ensure_ascii=False)
    except Exception as e:
        print(f"[AVÍS] No s'ha pogut actualitzar l'estat de felicitat: {e}")

# =====================================================================
# REGISTRE D'ACTIVITAT EN CSV
# =====================================================================
def guardar_a_csv(dades, estat, missatge_ia):
    existeix = os.path.exists(FITXER_CSV)
    try:
        with open(FITXER_CSV, mode="a", newline="", encoding="utf-8-sig") as f:
            escriptor = csv.writer(f, delimiter=",")
            if not existeix or os.path.getsize(FITXER_CSV) == 0:
                escriptor.writerow([
                    "Data", "Hora", "Finestra", "Actiu", "Estat IA", "Missatge IA"
                ])
            titol_neteit = str(dades[2]).replace("\r", "  ").replace("\n", "  ").strip()
            missatge_neteit = str(missatge_ia).replace("\r", "  ").replace("\n", "  ").strip()
            escriptor.writerow([
                dades[0], dades[1], titol_neteit, dades[3], estat, missatge_neteit
            ])
            f.flush()
    except Exception as e:
        print(f"[ERROR CSV]: {e}")

# =====================================================================
# ESTAT GLOBAL DE LA SESSIÓ (per guardar-lo en qualsevol moment)
# =====================================================================
ESTAT_SESSIO = {
    "objectiu": "",
    "categoria": "",
    "mode": "RECONEIXEMENT",
    "mascota": None,
    "felicitat": 100,
    "comptador_avisos": 0,
    "pomodoro": {
        "actiu": False,
        "fase": "treball",
        "segons_restants": 0,
        "treball_min": 25,
        "descans_min": 5,
    },
}

def _construir_estat_per_guardar(felicitat, comptador_avisos, mode,
                                  pomodoro_actiu, treball_min, descans_min):
    fase = "treball"
    segons = treball_min * 60 if pomodoro_actiu else 0
    try:
        if os.path.exists(FITXER_FANTASMA) and os.path.getsize(FITXER_FANTASMA) > 0:
            with open(FITXER_FANTASMA, "r", encoding="utf-8") as f:
                d = json.load(f)
            fase = d.get("fase", "treball")
            segons = int(d.get("segons_restants", segons))
    except Exception:
        pass
    return {
        "objectiu": ESTAT_SESSIO["objectiu"],
        "categoria": ESTAT_SESSIO["categoria"],
        "mode": mode,
        "mascota": ESTAT_SESSIO["mascota"],
        "felicitat": max(0, min(100, int(felicitat))),
        "comptador_avisos": int(comptador_avisos),
        "pomodoro": {
            "actiu": bool(pomodoro_actiu),
            "fase": fase,
            "segons_restants": max(0, int(segons)),
            "treball_min": int(treball_min),
            "descans_min": int(descans_min),
        },
    }

def _guardar_ara(felicitat, comptador_avisos, mode, pomodoro_actiu,
                 treball_min, descans_min):
    dades = _construir_estat_per_guardar(
        felicitat, comptador_avisos, mode, pomodoro_actiu, treball_min, descans_min
    )
    guardar_sessio(dades)

# =====================================================================
# PUNT D'ENTRADA PRINCIPAL
# =====================================================================
def main():
    global _ULTIM_GUARDAT
    
    verificar_i_instal·lar_llama()
    print("\n" + "=" * 60)
    print(" AURAL - Versió amb Llama 3.2")
    print("=" * 60)
    
    sessio_anterior = carregar_sessio()
    reprendre = False
    if sessio_anterior:
        reprendre = PREGUNTAR_REPRENDRE_SESSIO(sessio_anterior)

    if reprendre and sessio_anterior:
        objectiu = sessio_anterior["objectiu"]
        categoria = sessio_anterior["categoria"]
        mode_actual = sessio_anterior.get("mode", "GUARDIA")
        mascota_triada = sessio_anterior.get("mascota")
        felicitat = int(sessio_anterior.get("felicitat", 100))
        comptador_avisos = int(sessio_anterior.get("comptador_avisos", 0))
        pom = sessio_anterior.get("pomodoro", {})
        pomodoro_actiu = bool(pom.get("actiu", False))
        treball_min = int(pom.get("treball_min", 25))
        descans_min = int(pom.get("descans_min", 5))
        fase_reprise = pom.get("fase", "treball")
        segons_reprise = int(pom.get("segons_restants", treball_min * 60))

        ESTAT_SESSIO.update({
            "objectiu": objectiu,
            "categoria": categoria,
            "mode": mode_actual,
            "mascota": mascota_triada,
        })
        resume = (fase_reprise, segons_reprise) if pomodoro_actiu else None
        esborrar_sessio()
    else:
        if sessio_anterior:
            esborrar_sessio()
        (
            objectiu,
            mode_actual,
            categoria_guardada,
            mascota_triada,
            pomodoro_cfg,
        ) = SELECCIONAR_OBJECTIU_INICIAL()

        pomodoro_actiu, treball_min_str, descans_min_str = pomodoro_cfg
        try:
            treball_min = max(1, int(treball_min_str))
        except (TypeError, ValueError):
            treball_min = 25
        try:
            descans_min = max(1, int(descans_min_str))
        except (TypeError, ValueError):
            descans_min = 5

        if mode_actual == "GUARDIA" and categoria_guardada:
            categoria = categoria_guardada
        else:
            categoria_ia = determinar_categoria_ia(objectiu)
            categoria = VALIDAR_CATEGORIA_IA(objectiu, categoria_ia)
            if categoria != categoria_ia:
                guardar_feedback_usuari(objectiu, categoria)

        felicitat = 100
        comptador_avisos = 0
        resume = None
        ESTAT_SESSIO.update({
            "objectiu": objectiu,
            "categoria": categoria,
            "mode": mode_actual,
            "mascota": mascota_triada,
        })

    monitor = AuralMonitor()
    proces_fantasma = llancar_fantasma(
        mascota_triada, pomodoro_actiu, treball_min, descans_min, resume=resume
    )
    actualitzar_estat_felicitat(felicitat)

    print(f"\n[SISTEMA AURAL] Sessió iniciada.")
    print(f"📁 Perfil de treball: {categoria.upper()} | Mode: {mode_actual}")
    if pomodoro_actiu:
        print(f"🍅 Mode Pomodoro actiu: {treball_min} min treball / {descans_min} min descans")

    estat_final = {
        "felicitat": felicitat,
        "comptador_avisos": comptador_avisos,
        "mode": mode_actual,
    }

    def _neteja_final():
        try:
            _guardar_ara(
                estat_final["felicitat"],
                estat_final["comptador_avisos"],
                estat_final["mode"],
                pomodoro_actiu,
                treball_min,
                descans_min,
            )
            print("\n💾 Sessió guardada per si vols reprendre-la la propera vegada.")
        except Exception as e:
            print(f"[AVÍS] No s'ha pogut guardar l'estat final: {e}")

    atexit.register(_neteja_final)

    def _handler_sigint(sig, frame):
        print("\n[!] Interrupció detectada. Guardant sessió...")
        _neteja_final()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler_sigint)

    try:
        while True:
            try:
                dades = monitor.get_data()
                titol_finestra = dades[2]
                nom_app = extreure_nom_app(titol_finestra)

                if not nom_app:
                    time.sleep(3)
                    continue

                memoria = carregar_memoria()
                cat_data = memoria["categories"].get(
                    categoria, {"llista_blanca": [], "llista_negra": []}
                )

                if mode_actual == "RECONEIXEMENT":
                    if (
                        nom_app not in cat_data["llista_blanca"]
                        and nom_app not in cat_data["llista_negra"]
                    ):
                        print(f"\n S'ha obert una aplicació no guardada: '{nom_app}'")
                        estat_triat = PREGUNTAR_TIPUS_APP(nom_app, objectiu)
                        registrar_app_manual(categoria, nom_app, estat_triat)
                        guardar_a_csv(
                            dades, "CONFIGURAT",
                            f"L'usuari ha marcat '{nom_app}' com a {estat_triat}.",
                        )
                        if PREGUNTAR_SEGUENT_PAS() == "TREBALLAR":
                            mode_actual = "GUARDIA"
                            estat_final["mode"] = mode_actual
                            MOSTRAR_FINESTRA_OK(
                                f" Escut Guardià activat per a {categoria.upper()}!"
                            )
                    else:
                        print(
                            f"\r Escanejant... '{nom_app}' ja és coneguda. "
                            f"Obre una altra app per registrar-la.",
                            end="", flush=True,
                        )
                    time.sleep(3)
                    continue

                if nom_app in cat_data["llista_blanca"]:
                    estat, missatge_ia = "PRODUCTIU", f"Eina de confiança per a {categoria} ({nom_app})."
                elif nom_app in cat_data["llista_negra"]:
                    estat, missatge_ia = "DISTRET", f"Aplicació explícitament prohibida ({nom_app})."
                else:
                    estat_ia, missatge_ia_ia = avaluar_amb_ia(objectiu, titol_finestra)
                    print(
                        f"\n App desconeguda '{nom_app}': la IA suggereix {estat_ia}."
                    )
                    decisio = PREGUNTAR_CONFIRMACIO_APP(
                        nom_app, objectiu, estat_ia, missatge_ia_ia, timeout=25,
                    )
                    registrar_app_manual(categoria, nom_app, decisio)
                    if decisio == "PRODUCTIU":
                        estat = "PRODUCTIU"
                        missatge_ia = f"Confirmada per l'usuari com a productiva ({nom_app})."
                        guardar_a_csv(dades, "APRÈS", missatge_ia)
                    else:
                        estat = "DISTRET"
                        missatge_ia = f"Confirmada per l'usuari com a distracció ({nom_app})."
                        guardar_a_csv(dades, "APRÈS", missatge_ia)

                guardar_a_csv(dades, estat, missatge_ia)

                if estat == "PRODUCTIU":
                    comptador_avisos = 0
                    felicitat = min(100, felicitat + 2)
                elif estat == "DISTRET":
                    comptador_avisos += 1
                    felicitat = max(0, felicitat - 10)
                    print(f"\n[DISTRACTE] Avís crític: {comptador_avisos}/3")

                    if comptador_avisos == 1:
                        AVISAR(f"Avís: {missatge_ia}", segons=3)
                    elif comptador_avisos == 2:
                        AVISAR("ÚLTIM AVÍS abans del tancament coercitiu.", segons=4)
                    elif comptador_avisos >= 3:
                        print(f"[!] TANCANT FINESTRA PROHIBIDA: {titol_finestra}")
                        TANCAR_FINESTRA(titol_finestra)
                        AVISAR(
                            f"La finestra '{nom_app}' ha estat tancada de forma fulminant.",
                            segons=5,
                        )
                        comptador_avisos = 0

                estat_final["felicitat"] = felicitat
                estat_final["comptador_avisos"] = comptador_avisos
                estat_final["mode"] = mode_actual
                actualitzar_estat_felicitat(felicitat)

                _ULTIM_GUARDAT += 1
                if _ULTIM_GUARDAT >= INTERVAL_GUARDAT:
                    _ULTIM_GUARDAT = 0
                    try:
                        _guardar_ara(
                            felicitat, comptador_avisos, mode_actual,
                            pomodoro_actiu, treball_min, descans_min,
                        )
                    except Exception as e:
                        print(f"[AVÍS] Error en guardat periòdic: {e}")

                barra = "█" * (felicitat // 10) + "░" * (10 - felicitat // 10)
                print(
                    f"\rFELI: [{barra}] | Avisos: {comptador_avisos}/3 | "
                    f"Actual: {nom_app.upper()}",
                    end="", flush=True,
                )
                time.sleep(5)

            except Exception as e:
                print(f"\n[ERROR CRÍTIC BUCLE]: {e}")
                time.sleep(2)

    except KeyboardInterrupt:
        print("\n[!] Interrupció manual. Guardant sessió...")
    finally:
        try:
            _neteja_final()
        except Exception:
            pass

if __name__ == "__main__":
    main()