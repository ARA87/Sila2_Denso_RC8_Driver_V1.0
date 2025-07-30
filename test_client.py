# test_client.py
import asyncio
from sila2.client import SilaClient

async def main():
    # 🔐 Lade Root-Zertifikat (cert.pem vom Server)
    with open("server/cert.pem", "rb") as f:
        root_cert = f.read()

    # 🔌 TLS-gesicherte Verbindung mit dem SiLA2-Server
    client = SilaClient("127.0.0.1", 50100, root_certs=root_cert)

    # 📋 Liste der implementierten Features anzeigen
    print("Implementierte Features:")
    features = client.SiLAService.ImplementedFeatures.get()
    for feature in features:
        print(f"- {feature}")

    # 1️⃣ Verbindung konfigurieren (IP, Port, Timeout)
    print("📡 Konfiguriere Verbindung zum Controller...")
    client.DensoRC8Control.ConfigureConnection(
        IPAddress="127.0.0.1",  # ← ggf. anpassen
        Port=5007,
        Timeout=2000
    )

    # 2️⃣ Verbindung starten
    print("🚀 Starte Verbindung...")
    client.DensoRC8Control.Start()

    # 3️⃣ Mehrere Werte setzen
    print("✍️ Setze S30-Wert auf 123...")
    client.DensoRC8Control.SetSValue(Index=30, Value="123")

    print("✍️ Setze S31-Wert auf 123jj...")
    client.DensoRC8Control.SetSValue(Index=31, Value="123jj")

    print("✍️ Setze S53-Wert auf 123...")
    client.DensoRC8Control.SetSValue(Index=53, Value="123")

    # 4️⃣ Wert auslesen
    print("🔎 Lese aktuellen S10-Wert...")
    response = client.DensoRC8Control.GetSValue(Index=10)
    print(f"📥 Aktueller S10-Wert: {response.Value}")

if __name__ == "__main__":
    asyncio.run(main())
