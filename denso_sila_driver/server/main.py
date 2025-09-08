# server/main.py

import sys
import os
import uuid
import asyncio


base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# driver path
driver_path = os.path.join(base_path, "driver")
if driver_path not in sys.path:
    sys.path.insert(0, driver_path)

# Imports
from sila2.server import SilaServer
from sila2.framework.feature import Feature
from implementation.denso_rc8_feature_impl import DensoRC8Feature


async def main():
    # path to feature xml
    feature_path = os.path.join(base_path, "features", "DensoRC8Control.sila.xml")
    feature = Feature(feature_path)

    # Create SiLA2-Server
    server = SilaServer(
        server_name="DensoRC8",
        server_type="RobotController",
        server_description="SiLA 2 Server for Denso RC8 using bcapclient",
        server_version="1.0.0",
        server_vendor_url="https://https://www.densorobotics-europe.com/",  
        server_uuid="78e7306b-4aef-4c70-857c-87e0d2f4e32f"
    )

    # Feature-Implemention register
    server.set_feature_implementation(feature, DensoRC8Feature(parent_server=server))

    # Load TLS-Certificate and key 
    cert_path = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_path = os.path.join(os.path.dirname(__file__), "key.pem")
    with open(cert_path, "rb") as cert_file:
        cert_chain = cert_file.read()
    with open(key_path, "rb") as key_file:
        private_key = key_file.read()

    # Start TLS-Server starten
    server.start(
        address="0.0.0.0",
        port=50100,
        cert_chain=cert_chain,
        private_key=private_key,
        enable_discovery=False 
    )

    print("✅ SiLA2 Server running on 0.0.0.0:50100")

    # Server running
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

