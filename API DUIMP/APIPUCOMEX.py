from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
import requests

# Caminho para o arquivo .pfx e senha
PFX_FILE = r"C:\\Users\\fcherpin\\OneDrive - Donaldson Company, Inc\\Documents\\Certificado Digital\\certificadoFelipe.pfx"
PFX_PASSWORD = b"964180"

# Carregar o certificado e a chave privada
with open(PFX_FILE, "rb") as pfx_file:
    pfx_data = pfx_file.read()

private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
    pfx_data, PFX_PASSWORD, default_backend()
)

# Converter os objetos em PEM (opcional)
from cryptography.hazmat.primitives import serialization

cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
key_pem = private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL,
    serialization.NoEncryption(),
)

# Salvar em arquivos temporários ou usar diretamente
with open("certificado.pem", "wb") as cert_file:
    cert_file.write(cert_pem)

with open("chave-privada.pem", "wb") as key_file:
    key_file.write(key_pem)

# Endpoint de autenticação
url = "https://val.portalunico.siscomex.gov.br/portal/api/autenticar"

# Cabeçalhos para a autenticação
headers = {
    "Role-Type": "IMPEXP",
}

# Usar os arquivos convertidos
response = requests.post(
    url,
    headers=headers,
    cert=("certificado.pem", "chave-privada.pem"),
    verify="ca-bundle.crt",
)

print(response.status_code)
print(response.text)
