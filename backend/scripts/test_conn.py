import psycopg2
from sqlalchemy.engine import make_url
from app.core.config import settings

u = make_url(settings.DATABASE_URL)
print("host:", u.host, "| porta:", u.port, "| usuario:", u.username, "| banco:", u.database)

try:
    psycopg2.connect(
        host=u.host, port=u.port, user=u.username,
        password=u.password, dbname=u.database,
    )
    print("OK, conectou")
except UnicodeDecodeError as e:
    print("ERRO REAL DO SERVIDOR:", e.object.decode("cp1252", errors="replace"))