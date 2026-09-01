"""
fantasma.py
Personatge flotant que es queda sempre visible a la cantonada inferior
dreta de la pantalla mentre treballes amb AURAL. N'hi ha 20 de diferents,
cadascun amb la seva animació i personalitat pròpia.
Es llança com a PROCÉS INDEPENDENT des de main.py (subprocess).

Ús manual:
  python fantasma.py                                     -> personatge aleatori
  python fantasma.py --personatge 3                      -> personatge número 3
  python fantasma.py --personatge "Robot"                -> personatge pel nom
  python fantasma.py --pomodoro 25 5                     -> mode Pomodoro
  python fantasma.py --resume treball 1245               -> reprendre Pomodoro
                                                           (fase + segons restants)
"""
import tkinter as tk
import random
import sys
import math
import argparse
import os
import json
import time

def ruta_dades_usuari(nom_fitxer):
    """Retorna la ruta absoluta d'un FITXER WRITABLE (dades d'usuari).
    En mode exe: apunta a %APPDATA%\Aural per evitar permisos d'administrador.
    En mode script: apunta al directori del script.
    """
    if getattr(sys, 'frozen', False):
        # MODE EXE: Usar AppData\Roaming\Aural
        appdata_dir = os.path.join(os.getenv('APPDATA'), 'Aural')
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, nom_fitxer)
    else:
        # MODE DESENVOLUPAMENT: Carpeta local del projecte
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nom_fitxer)

AMPLADA = 130
ALCADA = 178

FITXER_ESTIL = ruta_dades_usuari("estat_felicitat.json")

DESCANS_MISSATGES = [
    "Aixeca't i estira una mica les cames ",
    "Beu un got d'aigua, t'ho has guanyat ",
    "Fes 10 flexions o esquats ràpids ",
    "Menja alguna cosa lleugera ",
    "Mira lluny un moment, descansa la vista ",
    "Respira profundament 3 vegades ",
    "Obre la finestra i agafa aire fresc ",
    "O, si vols... queda't tota l'estona mirant la pantalla ",
]

