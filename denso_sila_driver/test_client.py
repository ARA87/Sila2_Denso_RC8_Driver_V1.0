import asyncio
from sila2.client import SilaClient
import time

async def main():
    # 🔐 Load root certificate (cert.pem from the server)
    with open("server/cert.pem", "rb") as f:
        root_cert = f.read()

    # 🔌 Establish TLS-secured connection to the SiLA2 server
    client = SilaClient("127.0.0.1", 50100, root_certs=root_cert)

    # 📋 Display list of implemented features
    print("Implemented Features:")
    features = client.SiLAService.ImplementedFeatures.get()
    for feature in features:
        print(f"- {feature}")

    # 1️⃣ Configure connection to the controller
    print("📡 Configuring connection to the controller...")
    client.DensoRC8Control.ConfigureConnection(
        IPAddress="127.0.0.1",  # ← adjust if necessary
        Port=5007,
        Timeout=2000
    )

    # 2️⃣ Start connection
    print("🚀 Starting connection...")
    client.DensoRC8Control.Start()

    # 3️⃣ Set values
    print("✍️ Setting S30 value to '123'...")
    client.DensoRC8Control.SetSValue(Index=30, Value="123")

    client.DensoRC8Control.SetIValue(Index=10, Value=500)
    response = client.DensoRC8Control.GetIValue(Index=10)
    print(f"📥 Current I10 value: {response.Value}")

    client.DensoRC8Control.SetFValue(Index=30, Value=30.5)
    response = client.DensoRC8Control.GetFValue(Index=30)
    print(f"📥 Current F30 value: {response.Value}")

    print("✍️ Setting S31 value to '123jj'...")
    client.DensoRC8Control.SetSValue(Index=31, Value="123jj")

    p_value = [35, 15, 0, 5, 1, 8, -3]
    print("✍️ Setting P31 value to P(35,15,0,5,1,8,-3)...")
    client.DensoRC8Control.SetPValue(Index=31, Value=p_value)

    # 4️⃣ Read value
    print("🔎 Reading current P31 value...")
    response = client.DensoRC8Control.GetPValue(Index=31)
    print(f"📥 Current P31 value: {response.Value}")

    j_value = [35, 15, 120, 5, 1, 8, -20, 80]
    print("✍️ Setting J31 value to J(35,15,120,5,1,8,-20,80)...")
    client.DensoRC8Control.SetJValue(Index=31, Value=j_value)

    print("🔎 Reading current J31 value...")
    response = client.DensoRC8Control.GetJValue(Index=31)
    print(f"📥 Current J31 value: {response.Value}")

    v_value = [35, 15, 120]
    print("✍️ Setting V1 value to V(35,15,120)...")
    client.DensoRC8Control.SetVValue(Index=1, Value=v_value)

    print("🔎 Reading current V1 value...")
    response = client.DensoRC8Control.GetVValue(Index=1)
    print(f"📥 Current V1 value: {response.Value}")

    print("✍️ Setting S53 value to '123'...")
    client.DensoRC8Control.SetSValue(Index=30, Value="123")

    response = client.DensoRC8Control.GetProgram(ProgramName="Pro2")
    print(f"📥 Current program: Pro1")

    # 3️⃣b Start program (new command)
    print("▶️ Starting program 'Pro1' in mode 'one_cycle'...")
    client.DensoRC8Control.StartProgram(ProgramName="Pro2", Mode="one_cycle")

    time.sleep(5)

    print("🔎 Reading current position value...")
    response = client.DensoRC8Control.GetPosValue()
    print(response)

    # 3️⃣b Stop program (new command)
    print("▶️ Stopping program 'Pro1' in mode 'step_stop'...")
    client.DensoRC8Control.StopProgram(ProgramName="Pro1", Mode="step_stop")

    # 4️⃣ Read value
    print("🔎 Reading current S10 value...")
    response = client.DensoRC8Control.GetSValue(Index=30)
    print(f"📥 Current S10 value: {response.Value}")

if __name__ == "__main__":
    asyncio.run(main())
