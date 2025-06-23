# POSシステム Backend API

## Render.com デプロイ手順

### 1. Renderアカウント作成
- [Render.com](https://render.com)でアカウントを作成

### 2. GitHubリポジトリの接続
- Renderダッシュボードで「New Web Service」を選択
- GitHubリポジトリを選択・接続

### 3. 環境変数の設定
Renderダッシュボードで以下の環境変数を設定:
- `DB_USER`: データベースのユーザー名
- `DB_PASSWORD`: データベースのパスワード  
- `DB_HOST`: データベースのホスト名
- `DB_PORT`: データベースのポート番号（通常3306）
- `DB_NAME`: データベース名

### 4. デプロイ設定
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Environment: `Python 3`

## ローカル開発

### 環境設定
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集してデータベース情報を設定

# サーバー起動
uvicorn app:app --reload
```

## API エンドポイント
- `/docs` - Swagger UI
- `/system/health` - ヘルスチェック
- その他のエンドポイントはSwagger UIで確認可能

## Githubリポジトリの初期化→プッシュまで

### 1. カレントディレクトリをGitリポジトリとして初期化
git init

### 2. ファイルをステージングエリアに追加
git add .

### 3. 初期コミットを作成
git commit -m "Initial commit"

### 4. リモートリポジトリのURLを追加（URLは実際のものに置き換えてください）
git remote add origin your-repository-url

### 5. ローカルのmainブランチをリモートにプッシュ
git push -u origin main
