from sqlalchemy import create_engine
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
base_path = Path(__file__).parents[1]  # backendディレクトリへのパス
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# SSL証明書のパス（存在する場合のみ使用）
ssl_cert = str(base_path / 'DigiCertGlobalRootCA.crt.pem')

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT') 
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SSL証明書が存在する場合のみSSL設定を追加
connect_args = {}
if os.path.exists(ssl_cert):
    connect_args = {
        "ssl": {
            "ssl_ca": ssl_cert
        }
    }

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

print("Current working directory:", os.getcwd())
print("Certificate file exists:", os.path.exists(ssl_cert))
print("Environment file exists:", os.path.exists(env_path))
print("Database URL (without password):", DATABASE_URL.replace(DB_PASSWORD, "****"))
