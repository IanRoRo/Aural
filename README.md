# 🤖 Aural — Assistent de Productivitat Intel·ligent

[![Llicència: MIT](https://img.shields.io/badge/Llic%C3%A8ncia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Models d'IA](https://img.shields.io/badge/LLM-Llama_3.2_%7C_DeepSeek--R1-purple.svg)](https://ollama.ai/)
[![Tipus de Projecte](https://img.shields.io/badge/TDR-1r_Batxillerat-orange.svg)]()

> **Idiomes / Languages:** 🐱 [Català](#català) | 🇬🇧 [English](#english) | 🇪🇸 [Español](#español)

---

<a name="català"></a>
## 🐱 Resum en Català

**Aural** és un assistent de productivitat intel·ligent, privat i d'execució local dissenyat per reduir les distraccions digitals durant les sessions d'estudi. Desenvolupat com a Treball de Recerca (TDR) de 1r de Batxillerat en un termini de 3 mesos, combina el monitoratge del sistema operatiu en temps real amb IA local (mitjançant Ollama) i un algorisme d'adaptació basat en l'estat d'ànim i la felicitat de l'assistent.

### ✨ Característiques Principals
- **IA Privada i Local:** S'executa 100% offline utilitzant els models `Llama 3.2` i `DeepSeek-R1` a través d'Ollama.
- **Monitoratge Actiu del SO:** `ulls.py` rastreja el focus de la finestra activa i les pulsacions de tecles en temps real.
- **Bloqueig Dinàmic:** `mans.py` força el focus de treball tancant els processos de distracció no desitjats mitjançant l'avaluació per PLN (Processament del Llenguatge Natural).
- **Acompanyant Adaptatiu:** `fantasma.py` inclou un algorisme d'estat emocional/felicitat que reacciona directament als nivells de productivitat de l'usuari.
- **Analítica Personalitzada:** `grafics.py` genera informes visuals sobre la distribució del temps utilitzant Pandas i Matplotlib.

### 🏗️ Arquitectura i Mòduls
- `ulls.py` — Monitoratge de finestres i activitat (`pygetwindow`, `pynput`, `psutil`)
- `mans.py` — Gestor dinàmic de processos i control de finestres
- `fantasma.py` — Lògica d'estat emocional i giny visual interactiu
- `grafics.py` — Canalització per a la generació d'analítiques
- `%appdata%/Aural/` — Base de dades local i registres persistents del sistema

---

<a name="english"></a>
## 🇬🇧 English Summary

**Aural** is a local, privacy-focused intelligent productivity assistant designed to curb digital distractions during study sessions. Built as a 1st-year Baccalaureate Research Project (TDR) in just 3 months, it combines dynamic OS-level monitoring with local LLMs (via Ollama) and a happiness-based adaptation algorithm.

### ✨ Key Features
- **Privacy-First AI:** Runs fully offline using `Llama 3.2` and `DeepSeek-R1` through Ollama.
- **Active OS Monitoring:** `ulls.py` monitors active window focus and keystrokes in real-time.
- **Dynamic Blocking:** `mans.py` enforces active focus by closing unwanted distraction processes via NLP evaluation.
- **Adaptive Companion:** `fantasma.py` features an emotional/happiness state algorithm that reacts to productivity levels.
- **Personal Analytics:** `grafics.py` generates visual insights on time allocation using Pandas and Matplotlib.

---

<a name="español"></a>
## 🇪🇸 Resumen en Español

**Aural** es un asistente de productividad inteligente, privado y de ejecución local diseñado para reducir las distracciones digitales. Desarrollado como Trabajo de Investigación (TDR) de 1º de Bachillerato en un plazo de 3 meses, combina monitorización a nivel de SO con IA local (Ollama) y un algoritmo de adaptación basado en el estado emocional del asistente.

### ✨ Características Principales
- **IA 100% Local:** Ejecución privada usando `Llama 3.2` y `DeepSeek-R1` mediante Ollama.
- **Monitorización de SO:** `ulls.py` detecta la ventana activa y actividad en tiempo real.
- **Bloqueo Inteligente:** `mans.py` gestiona el cierre de procesos mediante evaluación NLP.
- **Asistente Adaptativo:** `fantasma.py` adapta su comportamiento e interfaz según la productividad del usuario.
- **Módulo de Analítica:** `grafics.py` genera informes gráficos con Pandas y Matplotlib.

---

## 📄 Context Acadèmic i Documentació

Aquest repositori conté el codi font i els registres de desenvolupament del **TDR Aural**.

- 🌐 **Lloc Web del Projecte:** [Visita el web del projecte](https://iaaural.netlify.app)
- 📄 **Memòria Completa en PDF:** Disponible a `/docs/Memoria_Aural_TDR.pdf`
- 🛠️ **Metodologia:** Desenvolupat utilitzant una metodologia d'enginyeria de programari assistida per Copilot (arquitectura assistida per IA i prototipatge ràpid).
