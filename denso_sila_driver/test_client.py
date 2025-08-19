import asyncio
from sila2.client import SilaClient
import time 

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
    
    client.DensoRC8Control.SetIValue(Index=10, Value=500)
    response = client.DensoRC8Control.GetIValue(Index=10)
    print(f"📥 Aktueller I10-Wert: {response.Value}")
    
    client.DensoRC8Control.SetFValue(Index=30, Value=30.5)
    response = client.DensoRC8Control.GetFValue(Index=30)
    print(f"📥 Aktueller F30-Wert: {response.Value}")
    
    print("✍️ Setze S31-Wert auf 123jj...")
    client.DensoRC8Control.SetSValue(Index=31, Value="123jj")
    
    p_value = [35, 15, 0, 5, 1, 8, -3]
    print("✍️ Setze P31-Wert auf P(35,15,0,5,1,8,-3)")
    client.DensoRC8Control.SetPValue(Index=31, Value=p_value)
        # 4️⃣ Wert auslesen
    print("🔎 Lese aktuellen P31-Wert...")
    response = client.DensoRC8Control.GetPValue(Index=31)
    print(f"📥 Aktueller P31-Wert: {response.Value}")
    
    j_value = [35, 15, 120, 5, 1, 8, -20,80]
    print("✍️ Setze j31-Wert auf J(35, 15, 120, 5, 1, 8, -20,80)")
    client.DensoRC8Control.SetJValue(Index=31, Value=j_value)
    
    print("🔎 Lese aktuellen J31-Wert...")
    response = client.DensoRC8Control.GetJValue(Index=31)
    print(f"📥 Aktueller J31-Wert: {response.Value}")

    v_value = [35, 15, 120]
    print("✍️ Setze V1-Wert auf V(35, 15, 120)")
    client.DensoRC8Control.SetVValue(Index=1, Value=v_value)
    
    print("🔎 Lese aktuellen V1-Wert...")
    response = client.DensoRC8Control.GetVValue(Index=1)
    print(f"📥 Aktueller V1-Wert: {response.Value}")


    print("✍️ Setze S53-Wert auf 123...")
    client.DensoRC8Control.SetSValue(Index=30, Value="123")

    response = client.DensoRC8Control.GetProgram(ProgramName="Pro2")
    print(f"📥 Aktuelles Programm: Pro1")
    
    

    # 3️⃣b Programm starten (neuer Command)
    print("▶️ Starte Programm 'Pro1' im Modus 'one_cycle' ...")
    client.DensoRC8Control.StartProgram(ProgramName="Pro2", Mode="one_cycle")
    
    time.sleep(5)
    
    print("🔎 Lese aktuellen Pos-Wert...")
    response = client.DensoRC8Control.GetPosValue()
    print(response)
    
        # 3️⃣b Programm stoppen (neuer Command)
    print("▶️ stoppe Programm 'Pro1' im Modus 'step_stop' ...")
    client.DensoRC8Control.StopProgram(ProgramName="Pro1", Mode="step_stop")

    # 4️⃣ Wert auslesen
    print("🔎 Lese aktuellen S10-Wert...")
    response = client.DensoRC8Control.GetSValue(Index=30)
    print(f"📥 Aktueller S10-Wert: {response.Value}")

if __name__ == "__main__":
    asyncio.run(main())
