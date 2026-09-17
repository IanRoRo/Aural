# Desenvolupament d'una Intel·ligència Artificial per a la Gestió del Temps (Aural IA)
**Treball de Recerca (1r de Batxillerat)**

“Aural” és un assistent de productivitat intel·ligent i proactiu dissenyat en Python que utilitza Intel·ligència Artificial local (Llama 3.2) per combatre les distraccions digitals en l'àmbit acadèmic.

---

## Flux d'ús del programa

* **Fase inicial de planificació:** El procés s'inicia amb una pantalla de bloqueig on l'usuari ha de definir el seu objectiu d'estudi. Aural, mitjançant processament de llenguatge natural, avalua si l'objectiu és vàlid, demana més concreció si és massa genèric o rebutja el text si no té sentit. D'aquesta manera, s'obliga l'usuari a vèncer la resistència inicial a la planificació abans de poder utilitzar l'ordinador.
* **Monitoratge dinàmic:** A diferència dels bloquejadors d'aplicacions tradicionals, Aural monitoritza en segon pla l'activitat de la pantalla i avalua el comportament de l'usuari mitjançant un algorisme de "Percentatge de Felicitat" o autocontrol. Segons aquest percentatge, el caràcter i el nivell de restricció de la IA s'adapten dinàmicament:
  * **Amb un 100%:** L'usuari gaudeix de llibertat absoluta i l'assistent l'avisa del risc de cremar-se (burnout).
  * **Entre el 80% i el 90%:** Augmenta la vigilància per evitar caure en temptacions.
  * **Entre el 50% i el 80%:** Aural es torna antipàtic i comença a tancar finestres de forma activa.
  * **Per sota del 50%:** Només permet tres avisos per sessió abans de tancar qualsevol element no productiu.
  * **En caure per sota del 30%:** S'activa el mode d'hostilitat màxima, tancant distraccions fulminantment i sense donar cap mena d'explicació.
* **Mòdul d'Analítica:** El sistema inclou un mòdul encarregat de registrar l'activitat i generar gràfiques visuals sobre els minuts productius. D'aquesta manera, l'usuari pot consultar de forma ràpida i clara com ha aprofitat el temps i avaluar el seu rendiment. 

---

## Versions

Durant el procés de desenvolupament del projecte, han sorgit diversos desafiaments relacionats amb la potència de càlcul i la precisió de la IA. Per aquest motiu, s'han dissenyat tres versions del sistema, adaptades a diferents necessitats i requeriments de maquinari:

