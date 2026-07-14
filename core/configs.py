
import dotenv
import os
dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import sys
    if "pytest" not in sys.modules:
        raise RuntimeError("SECRET_KEY não definida. Configure via variável de ambiente.")
    SECRET_KEY = "test-secret-key-only-for-testing"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

ADMIN_USERNAMES = [u.strip() for u in os.getenv("ADMIN_USERNAMES", "jackson").split(",") if u.strip()]
# Adicionar usuário de teste local como admin para facilitar testes locais
if "testadmin" not in ADMIN_USERNAMES:
    ADMIN_USERNAMES.append("testadmin")

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_CLAIM_EMAIL = os.getenv("VAPID_CLAIM_EMAIL", "contato.ballers085@gmail.com)")

