# 🤖 Aural — Intelligent Productivity Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AI Models](https://img.shields.io/badge/LLM-Llama_3.2_%7C_DeepSeek--R1-purple.svg)](https://ollama.ai/)
[![Project Type](https://img.shields.io/badge/TDR-1st_Baccalaureate-orange.svg)]()

> **Languages / Idiomes:** 🇬🇧 [English](#english) | 🐱 [Català](#català) | 🇪🇸 [Español](#español)

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

### 🏗️ Architecture & Modules
- `ulls.py` — Window monitoring (`pygetwindow`, `pynput`, `psutil`)
- `mans.py` — Dynamic process manager & window control
- `fantasma.py` — Interactive visual widget & emotional state logic
- `grafics.py` — Analytics generation pipeline
- `%appdata%/Aural/` — Local database & persistent system logs

---

<a name="català"></a>
## 🐱 Resum en Català

**Aural** és un assistent de productivitat intel·ligent, privat i d'execució local dissenyat per reduir les distraccions digitals durant les sessions d'estudi. Desenvolupat com a Treball de Recerca (TDR) de 1r de Batxillerat en 3 mesos, combina el monitoratge del sistema operatiu en temps real amb IA local (Ollama) i un algorisme d'adaptació basat en la "felicitat" de l'assistent.

### ✨ Característiques Principals
- **IA Privada i Local:** Execució 100% offline amb models `Llama 3.2` i `DeepSeek-R1` via Ollama.
- **Monitoratge Actiu de SO:** `ulls.py` rastreja la finestra activa i els patrons d'ús en temps real.
- **Bloqueig Dinàmic:** `mans.py` tanca els processos de distracció a través d'avaluació per PLN (Processament del Llenguatge Natural).
- **Mascota Adaptativa:** `fantasma.py` gestiona la interfície visual i l'algorisme d'estat d'ànim/hostilitat segons el rendiment.
- **Analítica Personalitzada:** `grafics.py` processa els registres amb Pandas i Matplotlib per mostrar estadístiques d'estudi.

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

## 📄 Academic Context & Documentation

This repository contains the source code and development logs for the **Aural TDR**. 

- 🌐 **Web Portal:** [Visit project website](https://el-teu-usuari.github.io/aural-web) *(o el teu link)*
- 📄 **Full Thesis PDF:** Available in `/docs/Memoria_Aural_TDR.pdf`
- 🛠️ **Methodology:** Developed using a Copilot-assisted software engineering methodology (AI-assisted architecture & rapid prototyping).
