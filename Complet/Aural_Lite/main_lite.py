"""
main_lite.py
Punt d'entrada de AURAL LITE (versió sense IA local).
Manté: mascota, Pomodoro, avisos, felicitat, persistència de sessió.
Elimina: Llama 3.2, Ollama, classificació automàtica per IA.
"""
from ulls import AuralMonitor
from mans_lite import (
    AVISAR, TANCAR_FINESTRA, SELECCIONAR_OBJECTIU_INICIAL,
    PREGUNTAR_SI_ES_DISTRACTIVA, PREGUNTAR_SEGUENT_PAS, MOSTRAR_FINESTRA_OK,
    carregar_sessio, guardar_sessio, esborrar_sessio, PREGUNTAR_REPRENDRE_SESSIO,
)
from intel_ligencia_lite import (
    carregar_memoria, obtenir_o_crear_perfil, extreure_nom_app,
    registrar_app_manual, avaluar_app_coneguda,
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
# GESTIÓ DE RUTES 
# =====================================================================
def ruta_dades_usuari(nom_fitxer):
    """Retorna la ruta absoluta a AppData\Roaming\Aural en modo .exe"""
    if getattr(sys, 'frozen', False):
        appdata_dir = os.path.join(os.getenv('APPDATA'), 'Aural')
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, nom_fitxer)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), nom_fitxer)

FITXER_ESTIL = ruta_dades_usuari("estat_felicitat.json")
FITXER_CSV = ruta_dades_usuari("registre_activitat_lite.csv")
FITXER_FANTASMA = ruta_dades_usuari("estat_fantasma.json")
INTERVAL_GUARDAT = 6
_ULTIM_GUARDAT = 0

# =====================================================================
# LLANÇAMENT DEL FANTASMA (Corregido para modo .exe)
# =====================================================================
def llancar_fantasma(mascota=None, pomodoro_actiu=False, treball_min=25,
                     descans_min=5, resume=None):
    try:
        if getattr(sys, 'frozen', False):
            # MODE EXE: busca fantasma.exe al lado del ejecutable principal
            fantasma_exe = os.path.join(os.path.dirname(sys.executable), "fantasma.exe")
            if not os.path.exists(fantasma_exe):
                print(f"[AVÍS] No s'ha trobat fantasma.exe a: {fantasma_exe}")
                return None
            comanda = [fantasma_exe]
        else:
            # MODE DESENVOLUPAMENT
            script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fantasma.py")
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

def actualitzar_estat_felicitat(felicitat):
    try:
        dades = {"felicitat": max(0, min(100, int(felicitat)))}
        with open(FITXER_ESTIL, "w", encoding="utf-8") as f:
            json.dump(dades, f, ensure_ascii=False)
    except Exception as e:
        print(f"[AVÍS] No s'ha pogut actualitzar l'estat de felicitat: {e}")

def guardar_a_csv(dades, estat, missatge):
    """Guarda al CSV propi de Aural Lite (separat del principal)."""
    # ✅ CORREGIT: Usa FITXER_CSV en lloc de hardcodejar el nom
    existeix = os.path.exists(FITXER_CSV)
    try:
        with open(FITXER_CSV, mode="a", newline="", encoding="utf-8-sig") as f:
            escriptor = csv.writer(f, delimiter=",")
            if not existeix or os.path.getsize(FITXER_CSV) == 0:
                escriptor.writerow(["Data", "Hora", "Finestra", "Actiu", "Estat", "Missatge"])
            titol_neteit = str(dades[2]).replace("\r", "  ").replace("\n", "  ").strip()
            missatge_neteit = str(missatge).replace("\r", "  ").replace("\n", "  ").strip()
            escriptor.writerow([dades[0], dades[1], titol_neteit, dades[3], estat, missatge_neteit])
            f.flush()
    except Exception as e:
        print(f"[ERROR CSV LITE]: {e}")

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
        # ✅ CORREGIT: Usa FITXER_FANTASMA (ja és ruta absoluta)
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

def main():
    global _ULTIM_GUARDAT

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

        # 🎯 EN AURAL LITE: el perfil es crea directament a partir de l'objectiu
        if mode_actual == "GUARDIA" and categoria_guardada:
            categoria = categoria_guardada
        else:
            categoria = obtenir_o_crear_perfil(objectiu)

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

    print(f"\n[SISTEMA AURAL LITE] Sessió iniciada (sense IA).")
    print(f"📁 Perfil de treball: {categoria.upper()} | Mode: {mode_actual}")
    if pomodoro_actiu:
        print(f"🍅 Pomodoro: {treball_min} min treball / {descans_min} min descans")

    # ------------------------------------------------------------------
    # Neteja en sortir
    # ------------------------------------------------------------------
    estat_final = {"felicitat": felicitat, "comptador_avisos": comptador_avisos,
                   "mode": mode_actual}

    def _neteja_final():
        try:
            _guardar_ara(
                estat_final["felicitat"],
                estat_final["comptador_avisos"],
                estat_final["mode"],
                pomodoro_actiu, treball_min, descans_min,
            )
            print("\n💾 [LITE] Sessió guardada per si vols reprendre-la.")
        except Exception as e:
            print(f"[AVÍS] No s'ha pogut guardar l'estat final: {e}")

    atexit.register(_neteja_final)

    def _handler_sigint(sig, frame):
        print("\n[!] Interrupció detectada. Guardant sessió Lite...")
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

                # -----------------------------------------------
                # AVALUACIÓ PER REGLES (sense IA)
                # -----------------------------------------------
                estat, missatge = avaluar_app_coneguda(categoria, nom_app)

                if estat is None:
                    # 🎯 APP DESCONEGUDA → PREGUNTA DIRECTA A L'USUARI
                    print(f"\n✨ [LITE] App no classificada: '{nom_app}'")
                    decisio = PREGUNTAR_SI_ES_DISTRACTIVA(nom_app, objectiu)
                    registrar_app_manual(categoria, nom_app, decisio)

                    if decisio == "PRODUCTIU":
                        estat = "PRODUCTIU"
                        missatge = f"Marcada per l'usuari com a productiva ({nom_app})."
                    else:
                        estat = "DISTRET"
                        missatge = f"Marcada per l'usuari com a distracció ({nom_app})."

                    guardar_a_csv(dades, "APRÈS", missatge)
                else:
                    guardar_a_csv(dades, estat, missatge)

                # -----------------------------------------------
                # Lògica d'avisos i felicitat
                # -----------------------------------------------
                if estat == "PRODUCTIU":
                    comptador_avisos = 0
                    felicitat = min(100, felicitat + 2)
                elif estat == "DISTRET":
                    comptador_avisos += 1
                    felicitat = max(0, felicitat - 10)
                    print(f"\n[DISTRACTE] Avís crític: {comptador_avisos}/3")

                    if comptador_avisos == 1:
                        AVISAR(f"Avís: {missatge}", segons=3)
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

                # Guardat periòdic
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
                    f"\r[LITE] FELI: [{barra}] | Avisos: {comptador_avisos}/3 | "
                    f"Actual: {nom_app.upper()}",
                    end="", flush=True,
                )
                time.sleep(5)

            except Exception as e:
                print(f"\n[ERROR CRÍTIC BUCLE LITE]: {e}")
                time.sleep(2)

    except KeyboardInterrupt:
        print("\n[!] Interrupció manual. Guardant sessió Lite...")
    finally:
        try:
            _neteja_final()
        except Exception:
            pass

if __name__ == "__main__":
    main()