* **Aural Lite:** Es tracta d'una versió lleugera que prescindeix de sistemes neuronals. Funciona mitjançant un aprenentatge supervisat on l'usuari defineix els patrons de comportament per a cada mode. En no utilitzar cap model de llenguatge (LLM) ni intel·ligència artificial, no té capacitat de qüestionar l'usuari ni de raonar; el seu gran avantatge és que és extremadament eficient i compatible amb gairebé qualsevol dispositiu, independentment del seu maquinari.
* **Aural:** És la versió estàndard del projecte, desenvolupada amb el model Llama 3.2 (d'1 mil milions de paràmetres / 1 billion). A diferència de la versió Lite, aquesta IA és capaç de processar llenguatge natural, qüestionar els objectius de les sessions i suggerir modes de treball. Durant l'execució, té la capacitat de discernir si l'ús de noves aplicacions correspon a una activitat productiva o a una distracció, tot i que, a causa de la naturalesa del model, la precisió en l'anàlisi pot ser limitada en contextos complexos.
* **Aural Pro:** Representa l'evolució més avançada del sistema. Aquesta versió incorpora un model d'IA significativament més potent, amb una arquitectura de 8 mil milions de paràmetres. Aquesta major capacitat ofereix una lògica més robusta i precisa en la presa de decisions. Com a contrapartida, aquesta versió requereix un equip amb capacitats de processament (CPU/GPU/RAM) elevades per poder executar la IA en segon pla de manera fluida sense afectar el rendiment general de l'ordinador.

---

## Propòsit

El propòsit d'Aural és experimentar si un sistema de control rígid, dinàmic i amb pressió psicològica per part d'una IA —combinat amb flexibilitat humana— és més efectiu per recuperar l'enfocament que els mètodes de motivació tous tradicionals.

---

# Diari de Desenvolupament

* **Dia 1 (Dimarts 07/04/26)**
  * ❖ Fase 1: Mòdul de monitoratge i captura de dades (`ulls.py`)
* **Dia 2 (Dijous 09/04/26)**
  * ❖ Fase 2: Mòdul d'execució d'accions (`mans.py`)
  * ❖ Fase 3: Algorisme de control de caràcter i estat
* **Setmana 3 (Del 25/05/26 al 31/05/26)**
  * ❖ Fase 4: Integració del model de llenguatge (LLM)
  * ❖ Fase 5: Gestió contextual i modes de treball
* **Setmanes 4 - 5 (Del 1/05/26 al 14/06/26)**
  * ❖ Fase 6: Gràfics i Estadístiques
* **Setmanes 6 a 10 (Del 15/06/26 al 23/07/26)**
  * ❖ Fase 7: Diversificació del sistema i disseny d'Aural Lite
  * ❖ Fase 8: Mòdul visual i de motivació (`fantasma.py`)
  * ❖ Fase 9: Redissenys de la interfície (UI) i noves mesures dissuasives
* **Setmanes 11 i 12 (Del 17/08/26 al 30/08/26)**
  * ❖ Fase 10: Integració de DeepSeek-R1 i compilació del sistema
  * ❖ Fase 11: Desplegament web i tancament del projecte

---

## Dia 1 (Dimarts 07/04/26)

Durant la primera jornada de desenvolupament s'han establert les bases de l'arquitectura de programari i s'han implementat les funcionalitats bàsiques de monitoratge d'Aural. Per garantir una gestió aïllada i eficient de les dependències, s'ha configurat un entorn virtual de desenvolupament en Python dedicat exclusivament al projecte.

### Problemes detectats:
* **Conflictes d'instal·lació de dependències:** Es van generar errors en la descàrrega i vinculació de les llibreries inicials en l'entorn global del sistema. Es va resoldre creant i configurant un entorn virtual (`venv`) dins del directori del projecte per aïllar els paquets necessaris.

### Objectius assolits aquesta jornada:
* **Fase 1: Mòdul de monitoratge i captura de dades (`ulls.py`)**
  * **Pas 1.1:** Disseny i execució d'un bucle principal de control temporal configurat per executar-se en intervals de 5 segons.
  * **Pas 1.2:** Implementació de la llibreria `pygetwindow` per a la captura dinàmica i l'obtenció del títol de la finestra activa en cada cicle.
  * **Pas 1.3:** Integració de la llibreria `pynput` per a la detecció d'inactivitat de l'usuari (mitjançant el seguiment dels esdeveniments del ratolí i del teclat en els darrers 2-3 minuts), optimitzant el consum de recursos en evitar l'anàlisi continu de píxels.
  * **Pas 1.4:** Creació del sistema de persistència de dades per a l'enregistrament estructurat de l'activitat (data, hora, nom de la finestra i estat d'activitat) en un fitxer en format `.csv`.

*El codi font d'aquesta fase inicial s'ha consolidat i pujat al repositori de GitHub.*

---

## Dia 2 (Dijous 09/04/26)

Durant aquesta jornada s'ha implementat el mòdul d'interacció amb el sistema operatiu. Per a aquesta funció s'ha creat el fitxer `mans.py`, el qual conté les rutines encarregades d'executar les accions del programa (`AVISAR`, `TANCAR_FINESTRA` i `BLOQUEJAR_INICI`). Totes aquestes funcions s'han centralitzat i coordinat des del fitxer principal `main.py`, que actua com a mòdul de control central del sistema.

### Problemes detectats:
* **Bloqueig del flux d'execució per bucle residual:** S'ha detectat que el programa no avançava en la seva seqüència a causa d'un bucle infinit no eliminat al fitxer `ulls.py`, el qual impedia l'arribada d'instruccions a la resta del codi. Es va resoldre depurant l'estructura de control del mòdul de monitoratge.
* **Manca de notificacions de transició d'estat:** El sistema tancava les aplicacions de forma immediata sense emetre cap avís previ. Es va integrar la lògica del controlador de productivitat ("Percentatge de Felicitat") per generar alertes preventives i notificar a l'usuari la necessitat de realitzar pauses de descans després de períodes de concentració prolongats.

### Objectius assolits aquesta jornada:
* **Fase 2: Mòdul d'execució d'accions (`mans.py`)**
  * **Pas 2.1 (Notificacions):** Implementació de la funció `AVISAR` per a la generació de finestres emergents i avisos del sistema.
  * **Pas 2.2 (Control de processos):** Desenvolupament de la funció `TANCAR_FINESTRA` utilitzant la llibreria `psutil` per a la finalització forçada de processos no productius.
  * **Pas 2.3 i 2.4 (Bloqueig proactiu):** Disseny de la interfície de bloqueig inicial (`BLOQUEJAR_INICI`) que obliga l'usuari a definir un objectiu concret de treball abans d'habilitar l'ús de l'ordinador.
* **Fase 3: Algorisme de control de caràcter i estat**
  * **Pas 3.1:** Creació de la variable mètrica de "Felicitat" o "Paciència" (amb una escala numèrica de 0 a 10).
  * **Pas 3.2:** Desenvolupament de la lògica d'adaptació dinàmica: l'estat augmenta progressivament durant els períodes d'activitat productiva i decreix ràpidament quan es detecten distraccions.

*El codi corresponent a aquesta fase s'ha consolidat i actualitzat al repositori de GitHub.*

---

## Setmana 3 (Del 25/05/26 al 31/05/26)

Aquesta setmana el desenvolupament s'ha centrat en la integració del nucli d'Intel·ligència Artificial del sistema. L'objectiu principal ha estat connectar el model Llama 3.2 en local mitjançant la plataforma Ollama, permetent que Aural interpreti de forma autònoma l'activitat de l'usuari, avaluï la validesa dels objectius d'estudi i prengui decisions d'execució en segon pla. 

### Problemes detectats:
* **Latència excessiva per doble traducció:** Inicialment es va dissenyar un sistema intermedi que traduïa els textos al català i a l'anglès per aprofitar el millor rendiment del model en anglès. No obstant això, aquest flux de traducció (Català → Anglès → Català) generava una latència inacceptable i errors d'interpretació. Es va resoldre eliminant la traducció i optimitzant l'estructura dels prompts directament en llengua catalana.
* **Corrupció de caràcters al fitxer CSV:** S'ha detectat que la codificació per defecte del sistema operatiu Windows generava caràcters corruptes en desar accents i caràcters especials. Es va solucionar forçant la lectura i escriptura dels fitxers de registre mitjançant el format `encoding='utf-8'`.

### Objectius assolits aquesta setmana:
* **Fase 4: Integració del model de llenguatge (LLM)**
  * **Pas 4.1:** Configuració i vinculació de l'API d'Ollama en Python per a l'execució de Llama 3.2 en entorn local, sense dependència de connexió a Internet.
  * **Pas 4.2:** Desenvolupament de l'algorisme de validació d'objectius a la pantalla de bloqueig inicial, capacitant la IA per rebutjar entrades no acadèmiques o no vàlides abans de permetre l'accés al sistema.
* **Fase 5: Gestió contextual i modes de treball**
  * **Pas 5.1:** Implementació de la classificació dinàmica d'aplicacions: la IA analitza noves finestres obertes i les categoritza per similitud semàntica dins la llista blanca (productiva) o llista negra (distracció).
  * **Pas 5.2:** Programació de la inferència contextual per assignatures, permetent que el sistema autoritzi l'ús de recursos auxiliars (com diccionaris o eines de consulta) segons la matèria seleccionada.
  * **Pas 5.3:** Disseny del sistema de persistència de "Modes" (ex. Estudiar o Programar) per emmagatzemar configuracions prèvies i optimitzar el temps d'execució en sessions posteriors.

*Un cop validada l'estabilitat del sistema integrat en un entorn de proves, el codi corresponent a aquesta fase s'ha actualitzat al repositori de GitHub.*

---

## Setmanes 4 - 5 (Del 01/05/26 al 14/06/26)

Aquestes setmanes el desenvolupament s'ha centrat en la implementació del sistema de recollida de dades i en la generació d'estadístiques visuals. L'objectiu ha estat dissenyar un panell de control (*dashboard*) integrat per avaluar la productivitat de l'usuari d'una ullada. Per a aquesta funció, s'ha creat el nou mòdul `grafics.py`, encarregat de llegir i processar les dades enregistrades.

### Problemes detectats:
* **Inestabilitat en la integració de gràfics a la interfície:** Es van detectar dificultats per integrar els gràfics de Matplotlib dins la finestra principal de Tkinter, ja que generaven tancaments inesperats o llançaven finestres externes. Es va resoldre utilitzant la interfície `FigureCanvasTkAgg` per incrustar els gràfics directament com a components de la interfície d'usuari.
* **Inconsistència de dades al fitxer CSV:** Durant les proves inicials, la presència de línies en blanc al fitxer de registre `.csv` generava excepcions en la lectura de dades. S'ha integrat un procés de neteja automàtica mitjançant la llibreria Pandas (emprant les funcions `str.strip()` i `dropna()`) per eliminar registres buits abans de processar la visualització.

### Objectius assolits aquestes setmanes:
* **Fase 6: Gràfics i Estadístiques**
  * **Pas 6.1:** Desenvolupament de la interfície en Tkinter amb selectors desplegables per a la filtració temporal per any i mes.
  * **Pas 6.2:** Programació de l'algorisme d'agregació de registres quinquagenerals (cada 5 segons) per al càlcul del percentatge real de temps "Productiu" i "Distret" sobre el total.
  * **Pas 6.3:** Implementació de controls d'interactivitat per alternar entre la Vista Diària, Setmanal o Mensual, representant els resultats mitjançant diagrames de barres de colors (verd per a activitats productives i vermell per a distraccions).

*A causa dels errors de processament de dades i de la necessitat de depurar el codi d'integració entre Matplotlib i Tkinter, es va decidir mantenir aquest mòdul en un entorn de desenvolupament local. La pujada al repositori de GitHub es va posposar fins a consolidar una versió completament estable i lliure d'excepcions.*

---

## Setmanes 6 a 10 (Del 15/06/26 al 23/07/26)

Aquestes setmanes van suposar una reestructuració profunda del projecte. A causa de les limitacions i els errors de processament derivats de la simplicitat del model d'IA integrat inicialment —el qual s'havia escollit per reduir el consum de recursos de l'ordinador—, el sistema no aconseguia la precisió desitjada. Després de provar nombrosos canvis en els prompts i traduccions entre català i anglès sense obtenir els resultats esperats, es va decidir replantejar l'arquitectura del programari i diversificar-lo en tres versions diferents (Aural Lite, Aural i Aural Pro). 

Per cobrir els equips amb menys recursos sense dependre d'un model d'IA imprecís, es va dissenyar la versió Aural Lite, la qual prescindeix de models de llenguatge externs i es basa únicament en l'algorisme local del programa. Paral·lelament, es va començar a investigar quins models d'IA més potents es podrien incorporar per a la futura versió Pro. 

### Problemes detectats:
* **Imprecisió per simplicitat del model d'IA:** En utilitzar un model d'IA molt lleuger per no sobrecarregar el sistema, la capacitat de processament i la precisió contextual eren insuficients, generant molts errors d'interpretació.
* **Manca d'impacte dels avisos tradicionals:** Les notificacions emergents petites eren fàcils d'ignorar per l'usuari, reduint l'efectivitat del sistema contra les distraccions.
* **Risc d'esgotament (*burnout*):** Calia un mecanisme que obligués l'usuari a fer pauses reals i desconnectar la vista de la pantalla després d'un bloc de treball.

### Objectius assolits aquestes setmanes:
* **Fase 7: Diversificació del sistema i disseny d'Aural Lite**
  * *Arquitectura multiversió:* Creació de la versió Aural Lite, optimitzada per funcionar sense IA externa mitjançant regles i algorismes locals, eliminant la dependència d'un model d'IA bàsic i reduint al màxim el consum de CPU/RAM.
  * *Cerca de models superiors:* Inici de la recerca de models de llenguatge més potents i complexos (futur Aural Pro) per garantir una lògica i un raonament contextual precisos.
* **Fase 8: Mòdul visual i de motivació (`fantasma.py`)**
  * *Implementació de la mascota virtual:* Creació del fitxer `fantasma.py`, un assistent visual que utilitza icones/emojis (com un fantasma, una cara somrient o una flama) ubicat a la part inferior de la pantalla.
  * *Integració de la tècnica Pomodoro:* La mascota canvia d'estat (content, enfadat o decebut) i de diàleg segons el nivell de productivitat i el temps de treball acumulat.
* **Fase 9: Redissenys de la interfície (UI) i noves mesures dissuasives**
  * *Interfície d'Avisos Reflexius:* Substitució de les notificacions petites per una pantalla completa de pausa forçada de 5 segons quan es detecta una distracció. Aquest temporitzador no es pot saltar, obligant l'usuari a reflexionar abans de continuar.
  * *Bloqueig de descans actiu:* Quan finalitza el bloc de treball definit, el sistema bloqueja l'ordinador i mostra consells de salut laboral (beure aigua, mirar de lluny, fer estiraments) per evitar l'esgotament psicològic.
  * *Actualització general de la UI:* Redisseny global de la interfície d'usuari per permetre la selecció de modes de treball (estudiar, programar, llegir) més facilment, la personalització del temps de treball/descans i l'elecció de la mascota.

*A causa de la gran magnitud dels canvis arquitectònics i als problemes de compatibilitat derivats de la reestructuració multiversió, es va decidir pausar les actualitzacions periòdiques al repositori de GitHub durant aquestes setmanes. Tot el codi es va mantenir en un entorn de desenvolupament local per resoldre els conflictes d'integració i estabilitzar la nova estructura abans d'efectuar el següent commit principal.*

---

## Setmanes 11 i 12 (Del 17/08/26 al 30/08/26)

Aquestes dues últimes setmanes de desenvolupament van culminar el projecte amb la creació de la versió Aural Pro, la integració d'un model de llenguatge d'alta capacitat, el procés de compilació de tot el sistema i el desplegament del portal web de distribució.

Per a la versió Pro s'hi va integrar el model **DeepSeek-R1 8B** (quantitzat en `Q4_K_M`), el qual ofereix un rendiment i un raonament superior a Llama 3.2. Aquest model va permetre augmentar de forma dràstica la precisió en la detecció de distraccions i garantir una major estabilitat en la definició dels modes de treball. Les tres versions (Lite, Standard i Pro) van compartir l'estructura principal de prompts, adaptant cada mòdul a les seves necessitats específiques (com ara la supressió del mòdul d'IA a Aural Lite o la incorporació d'un script de verificació i instal·lació automàtica del model a les versions Standard i Pro).

### Problemes detectats:
* **Conflictes de compilació i modularitat:** La conversió dels scripts de Python a executables independents (`.exe`) va generar nombrosos errors de dependències. Es va optar per compilar el mòdul `fantasma.py` de forma separada per preservar la modularitat del programari.
* **Gestió de permisos i rutes relatives:** L'execució directa dels fitxers `.exe` causava errors d'escriptura quan s'intentava guardar dades a la carpeta d'instal·lació. Es va haver de refactoritzar el codi per redirigir l'emmagatzematge dels fitxers de registre (`.csv`) i configuració al directori de l'usuari `%appdata%`.
* **Optimització del pes lingüístic:** Es va avaluar la possibilitat de fer la IA multilingüe, però es va decidir mantenir el nucli d'Aural exclusivament en català per evitar un augment excessiu en la mida dels executables i en els temps de resposta.

### Objectius assolits aquestes setmanes:
* **Fase 10: Integració de DeepSeek-R1 i compilació del sistema**
  * *Integració del model DeepSeek-R1 8B:* Configuració de la versió Pro amb quantització `Q4_K_M` per a una execució local optimitzada i una classificació de finestres extremadament precisa.
  * *Compilació a Executables (`.exe`):* Conversió de tots els mòduls de Python a executables mitjançant eines de congelació de codi.
  * *Desenvolupament de l'Instal·lador Unificat:* Creació d'un assistent d'instal·lació que permet a l'usuari triar quina versió instal·lar (Lite, Standard o Pro), personalitzar la ruta d'instal·lació i configurar l'inici automàtic amb el sistema operatiu.
* **Fase 11: Desplegament web i tancament del projecte**
  * *Creació del lloc web oficial d'Aural:* Disseny i publicació d'una plataforma web accessible en tres idiomes (català, castellà i anglès) per facilitar la descàrrega de l'instal·lador unificat i la divulgació de la documentació del projecte.
  * *Consolidació i publicació del codi font:* Una vegada resolts tots els conflictes de compilació, permisos de `%appdata%` i estabilitzades les tres versions, es va realitzar la pujada definitiva del codi font estructurat i actualitzat al repositori de GitHub.