PERSONATGES = [
    {"nom": "Fantasma", "emoji": "👻", "emoji_feliç": "🎉", "emoji_trist": "😰",
     "animacio": "flicker",
     "pressio": ["Et vigilo 👻", "Bu! Torna a la feina.", "Un fantasma sap quan et distraus...", "Tic-tac, tic-tac ⏰"],
     "decepcio": ["Em decepciones... 👻", "Estàs deixant morir la teva ratxa...", "Bu... què ha passat? 😰"],
     "que_vols": ["Què vols? 👻", "Bu! Digues...", "Sí? T'escolto..."],
     "enfadat": "Deixa'm tranquil i posa't a treballar. 😤"},
    {"nom": "Robot", "emoji": "🤖", "emoji_feliç": "⚡", "emoji_trist": "⚠️",
     "animacio": "tremolor",
     "pressio": ["ALERTA: productivitat baixant.", "Bip bip. Torna a la tasca.", "Detecto distracció, humà."],
     "decepcio": ["ERROR: rendiment per sota del mínim.", "Els meus sensors detecten fracàs.", "Bip... estàs fallant, humà."],
     "que_vols": ["PROCESSANT... què vols?", "Bip? Introdueix ordre."],
     "enfadat": "ERROR 404: paciència no trobada. Treballa."},
    {"nom": "Gat", "emoji": "🐱", "emoji_feliç": "😺", "emoji_trist": "😿",
     "animacio": "balanceig",
     "pressio": ["Miau... no hauries d'estar treballant?", "T'observo des d'aquí dalt.", "El meu gat sisè sentit diu que et distraus."],
     "decepcio": ["Miau... estic decebut 😿", "Ni els gats perdem tant el temps.", "Ronroneig trist..."],
     "que_vols": ["Miau? Què vols?", "Ronroneig interrogatiu..."],
     "enfadat": "Miaaau (traducció: deixa'm i treballa). 😾"},
    {"nom": "Calavera", "emoji": "💀", "emoji_feliç": "🎃", "emoji_trist": "☠️",
     "animacio": "pols",
     "pressio": ["El temps passa igualment...", "Ossos inquiets per la teva procrastinació.", "🦴 tic tac tic tac"],
     "decepcio": ["La teva vida s'escola... ☠️", "Ni els morts perdem tant el temps.", "M'avorreixes, mortal."],
     "que_vols": ["Digues, mortal.", "Què desitges?"],
     "enfadat": "Torna a la feina abans que sigui tard. 💀"},
    {"nom": "Extraterrestre", "emoji": "👽", "emoji_feliç": "🛸", "emoji_trist": "🌠",
     "animacio": "gir",
     "pressio": ["A casa fem servir aquest temps millor.", "T'estic escanejant... distracció detectada.", "👽 senyal de baixa concentració."],
     "decepcio": ["La teva espècie és decebedora...", "Informaré al planeta del teu fracàs.", "🌠 senyal de rendició."],
     "que_vols": ["Digues, terrícola.", "Quin és el teu missatge?"],
     "enfadat": "Torno a la meva nau. Treballa. 🛸"},
    {"nom": "Flama", "emoji": "🔥", "emoji_feliç": "🌟", "emoji_trist": "💨",
     "animacio": "pols",
     "pressio": ["No deixis que s'apagui la flama del teu objectiu.", "Estic cremant d'impaciència.", "🔥 la teva ratxa perilla."],
     "decepcio": ["M'estàs apagant... 💨", "La flama es fa petita per la teva mandra.", "Quasi bé ets cendra."],
     "que_vols": ["Digues abans que m'apagui.", "Crema, digues."],
     "enfadat": "M'apagues la motivació. Torna-hi. 🔥"},
    {"nom": "Rellotge", "emoji": "⏰", "emoji_feliç": "⌚", "emoji_trist": "🕰️",
     "animacio": "gir",
     "pressio": ["El temps no torna, eh.", "Tic tac... tic tac...", "Cada minut compta."],
     "decepcio": ["Les hores passen... i tu res. 🕰️", "El rellotge fa tristesa amb tu.", "Tic... tac... fracàs."],
     "que_vols": ["Ring! Digues ràpid.", "El temps corre, parla."],
     "enfadat": "RING RING: torna a la feina! ⏰"},
    {"nom": "Cafè", "emoji": "☕", "emoji_feliç": "🍵", "emoji_trist": "🥤",
     "animacio": "surar",
     "pressio": ["Encara calent, com la teva excusa per no treballar.", "Un cafè et donaria l'empenta que et falta.", "☕ Necessites reactivar-te."],
     "decepcio": ["M'he refredat del tot per tu... 🥤", "Ni la cafeïna et desperta.", "Tassa buida, com la teva productivitat."],
     "que_vols": ["Digues abans que em refredi.", "Sí? Xerra."],
     "enfadat": "M'he refredat esperant. Treballa. ☕"},
    {"nom": "Bomba", "emoji": "💣", "emoji_feliç": "🎆", "emoji_trist": "🧨",
     "animacio": "tremolor",
     "pressio": ["Tic tic tic... la procrastinació explota.", "Estic a punt de petar de paciència.", "💣 temps límit s'escurça."],
     "decepcio": ["Petaré de decepció... 🧨", "La metxa es consumeix en va.", "Boom... de frustració."],
     "que_vols": ["Ràpid, què vols?!", "Parla abans que exploti."],
     "enfadat": "BOOM. Torna a treballar. 💥"},
    {"nom": "Drac", "emoji": "🐉", "emoji_feliç": "🐲", "emoji_trist": "🦖",
     "animacio": "balanceig",
     "pressio": ["Un drac no perd el temps... i tu?", "Guardo el teu objectiu com un tresor. No el descuidis.", "🐉 la meva paciència també crema."],
     "decepcio": ["El meu foc s'apaga amb la teva mandra.", "Ni els dracs perden tant el temps... 🦖", "Deceps el tresor que guardo."],
     "que_vols": ["Parla, aventurer.", "Digues el teu desig."],
     "enfadat": "Torna a la teva missió. 🐉"},
    {"nom": "Diable", "emoji": "😈", "emoji_feliç": "👿", "emoji_trist": "😇",
     "animacio": "pols",
     "pressio": ["Deixa't temptar... per acabar la feina.", "La procrastinació és el meu pecat preferit... el teu no hauria de ser-ho.", "😈 et veig venir."],
     "decepcio": ["Fins i tot jo estic decebut... 😇", "Ets més pecador del que pensava, però de mandra.", "Ni jo et temptaria ara."],
     "que_vols": ["Digues el teu desig, mortal.", "Sí? Temptació escoltant."],
     "enfadat": "Fins i tot jo m'avorreixo. Treballa. 😈"},
    {"nom": "Àngel", "emoji": "😇", "emoji_feliç": "🌟", "emoji_trist": "😢",
     "animacio": "surar",
     "pressio": ["Crec en tu, però fes-ho ja.", "Un petit empenyiment celestial: torna a la feina.", "😇 la teva millor versió t'espera."],
     "decepcio": ["Fins i tot jo dubto de tu... 😢", "El cel està trist amb el teu progrés.", "🌟 la teva llum s'apaga."],
     "que_vols": ["Digues, ho escolto amb calma.", "Sí? T'ajudo."],
     "enfadat": "Fins i tot un àngel perd la paciència. 😇"},
    {"nom": "Zombi", "emoji": "🧟", "emoji_feliç": "🧟‍♂️", "emoji_trist": "🪦",
     "animacio": "tremolor",
     "pressio": ["No et converteixis en un zombi de les xarxes...", "Camino lent, però tu vas més lent encara.", "🧟 desperta't i treballa."],
     "decepcio": ["Grrrr... decepció... 🪦", "Ni els zombis som tan lents.", "Enterraré les teves ganes de treballar."],
     "que_vols": ["Grrrr... què vols?", "..què.. necessites..?"],
     "enfadat": "Grrrr, torna a la feina. 🧟"},
    {"nom": "Ogre", "emoji": "👹", "emoji_feliç": "😡", "emoji_trist": "😰",
     "animacio": "rebot",
     "pressio": ["GRRR! Treballa d'una vegada!", "No em facis enfadar més.", "👹 la meva paciència és petita."],
     "decepcio": ["GRRR... decebut... 😰", "Fins i tot jo em sento petit amb la teva mandra.", "👹 quina vergonya."],
     "que_vols": ["QUÈ VOLS?!", "Parla fort!"],
     "enfadat": "PROU. TREBALLA JA. 👹"},
    {"nom": "Bruixot", "emoji": "🧙", "emoji_feliç": "🪄", "emoji_trist": "📜",
     "animacio": "gir",
     "pressio": ["El meu conjur de productivitat només funciona si hi poses de la teva part.", "Preveig distracció en el teu futur pròxim.", "🧙 la màgia no substitueix l'esforç."],
     "decepcio": ["Els meus encanteris fallen amb tu... 📜", "Ni la màgia et salva de la mandra.", "🪄 la teva aura és grisa."],
     "que_vols": ["Parla, aprenent.", "Digues el teu encanteri."],
     "enfadat": "Torna al teu grimori de feina. 🧙"},
    {"nom": "Ninja", "emoji": "🥷", "emoji_feliç": "⚔️", "emoji_trist": "🗡️",
     "animacio": "tremolor",
     "pressio": ["T'he vigilat en silenci... i estàs distret.", "Un ninja no perd el temps.", "🥷 sigil·losament et recordo la feina."],
     "decepcio": ["El meu honor està tacat... 🗡️", "Ni un aprenent seria tan lent.", "⚔️ decep el dojo."],
     "que_vols": ["Xt... digues ràpid.", "Parla amb sigil."],
     "enfadat": "Desapareixo. Torna a la feina. 🥷"},
    {"nom": "Aranya", "emoji": "🕷️", "emoji_feliç": "🕸️", "emoji_trist": "🪰",
     "animacio": "balanceig",
     "pressio": ["Estic teixint la teva xarxa de distraccions...", "🕸️ compte, t'hi estàs enredant.", "Una aranya pacient sempre atrapa la presa (la teva feina, en aquest cas)."],
     "decepcio": ["La meva xarxa es trenca amb la teva mandra... 🪰", "Ni les mosques treballen tant.", "🕷️ decepció entre fils."],
     "que_vols": ["Digues, què vols atrapar?", "🕷️ escolto des de la xarxa."],
     "enfadat": "Torna a teixir la teva feina, no distraccions. 🕷️"},
    {"nom": "Ratpenat", "emoji": "🦇", "emoji_feliç": "🌙", "emoji_trist": "🦉",
     "animacio": "rebot",
     "pressio": ["Volo per sobre teu vigilant...", "🦇 detecto sons de distracció.", "A les fosques també es treballa, eh."],
     "decepcio": ["La meva ecolocalització només detecta fracàs... 🦉", "🌙 la nit és llarga i tu no avances.", "Fins i tot a les fosques es nota la teva mandra."],
     "que_vols": ["Digues, xt...", "🦇 escolto amb l'ecolocalització."],
     "enfadat": "Me'n vaig volant. Treballa. 🦇"},
    {"nom": "Mussol", "emoji": "🦉", "emoji_feliç": "🦅", "emoji_trist": "🐤",
     "animacio": "surar",
     "pressio": ["Savi consell: torna a la feina.", "🦉 la nit és llarga si no acabes ara.", "Un mussol observa... i tu et distraus."],
     "decepcio": ["Fins i tot jo tinc dubtes de la teva saviesa... 🐤", "🦅 la teva visió és massa curta.", "Uhu... decepció."],
     "que_vols": ["Uhu? Digues.", "Parla amb saviesa."],
     "enfadat": "Uhu-uhu, torna-hi. 🦉"},
    {"nom": "Cargol", "emoji": "🐌", "emoji_feliç": "🐚", "emoji_trist": "🪨",
     "animacio": "surar",
     "pressio": ["Vas més lent que jo, i soc un cargol.", "🐌 a aquest ritme...", "Ni jo trigo tant a fer les coses."],
     "decepcio": ["Fins i tot una pedra avança més... 🪨", "🐚 m'he amagat a la closca de la vergonya.", "Em guanyes, i soc un cargol."],
     "que_vols": ["Digues... (amb calma)", "🐌 t'escolto, sense pressa."],
     "enfadat": "Fins i tot jo avanço més que tu ara. 🐌"},
]


