from ulls import AuralMonitor
from mans import AVISAR, TANCAR_FINESTRA, SELECCIONAR_OBJECTIU_INICIAL, PREGUNTAR_TIPUS_APP, PREGUNTAR_SEGUENT_PAS, MOSTRAR_FINESTRA_OK, VALIDAR_CATEGORIA_IA
from intel_ligencia import carregar_memoria, determinar_categoria_ia, extreure_nom_app, registrar_app_manual, avaluar_amb_ia, guardar_feedback_usuari
import time
import os
import csv

def guardar_a_csv(dades, estat, missatge_ia):
    fitxer_nom = "registre_activitat.csv"
    existeix = os.path.exists(fitxer_nom)
    try:
        with open(fitxer_nom, mode="a", newline="", encoding="utf-8-sig") as f:
            escriptor = csv.writer(f, delimiter=",")
            if not existeix or os.path.getsize(fitxer_nom) == 0:
                escriptor.writerow(["Data", "Hora", "Finestra", "Actiu", "Estat IA", "Missatge IA"])
            titol_neteit = str(dades[2]).replace("\r", "").replace("\n", "").strip()
            missatge_neteit = str(missatge_ia).replace("\r", "").replace("\n", "").strip()
            escriptor.writerow([dades[0], dades[1], titol_neteit, dades[3], estat, missatge_neteit])
            f.flush()
    except Exception as e:
        print(f"[ERROR CSV]: {e}")

def main():
    # 1. Obrim el menú complet (Retorna l'objectiu, el mode i si s'ha triat perfil existent)
    objectiu, mode_actual, categoria_guardada = SELECCIONAR_OBJECTIU_INICIAL()
    
    # Si entrem directe per un perfil vell, saltem la IA. Si és un mode nou, usem IA + Feedback
    if mode_actual == "GUARDIA" and categoria_guardada:
        categoria = categoria_guardada
    else:
        # 🤖 El sistema mira el JSON i, si és nou, demana classificació a Ollama
        categoria_ia = determinar_categoria_ia(objectiu)
        
        # 🛠️ Mostra la finestra per si l'usuari vol corregir la IA (Ex: Python -> Programar i no Estudiar)
        categoria = VALIDAR_CATEGORIA_IA(objectiu, categoria_ia)
        
        # 💾 Si l'usuari ha corregit la IA, guardem el feedback perquè aprengui per a sempre
        if categoria != categoria_ia:
            guardar_feedback_usuari(objectiu, categoria)
    
    monitor = AuralMonitor()
    felicitat = 100
    comptador_avisos = 0 
    
    print(f"\n[SISTEMA AURAL] Sessió iniciada.")
    print(f"📁 Perfil de treball: {categoria.upper()} | Mode inicial: {mode_actual}")

    while True:
        try:
            dades = monitor.get_data()
            titol_finestra = dades[2]
            
            # Extreu el nom dinàmic de l'app o el subdomini (Ex: "web: google gemini", "web: instagram")
            nom_app = extreure_nom_app(titol_finestra)
            
            if not nom_app:
                time.sleep(3)
                continue

            memoria = carregar_memoria()
            cat_data = memoria["categories"].get(categoria, {"llista_blanca": [], "llista_negra": []})
            
            # --- FLUX A: MODE RONDA DE RECONEIXEMENT (Només perfils nous o calibratges) ---
            if mode_actual == "RECONEIXEMENT":
                if nom_app not in cat_data["llista_blanca"] and nom_app not in cat_data["llista_negra"]:
                    print(f"\n✨ S'ha obert una aplicació no guardada: '{nom_app}'")
                    
                    estat_triat = PREGUNTAR_TIPUS_APP(nom_app, objectiu)
                    registrar_app_manual(categoria, nom_app, estat_triat)
                    guardar_a_csv(dades, "CONFIGURAT", f"L'usuari ha marcat '{nom_app}' com a {estat_triat}.")
                    
                    # Preguntem si vol seguir registrant aplicacions o activar l'escut
                    if PREGUNTAR_SEGUENT_PAS() == "TREBALLAR":
                        mode_actual = "GUARDIA"
                        MOSTRAR_FINESTRA_OK(f"🛡️ Escut Guardià activat per a {categoria.upper()}!")
                else:
                    print(f"\r🔍 Escanejant... '{nom_app}' ja és coneguda. Obre una altra app per registrar-la.", end="", flush=True)
                
                time.sleep(3)
                continue

            # --- FLUX B: MODE GUARDIÀ DIRECTE ACTIU ---
            if nom_app in cat_data["llista_blanca"]:
                estat, missatge_ia = "PRODUCTIU", f"Eina de confiança per a {categoria} ({nom_app})."
            elif nom_app in cat_data["llista_negra"]:
                estat, missatge_ia = "DISTRET", f"Aplicació explícitament prohibida pel context ({nom_app})."
            else:
                # Si obre una cosa nova sobre la marxa que no és al JSON, s'avalua dinàmicament
                estat, missatge_ia = avaluar_amb_ia(objectiu, titol_finestra)

            guardar_a_csv(dades, estat, missatge_ia)
            
            # Lògica i penalitzacions del sistema d'avisos executius
            if estat == "PRODUCTIU":
                comptador_avisos = 0
                felicitat = min(100, felicitat + 2)
            elif estat == "DISTRET":
                comptador_avisos += 1
                felicitat -= 10
                print(f"\n[DISTRACTE] Avís crític: {comptador_avisos}/3")

                if comptador_avisos == 1:
                    AVISAR(f"Avís: {missatge_ia}", segons=3)
                elif comptador_avisos == 2:
                    AVISAR(f"ÚLTIM AVÍS abans del tancament coercitiu.", segons=4)
                elif comptador_avisos >= 3:
                    print(f"[!] TANCANT FINESTRA PROHIBIDA: {titol_finestra}")
                    TANCAR_FINESTRA(titol_finestra)
                    AVISAR(f"La finestra '{nom_app}' ha estat tancada de forma fulminant.", segons=5)
                    comptador_avisos = 0
            
            # Barra visual de rendiment de la sessió actual
            barra = "█" * (felicitat // 10) + "░" * (10 - felicitat // 10)
            print(f"\rFELI: [{barra}] | Avisos: {comptador_avisos}/3 | Actual: {nom_app.upper()}", end="", flush=True)
            time.sleep(5)

        except Exception as e:
            print(f"\n[ERROR CRÍTIC BUCILE]: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()