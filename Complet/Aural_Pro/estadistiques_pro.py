import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def ruta_dades_usuari(nom_fitxer):
    if getattr(sys, 'frozen', False):
        appdata_dir = os.path.join(os.getenv('APPDATA'), 'Aural')
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, nom_fitxer)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), nom_fitxer)

FITXER_CSV = ruta_dades_usuari("registre_activitat_pro.csv")

def mostrar_grafics():
    if not os.path.exists(FITXER_CSV) or os.path.getsize(FITXER_CSV) == 0:
        print("Avís: No s'ha trobat el fitxer de registres o està buit.")
        return
    try:
        df = pd.read_csv(FITXER_CSV, delimiter=",", encoding="utf-8-sig", skipinitialspace=True)
    except Exception as e:
        print(f"Error al llegir el CSV: {e}")
        return

    df.columns = df.columns.str.strip()
    if 'Data' not in df.columns or 'Estat IA' not in df.columns:
        print("Avís: El CSV no té l'estructura esperada ('Data' i 'Estat IA').")
        return

    df = df[df['Estat IA'].isin(['PRODUCTIU', 'DISTRET'])]
    if df.empty:
        print("Avís: No hi ha prou dades vàlides per analitzar.")
        return

    df['Data_Formatada'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data_Formatada'])

    df['Any_Str'] = df['Data_Formatada'].dt.strftime('%Y')
    df['Mes_Str'] = df['Data_Formatada'].dt.strftime('%m')

    llista_anys = sorted(df['Any_Str'].unique())
    llista_mesos_num = sorted(df['Mes_Str'].unique())

    finestra_est = tk.Tk()
    finestra_est.title("Aural PRO - Panell d'Estadístiques")
    finestra_est.geometry("950x680")
    finestra_est.config(bg="#f4f4f4")

    vista_actual = tk.StringVar(value="Dia")
    fig, ax = plt.subplots(figsize=(8, 5))
    canvas = FigureCanvasTkAgg(fig, master=finestra_est)
    canvas_widget = canvas.get_tk_widget()

    def actualitzar_grafic():
        ax.clear()
        vista = vista_actual.get()
        any_triat = selector_any.get()
        mes_triat = selector_mes.get()

        df_filtrat = df[(df['Any_Str'] == any_triat) & (df['Mes_Str'] == mes_triat)].copy()
        if df_filtrat.empty:
            ax.set_title(f"No hi ha registres per a la data: {any_triat}-{mes_triat}", fontsize=12, fontweight='bold', pad=15)
            canvas.draw()
            return

        if vista == "Dia":
            grup = df_filtrat.groupby(df_filtrat['Data_Formatada'].dt.date)['Estat IA'].value_counts().unstack(fill_value=0)
            try:
                inici_mes = pd.to_datetime(f"{any_triat}-{mes_triat}-01").date()
                fi_mes = (pd.to_datetime(f"{any_triat}-{mes_triat}-01") + pd.offsets.MonthEnd(0)).date()
                tots_els_dies = pd.date_range(start=inici_mes, end=fi_mes).date
                grup = grup.reindex(tots_els_dies, fill_value=0)
            except Exception:
                pass
            titol = f"Balanç Diari del Mes de Calendari: {any_triat}-{mes_triat}"
            rotation = 45
        elif vista == "Setmana":
            df_filtrat['Setmana'] = df_filtrat['Data_Formatada'].dt.to_period('W').astype(str)
            grup = df_filtrat.groupby('Setmana')['Estat IA'].value_counts().unstack(fill_value=0)
            titol = f"Resum Setmanal del Mes: {any_triat}-{mes_triat}"
            rotation = 15
        elif vista == "Mes":
            df_filtrat['Mes'] = df_filtrat['Data_Formatada'].dt.strftime('%Y-%m')
            grup = df_filtrat.groupby('Mes')['Estat IA'].value_counts().unstack(fill_value=0)
            titol = f"Total d'aquest Mes seleccionat ({any_triat}-{mes_triat})"
            rotation = 0

        for estat in ['PRODUCTIU', 'DISTRET']:
            if estat not in grup.columns:
                grup[estat] = 0

        totals = grup.sum(axis=1)
        grup_percent = grup.div(totals.replace(0, 1), axis=0) * 100
        grup_percent.loc[totals == 0, ['PRODUCTIU', 'DISTRET']] = 0

        grup_percent.plot(kind='bar', stacked=True, ax=ax, color={'PRODUCTIU': '#2ECC71', 'DISTRET': '#E74C3C'}, width=0.6, alpha=0.9)

        ax.set_title(titol, fontsize=12, fontweight='bold', pad=15)
        ax.set_ylabel("% de Temps ocupat")
        ax.set_xlabel("")
        ax.set_ylim(0, 120)
        ax.grid(axis='y', linestyle=':', alpha=0.6)
        ax.legend(["Distret", "Productiu"], loc="upper right", ncol=2)

        etiquetes = [str(idx) for idx in grup_percent.index]
        ax.set_xticks(range(len(etiquetes)))
        ax.set_xticklabels(etiquetes, rotation=rotation, ha='right', fontsize=9)

        for i, (idx, row) in enumerate(grup_percent.iterrows()):
            if totals.iloc[i] > 0:
                prod_val = row['PRODUCTIU']
                ax.text(i, 103, f"{prod_val:.0f}%", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1E8449')

        plt.tight_layout()
        canvas.draw()

    def canviar_vista(nova_vista):
        vista_actual.set(nova_vista)
        actualitzar_grafic()

    frame_controls = tk.Frame(finestra_est, bg="#f4f4f4", pady=12)
    frame_controls.pack(fill="x")

    tk.Label(frame_controls, text="Any:", font=("Arial", 10, "bold"), bg="#f4f4f4").pack(side="left", padx=(20, 2))
    selector_any = ttk.Combobox(frame_controls, values=llista_anys, state="readonly", width=7, font=("Arial", 10))
    selector_any.set(llista_anys[-1] if llista_anys else "")
    selector_any.pack(side="left", padx=5)
    selector_any.bind("<<ComboboxSelected>>", lambda e: actualitzar_grafic())

    tk.Label(frame_controls, text="Mes:", font=("Arial", 10, "bold"), bg="#f4f4f4").pack(side="left", padx=(10, 2))
    selector_mes = ttk.Combobox(frame_controls, values=llista_mesos_num, state="readonly", width=5, font=("Arial", 10))
    selector_mes.set(llista_mesos_num[-1] if llista_mesos_num else "")
    selector_mes.pack(side="left", padx=5)
    selector_mes.bind("<<ComboboxSelected>>", lambda e: actualitzar_grafic())

    tk.Label(frame_controls, text="|", font=("Arial", 12), bg="#f4f4f4", fg="#bbb").pack(side="left", padx=15)

    tk.Button(frame_controls, text="Vista Diària", command=lambda: canviar_vista("Dia"), font=("Arial", 10, "bold"), bg="#34495E", fg="white", width=14).pack(side="left", padx=3)
    tk.Button(frame_controls, text="Vista Setmanal", command=lambda: canviar_vista("Setmana"), font=("Arial", 10, "bold"), bg="#34495E", fg="white", width=14).pack(side="left", padx=3)
    tk.Button(frame_controls, text="Vista Mensual", command=lambda: canviar_vista("Mes"), font=("Arial", 10, "bold"), bg="#34495E", fg="white", width=14).pack(side="left", padx=3)

    canvas_widget.pack(fill="both", expand=True, padx=20, pady=10)
    actualitzar_grafic()
    finestra_est.mainloop()

if __name__ == "__main__":
    mostrar_grafics()