class FantasmaConsola:
    def __init__(self, personatge=None, pomodoro=None, resume=None):
        """
        pomodoro: None o (treball_min, descans_min)
        resume: None o (fase, segons_restants) per reprendre un Pomodoro
                que s'havia pausat en tancar la sessió anterior.
        """
        self.p = personatge or random.choice(PERSONATGES)
        self.pomodoro_actiu = pomodoro is not None

        if self.pomodoro_actiu:
            treball_min, descans_min = pomodoro
            self.treball_segons = max(1, int(treball_min)) * 60
            self.descans_segons = max(1, int(descans_min)) * 60
        else:
            self.treball_segons = 25 * 60
            self.descans_segons = 5 * 60

        # RESUM DE SESSIÓ: si venim d'una sessió anterior, restaurem
        # exactament la fase i el temps restant.
        if resume and self.pomodoro_actiu:
            fase_resum, segons_resum = resume
            if fase_resum in ("treball", "descans"):
                self.fase = fase_resum
                # Assegurem que no sigui negatiu ni massa gran
                maxim = (
                    self.treball_segons if fase_resum == "treball"
                    else self.descans_segons
                )
                self.segons_restants = max(1, min(int(segons_resum), maxim))
            else:
                self.fase = "treball"
                self.segons_restants = self.treball_segons
        else:
            self.fase = "treball"
            self.segons_restants = self.treball_segons

        self.finestra_descans = None

        self.felicitat_actual = 100
        self.ultima_lectura_estat = 0

        self.root = tk.Tk()
        self.root.title(f"AURAL - {self.p['nom']}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.transparent_ok = False
        try:
            self.root.attributes("-transparentcolor", "black")
            self.root.configure(bg="black")
            self.transparent_ok = True
        except Exception:
            self.root.configure(bg="#2b2b2b")

        ample_pantalla = self.root.winfo_screenwidth()
        alt_pantalla = self.root.winfo_screenheight()
        x = ample_pantalla - AMPLADA - 25
        y = alt_pantalla - ALCADA - 55
        self.root.geometry(f"{AMPLADA}x{ALCADA}+{x}+{y}")

        fons = "black" if self.transparent_ok else "#2b2b2b"
        self.canvas = tk.Canvas(
            self.root, width=AMPLADA, height=ALCADA,
            bg=fons, highlightthickness=0,
        )
        self.canvas.pack()

        self.mida_base = 44
        self.personatge_id = self.canvas.create_text(
            AMPLADA // 2, 60, text=self.p["emoji"],
            font=("Segoe UI Emoji", self.mida_base), fill="white",
        )
        self.canvas.tag_bind(self.personatge_id, "<Button-1>", self._clic)
        self.canvas.tag_bind(self.personatge_id, "<B1-Motion>", self._arrossegar)

        self.label_bombolla = None
        self.bombolla_activa = False
        self._t = 0

        self.label_temps = None
        if self.pomodoro_actiu:
            self.label_temps = tk.Label(
                self.root, text="", font=("Arial", 10, "bold"),
                bg="#222831", fg="#ffffff",
            )
            self.label_temps.place(x=2, y=ALCADA - 24, width=AMPLADA - 4, height=20)
            self._actualitzar_label_temps()

        self._animar()
        self._programar_pressio()

        # Si estem en fase de descans quan es reprèn, tornem a obrir el bloqueig
        if self.pomodoro_actiu and self.fase == "descans":
            self._obrir_bloqueig_descans()
        elif self.pomodoro_actiu:
            self.root.after(1000, self._tick_pomodoro)

    def _llegir_estat_felicitat(self):
        try:
            if not os.path.exists(FITXER_ESTIL):
                return 100
            if os.path.getsize(FITXER_ESTIL) == 0:
                return 100
            with open(FITXER_ESTIL, "r", encoding="utf-8") as f:
                dades = json.load(f)
            return int(dades.get("felicitat", 100))
        except Exception:
            return 100

    def _actualitzar_emoji_segons_felicitat(self):
        ara = time.time()
        if ara - self.ultima_lectura_estat < 2:
            return
        self.ultima_lectura_estat = ara
        felicitat = self._llegir_estat_felicitat()
        self.felicitat_actual = max(0, min(100, felicitat))

        if self.felicitat_actual >= 70:
            nou_emoji = self.p.get("emoji_feliç", self.p["emoji"])
        elif self.felicitat_actual >= 40:
            nou_emoji = self.p["emoji"]
        else:
            nou_emoji = self.p.get("emoji_trist", self.p["emoji"])

        try:
            self.canvas.itemconfigure(self.personatge_id, text=nou_emoji)
        except Exception:
            pass

    def _animar(self):
        self._t += 1
        self._actualitzar_emoji_segons_felicitat()
        tipus = self.p["animacio"]

        if tipus == "surar":
            y_offset = math.sin(self._t * 0.15) * 6
            self.canvas.coords(self.personatge_id, AMPLADA // 2, 60 + y_offset)
        elif tipus == "rebot":
            y_offset = abs(math.sin(self._t * 0.2)) * 18
            self.canvas.coords(self.personatge_id, AMPLADA // 2, 70 - y_offset)
        elif tipus == "tremolor":
            x_offset = random.randint(-3, 3)
            y_offset = random.randint(-2, 2)
            self.canvas.coords(
                self.personatge_id, AMPLADA // 2 + x_offset, 60 + y_offset
            )
        elif tipus == "pols":
            mida = self.mida_base + int(math.sin(self._t * 0.2) * 6)
            self.canvas.itemconfigure(
                self.personatge_id, font=("Segoe UI Emoji", mida)
            )
            self.canvas.coords(self.personatge_id, AMPLADA // 2, 60)
        elif tipus == "balanceig":
            x_offset = math.sin(self._t * 0.1) * 15
            self.canvas.coords(
                self.personatge_id, AMPLADA // 2 + x_offset, 60
            )
        elif tipus == "gir":
            x_offset = math.cos(self._t * 0.15) * 12
            y_offset = math.sin(self._t * 0.15) * 12
            self.canvas.coords(
                self.personatge_id, AMPLADA // 2 + x_offset, 60 + y_offset
            )
        elif tipus == "flicker":
            y_offset = math.sin(self._t * 0.12) * 6
            self.canvas.coords(self.personatge_id, AMPLADA // 2, 60 + y_offset)
            if self._t % 40 < 3:
                estat_actual = self.canvas.itemcget(self.personatge_id, "state")
                nou = "hidden" if estat_actual != "hidden" else "normal"
                self.canvas.itemconfigure(self.personatge_id, state=nou)
            else:
                self.canvas.itemconfigure(self.personatge_id, state="normal")

        self.root.after(80, self._animar)

    def _actualitzar_label_temps(self):
        if not self.label_temps:
            return
        minuts, segons = divmod(max(0, self.segons_restants), 60)
        etiqueta_fase = "🍅 Treball" if self.fase == "treball" else "☕ Descans"
        self.label_temps.configure(
            text=f"{etiqueta_fase}  {minuts:02d}:{segons:02d}"
        )

    def _tick_pomodoro(self):
        if not self.pomodoro_actiu or self.fase != "treball":
            return
        self.segons_restants -= 1
        self._actualitzar_label_temps()
        if self.segons_restants <= 0:
            self._iniciar_descans()
        else:
            self.root.after(1000, self._tick_pomodoro)

    def _iniciar_descans(self):
        self.fase = "descans"
        self.segons_restants = self.descans_segons
        self._actualitzar_label_temps()
        self._obrir_bloqueig_descans()

    def _acabar_descans(self):
        if self.finestra_descans and self.finestra_descans.winfo_exists():
            self.finestra_descans.destroy()
        self.finestra_descans = None
        self.fase = "treball"
        self.segons_restants = self.treball_segons
        self._actualitzar_label_temps()
        self.root.after(1000, self._tick_pomodoro)

    def _obrir_bloqueig_descans(self):
        finestra = tk.Toplevel(self.root)
        self.finestra_descans = finestra
        finestra.overrideredirect(True)
        finestra.attributes("-topmost", True)
        finestra.configure(bg="#101820")
        ample = finestra.winfo_screenwidth()
        alt = finestra.winfo_screenheight()
        finestra.geometry(f"{ample}x{alt}+0+0")
        finestra.protocol("WM_DELETE_WINDOW", lambda: None)
        finestra.focus_force()
        finestra.grab_set()

        frame = tk.Frame(finestra, bg="#101820")
        frame.pack(expand=True)
        tk.Label(
            frame, text=self.p["emoji"], font=("Segoe UI Emoji", 110),
            bg="#101820", fg="white",
        ).pack(pady=(0, 10))
        tk.Label(
            frame, text="☕ Descans!", font=("Arial", 32, "bold"),
            bg="#101820", fg="#ffffff",
        ).pack(pady=(0, 10))
        label_compte = tk.Label(
            frame, text="", font=("Arial", 46, "bold"),
            bg="#101820", fg="#7c6cf0",
        )
        label_compte.pack(pady=(0, 20))
        label_missatge = tk.Label(
            frame, text="", font=("Arial", 18),
            bg="#101820", fg="#d0d0d0", wraplength=700, justify="center",
        )
        label_missatge.pack(pady=(0, 10))

        def actualitzar_compte():
            if not finestra.winfo_exists():
                return
            minuts, segons = divmod(max(0, self.segons_restants), 60)
            label_compte.configure(text=f"{minuts:02d}:{segons:02d}")

        def canviar_missatge():
            if not finestra.winfo_exists():
                return
            label_missatge.configure(text=random.choice(DESCANS_MISSATGES))
            finestra.after(6000, canviar_missatge)

        def tick_descans():
            if not finestra.winfo_exists():
                return
            self.segons_restants -= 1
            actualitzar_compte()
            self._actualitzar_label_temps()
            if self.segons_restants <= 0:
                self._acabar_descans()
            else:
                finestra.after(1000, tick_descans)

        actualitzar_compte()
        canviar_missatge()
        finestra.after(1000, tick_descans)

    def _arrossegar(self, event):
        x_root = self.root.winfo_pointerx() - AMPLADA // 2
        y_root = self.root.winfo_pointery() - 40
        self.root.geometry(f"+{x_root}+{y_root}")

    def _clic(self, event):
        if self.bombolla_activa:
            self._mostrar_bombolla(self.p["enfadat"], enfadat=True)
        else:
            self._mostrar_bombolla(random.choice(self.p["que_vols"]))

    def _mostrar_bombolla(self, text, enfadat=False):
        if self.label_bombolla:
            self.label_bombolla.destroy()
        self.bombolla_activa = True
        color = "#ffcdd2" if enfadat else "#fffde7"
        self.label_bombolla = tk.Label(
            self.root, text=text, font=("Arial", 9, "bold"),
            bg=color, fg="#333", wraplength=AMPLADA - 10, justify="center",
            relief="solid", bd=1,
        )
        self.label_bombolla.place(x=2, y=2, width=AMPLADA - 4)
        self.root.after(3500, self._amagar_bombolla)

    def _amagar_bombolla(self):
        if self.label_bombolla:
            self.label_bombolla.destroy()
            self.label_bombolla = None
        self.bombolla_activa = False

    def _programar_pressio(self):
        if self.bombolla_activa:
            self.root.after(5000, self._programar_pressio)
            return

        if self.felicitat_actual < 40:
            if random.random() < 0.55:
                missatges = self.p.get("decepcio") or self.p["pressio"]
                self._mostrar_bombolla(random.choice(missatges))
            seguent = random.randint(18000, 35000)
        elif self.felicitat_actual < 70:
            if random.random() < 0.30:
                self._mostrar_bombolla(random.choice(self.p["pressio"]))
            seguent = random.randint(35000, 60000)
        else:
            if random.random() < 0.20:
                self._mostrar_bombolla(random.choice(self.p["pressio"]))
            seguent = random.randint(55000, 95000)

        self.root.after(seguent, self._programar_pressio)

    def iniciar(self):
        self.root.mainloop()


def _triar_personatge_per_argument(arg):
    if arg.isdigit():
        idx = int(arg)
        if 0 <= idx < len(PERSONATGES):
            return PERSONATGES[idx]
    for p in PERSONATGES:
        if p["nom"].lower() == arg.lower():
            return p
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Personatge flotant AURAL")
    parser.add_argument(
        "--personatge", "-p", default=None,
        help="Nom o índex del personatge (per defecte: aleatori)",
    )
    parser.add_argument(
        "--pomodoro", nargs=2, type=int, metavar=("TREBALL_MIN", "DESCANS_MIN"),
        default=None, help="Activa el mode Pomodoro amb minuts de treball i descans",
    )
    parser.add_argument(
        "--resume", nargs=2, metavar=("FASE", "SEGONS_RESTANTS"),
        default=None,
        help="Reprèn un Pomodoro pausat. FASE = 'treball' o 'descans', "
             "SEGONS_RESTANTS = temps que quedava en tancar la sessió anterior.",
    )
    args, desconeguts = parser.parse_known_args()

    personatge_triat = None
    if args.personatge:
        personatge_triat = _triar_personatge_per_argument(args.personatge)
        if personatge_triat is None:
            print(f"[AVÍS] No s'ha trobat '{args.personatge}'. Se'n tria un a l'atzar.")
    elif desconeguts:
        personatge_triat = _triar_personatge_per_argument(desconeguts[0])
        if personatge_triat is None:
            print(f"[AVÍS] No s'ha trobat '{desconeguts[0]}'. Se'n tria un a l'atzar.")

    resume = None
    if args.resume:
        fase_str, segons_str = args.resume
        try:
            resume = (fase_str.lower(), int(segons_str))
        except ValueError:
            print("[AVÍS] Argument --resume invàleg. S'ignora.")
            resume = None

    try:
        app = FantasmaConsola(
            personatge_triat,
            pomodoro=args.pomodoro,
            resume=resume,
        )
        app.iniciar()
    except Exception as e:
        print(f"[ERROR FANTASMA]: {e}")
        sys.exit(1)