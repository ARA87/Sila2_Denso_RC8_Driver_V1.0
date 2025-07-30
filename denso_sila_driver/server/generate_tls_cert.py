import argparse
import uuid
import ipaddress
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ObjectIdentifier
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_cert(uuid_str: str, ip_address: str, cert_file: str, key_file: str):
    sila_uuid_oid = ObjectIdentifier("1.3.6.1.4.1.58583")

    # Generiere privaten Schlüssel
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Erstelle Subject und Issuer (selbstsigniert)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Example Org"),
        x509.NameAttribute(NameOID.COMMON_NAME, ip_address),
    ])

    # San extension (Subject Alternative Name)
    san = x509.SubjectAlternativeName([
        x509.IPAddress(ipaddress.IPv4Address(ip_address))
    ])

    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(san, critical=False)
        .add_extension(
            x509.UnrecognizedExtension(
                sila_uuid_oid,
                uuid_str.encode("ascii")  # 💡 WICHTIG: als ASCII, nicht UUID.bytes!
            ),
            critical=False
        )
    )

    cert = cert_builder.sign(key, hashes.SHA256(), default_backend())

    # Schreibe Zertifikat
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    # Schreibe privaten Schlüssel
    with open(key_file, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print(f"\n✅ Zertifikat und Schlüssel wurden erfolgreich erzeugt.")
    print(f"🔐 UUID im Zertifikat: {uuid_str}")
    print(f"📄 Zertifikat: {cert_file}")
    print(f"🔑 Schlüssel:    {key_file}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SiLA2-compatible TLS certificate with UUID")
    parser.add_argument("--uuid", required=False, help="UUID to include in certificate. If not provided, a random one will be used.")
    parser.add_argument("--host", default="127.0.0.1", help="IP address of the server (default: 127.0.0.1)")
    parser.add_argument("--cert", default="cert.pem", help="Output certificate file (default: cert.pem)")
    parser.add_argument("--key", default="key.pem", help="Output private key file (default: key.pem)")
    args = parser.parse_args()

    if args.uuid:
        try:
            uuid_obj = uuid.UUID(args.uuid)
            uuid_str = str(uuid_obj)
        except ValueError:
            raise ValueError("❌ Ungültige UUID angegeben.")
    else:
        uuid_str = str(uuid.uuid4())

    generate_cert(uuid_str, args.host, args.cert, args.key)
