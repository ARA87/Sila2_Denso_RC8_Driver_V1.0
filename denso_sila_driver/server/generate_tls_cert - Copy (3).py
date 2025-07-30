# generate_tls_cert.py
import subprocess
import os

def generate_self_signed_cert(cert_path="cert.pem", key_path="key.pem"):
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"✅ Zertifikat und Schlüssel existieren bereits: {cert_path}, {key_path}")
        return

    print("🔐 Erzeuge selbstsigniertes Zertifikat (TLS)...")
    
    config_path = os.path.join(os.path.dirname(__file__), "openssl.cnf")

    cmd = [
        "openssl", "req", "-x509",
        "-newkey", "rsa:4096",
        "-sha256",
        "-days", "365",
        "-nodes",
        "-keyout", key_path,
        "-out", cert_path,
        "-config", "openssl.cnf",
        "-extensions", "v3_req"
        
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Zertifikat erstellt: {cert_path}")
        print(f"🔑 Schlüssel erstellt: {key_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Fehler beim Erzeugen des Zertifikats:", e)
        print("💡 Stelle sicher, dass OpenSSL installiert ist und im PATH liegt.")

if __name__ == "__main__":
    generate_self_signed_cert()
