from sqlalchemy import create_engine
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
base_path = Path(__file__).parents[1]  # backendディレクトリへのパス
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# データベース接続情報（デフォルト値付き）
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'postgres')

# 環境変数の検証
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is required")

# PostgreSQLのURL構築
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Supabase用のSSL設定
connect_args = {
    "sslmode": "require"
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
print("Environment file exists:", os.path.exists(env_path))
print("Database URL (without password):", DATABASE_URL.replace(DB_PASSWORD, "****"))
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_NAME: {DB_NAME}")
print(f"DB_USER: {DB_USER}")
