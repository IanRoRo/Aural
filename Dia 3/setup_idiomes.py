import argostranslate.package
import ssl

def instal_lar_traductor_local():
    print("🔄 Intentant connectar amb el servidor d'Argos...")
    
    # Això arregla errors comuns de certificats SSL a Windows
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        # Intentem actualitzar l'índex
        argostranslate.package.update_package_index()
        print("✅ Índex actualitzat correctament.")
    except Exception as e:
        print(f"❌ No s'ha pogut actualitzar l'índex: {e}")
        print("💡 Intentarem continuar amb el que hi hagi en memòria...")

    # Obtenim paquets
    paquets_disponibles = argostranslate.package.get_available_packages()
    combinacions = [("ca", "en"), ("en", "ca")]
    
    for origen, desti in combinacions:
        print(f"📥 Buscant paquet: {origen} -> {desti}...")
        paquet = next(
            filter(lambda x: x.from_code == origen and x.to_code == desti, paquets_disponibles), 
            None
        )
        
        if paquet:
            print(f"📦 Instal·lant {origen}-{desti}... No toquis res, pot trigar un minut.")
            try:
                argostranslate.package.install_from_path(paquet.download())
                print(f"✅ {origen}-{desti} instal·lat.")
            except Exception as e:
                print(f"❌ Error descarregant el paquet: {e}")
        else:
            print(f"❌ No s'ha trobat la combinació {origen}->{desti}. Revisa la connexió.")

if __name__ == "__main__":
    instal_lar_traductor_local()
    print("\n🚀 Procés finalitzat.")