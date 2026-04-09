from ulls import AuralMonitor
from mans import AVISAR, TANCAR_FINESTRA, BLOQUEJAR_INICI
import time

DISTRACCIONS = ["youtube", "netflix", "instagram", "facebook", "twitch", "reddit", "spotify","discord"]
TREBALL = ["visual studio code", "stackoverflow", "docs", "arxiv", "canvas", "viquipèdia", "github", "aural","gemini"]

def avaluar_activitat(titol_finestra):
    titol = titol_finestra.lower()
    for paraula in DISTRACCIONS:
        if paraula in titol: return "DISTRET"
    for paraula in TREBALL:
        if paraula in titol: return "PRODUCTIU"
    return "NEUTRE"

def main():
    objectiu = BLOQUEJAR_INICI()
    felicitat = 100
    punts_productivitat = 0  # Nou comptador acumulat
    avisos_restants = 3
    monitor = AuralMonitor()

    try:
        while True:
            dades = monitor.get_data()
            titol_finestra = dades[2]
            esta_actiu = dades[3]
            estat = avaluar_activitat(titol_finestra)

            # --- GESTIÓ DE PUNTS I FELICITAT ---
            if estat == "PRODUCTIU" and esta_actiu == "SI":
                punts_productivitat += 5
                if felicitat < 100: felicitat += 1
            elif estat == "DISTRET":
                punts_productivitat -= 10
                felicitat -= 10
            
            # --- LÒGICA DE BURN OUT (Basada en punts, no en felicitat) ---
            if punts_productivitat > 1500: # Exemple: portar molta estona productiva
                temps_actual = time.time()
                AVISAR("⚠️ ALERTA DE BURNOUT: Portes massa estona rendint al màxim.\n"
                       "La teva ment necessita 5 minuts de descans real.\n"
                       "Aural t'ordena que t'allunyis de la pantalla.")
                ultim_avis_burnout = temps_actual
                print("⚠️ Aural: Portes un ritme excel·lent, però vigila el burnout. Descansa 5 minuts.")
                # Opcionalment, podem fer que els punts baixin una mica al descansar

            # --- LÒGICA DE DISTRACCIONS AL 100% DE FELICITAT ---
            if estat == "DISTRET":
                if felicitat >= 90:
                    # Advertència suau sense tancar res
                    AVISAR(f"Vigila... m'has dit que faries '{objectiu}'. No et despistis ara.")
                
                # --- FRANGES DE CÀSTIG (Resta de franges) ---
                elif 50 <= felicitat < 90:
                    AVISAR("T'he avisat. Tancant distracció.")
                    TANCAR_FINESTRA()
                
                elif 30 <= felicitat < 50:
                    if avisos_restants > 0:
                        avisos_restants -= 1
                        AVISAR(f"Para ja. Et queden {avisos_restants} avisos.")
                    else:
                        TANCAR_FINESTRA()
                
                elif felicitat < 30:
                    TANCAR_FINESTRA() # Hostilitat màxima

            # Barra visual per la terminal
            barra_p = "PROD: " + "█" * (min(punts_productivitat // 50, 10))
            barra_f = "FELI: " + "█" * (felicitat // 10)
            print(f"\n{barra_p} ({punts_productivitat} pts) | {barra_f} ({felicitat}%)")
            
            time.sleep(5) # Pas 1.1
            
    except KeyboardInterrupt:
        print("Sessió finalitzada.")

if __name__ == "__main__":
    main()
