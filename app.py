from fastapi import FastAPI, HTTPException, Query, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
import requests
import json
from datetime import datetime, date
from db_control import crud, mymodels
from db_control.connect import engine
from db_control.create_tables import init_db

# アプリケーション初期化時にテーブルを作成
init_db()

# Pydanticモデル定義（実際のDBテーブル構造に対応）
class ProductBase(BaseModel):
    code: str = Field(..., description="商品コード（JANコード）", examples=["4549995294989"])
    name: str = Field(..., description="商品名", examples=["iPhone 15 Pro 128GB ナチュラルチタニウム"])
    price: int = Field(..., description="商品価格（税込み）", examples=[159800])

class ProductCreate(ProductBase):
    class Config:
        schema_extra = {
            "example": {
                "code": "4549995294989",
                "name": "iPhone 15 Pro 128GB ナチュラルチタニウム",
                "price": 159800
            }
        }

class ProductUpdate(BaseModel):
    code: Optional[str] = Field(None, description="商品コード")
    name: Optional[str] = Field(None, description="商品名")
    price: Optional[int] = Field(None, description="商品価格")

class ProductResponse(ProductBase):
    prd_id: int = Field(..., description="商品ID")
    
    class Config:
        from_attributes = True

class ProductInfo(BaseModel):
    prd_code: str = Field(..., description="商品コード", examples=["4549995294989"])
    quantity: int = Field(1, description="数量", examples=[1])

class TransactionCreate(BaseModel):
    emp_cd: str = Field(..., description="従業員コード", examples=["EMP001"])
    products: List[ProductInfo] = Field(..., description="商品リスト")
    
    class Config:
        schema_extra = {
            "example": {
                "emp_cd": "EMP001",
                "products": [
                    {
                        "prd_code": "4549995294989",
                        "quantity": 1
                    },
                    {
                        "prd_code": "4549995294996",
                        "quantity": 2
                    }
                ]
            }
        }

class TransactionResponse(BaseModel):
    trd_id: int
    datetime: datetime
    emp_cd: str
    store_cd: str
    pos_no: str
    total_amt: int
    
    class Config:
        from_attributes = True

class TransactionDetailResponse(BaseModel):
    trd_id: int
    dtl_id: int
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int
    
    class Config:
        from_attributes = True

# データベースセッション取得
def get_db():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="テクワンPOSシステム API",
    description="Jastec株式会社 POSシステム API - 商品マスタ、取引管理、売上レポート機能を提供",
    version="1.0.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {
        "message": "テクワンPOSシステム API へようこそ！",
        "version": "1.0.0",
        "database": "possystem",
        "tables": ["product_master", "transaction", "transaction_detail"]
    }

# 商品マスタ関連エンドポイント
@app.post("/products", response_model=dict, tags=["商品マスタ"])
def create_product(product: Annotated[ProductCreate, Body(
    examples=[
        {
            "code": "4549995294989",
            "name": "iPhone 15 Pro 128GB ナチュラルチタニウム",
            "price": 159800
        }
    ]
)]):
    """商品マスタに新規商品を登録"""
    try:
        values = product.dict()
        result = crud.insert_product(values)
        
        # 登録された商品を取得して返却
        product_data = crud.select_product_by_code(values["code"])
        if not product_data:
            raise HTTPException(status_code=500, detail="商品登録に失敗しました")
        
        return {"status": "success", "data": json.loads(product_data), "message": "商品が正常に登録されました"}
    except Exception as e:
        print(f"商品登録エラー: {e}")
        raise HTTPException(status_code=400, detail=f"商品登録エラー: {str(e)}")

@app.get("/products/{product_code}", response_model=dict, tags=["商品マスタ"])
def get_product_by_code(product_code: str):
    """商品コードで商品情報を取得（POSの基本機能）"""
    result = crud.select_product_by_code(product_code)
    if not result:
        raise HTTPException(status_code=404, detail=f"商品コード {product_code} が見つかりません")
    
    return {"status": "success", "data": json.loads(result)}

@app.get("/products", response_model=dict, tags=["商品マスタ"])
def get_all_products():
    """全商品一覧を取得"""
    result = crud.select_all_products()
    if not result:
        return {"status": "success", "data": [], "message": "登録されている商品がありません"}
    
    return {"status": "success", "data": json.loads(result)}

@app.put("/products/{prd_id}", response_model=dict, tags=["商品マスタ"])
def update_product(prd_id: int, product: ProductUpdate):
    """商品情報を更新"""
    try:
        values = product.dict(exclude_unset=True)
        if not values:
            raise HTTPException(status_code=400, detail="更新するデータが指定されていません")
        
        values["prd_id"] = prd_id
        result = crud.update_product(values)
        
        return {"status": "success", "message": f"商品ID {prd_id} の情報を更新しました"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"商品更新エラー: {str(e)}")

@app.delete("/products/{prd_id}", response_model=dict, tags=["商品マスタ"])
def delete_product(prd_id: int):
    """商品を削除"""
    try:
        result = crud.delete_product(prd_id)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"商品削除エラー: {str(e)}")

# 商品検索エンドポイント
@app.get("/products/search/{search_term}", response_model=dict, tags=["商品マスタ"])
def search_products(search_term: str):
    """商品名による部分一致検索"""
    result = crud.search_products_by_name(search_term)
    if not result:
        return {"status": "success", "data": [], "message": f"'{search_term}' に該当する商品が見つかりません"}
    
    return {"status": "success", "data": json.loads(result)}

# 取引関連エンドポイント
@app.post("/transactions", response_model=dict, tags=["取引管理"])
def create_transaction(transaction: Annotated[TransactionCreate, Body(
    openapi_examples={
        "single_product": {
            "summary": "単一商品の取引",
            "description": "1つの商品を1個購入する場合",
            "value": {
                "emp_cd": "EMP001",
                "products": [
                    {
                        "prd_code": "4549995294989",
                        "quantity": 1
                    }
                ]
            }
        },
        "multiple_products": {
            "summary": "複数商品の取引",
            "description": "複数の商品を購入する場合",
            "value": {
                "emp_cd": "EMP001",
                "products": [
                    {
                        "prd_code": "4549995294989",
                        "quantity": 1
                    },
                    {
                        "prd_code": "4549995294996",
                        "quantity": 2
                    }
                ]
            }
        }
    }
)]):
    """完全な取引処理（取引+明細の同時処理）"""
    try:
        print(f"受信した取引データ: {transaction.dict()}")
        
        emp_cd = transaction.emp_cd
        products_info = transaction.products
        
        if not products_info:
            raise HTTPException(status_code=400, detail="商品が指定されていません")
        
        # 商品情報の検証と取得
        validated_products = []
        for product_info in products_info:
            product_code = product_info.prd_code
            quantity = product_info.quantity
            
            if quantity <= 0:
                raise HTTPException(status_code=400, detail="数量は1以上である必要があります")
            
            # 商品マスタから商品情報を取得
            product_data = crud.select_product_by_code(product_code)
            if not product_data:
                raise HTTPException(status_code=404, detail=f"商品コード {product_code} が見つかりません")
            
            product_obj = json.loads(product_data)
            
            # 数量分だけ商品を追加
            for _ in range(quantity):
                validated_products.append({
                    "prd_id": product_obj["prd_id"],
                    "prd_code": product_obj["code"],
                    "prd_name": product_obj["name"],
                    "prd_price": product_obj["price"]
                })
        
        # 取引処理実行
        result = crud.complete_transaction(emp_cd, validated_products)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return {"status": "success", "data": result, "message": "取引が正常に完了しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"取引処理エラー: {e}")
        raise HTTPException(status_code=400, detail=f"取引処理エラー: {str(e)}")

@app.get("/transactions/{transaction_id}/details", response_model=dict, tags=["取引管理"])
def get_transaction_details(transaction_id: int):
    """指定取引IDの明細データを取得"""
    result = crud.select_transaction_details(transaction_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"取引ID {transaction_id} の明細が見つかりません")
    
    return {"status": "success", "data": json.loads(result)}

@app.get("/transactions/date/{target_date}", response_model=dict, tags=["取引管理"])
def get_transactions_by_date(target_date: str):
    """指定日の取引データを取得"""
    try:
        # 日付形式の検証
        datetime.strptime(target_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="日付形式が正しくありません (YYYY-MM-DD)")
    
    result = crud.select_transactions_by_date(target_date)
    if not result:
        return {"status": "success", "data": [], "message": f"{target_date} の取引データがありません"}
    
    return {"status": "success", "data": json.loads(result)}

@app.get("/transactions", response_model=dict, tags=["取引管理"])
def get_all_transactions():
    """全取引データを取得"""
    result = crud.select_all_transactions()
    if not result:
        return {"status": "success", "data": [], "message": "取引データがありません"}
    
    return {"status": "success", "data": json.loads(result)}

# 売上レポート関連エンドポイント
@app.get("/reports/daily/{target_date}", response_model=dict, tags=["売上レポート"])
def get_daily_sales_report(target_date: str):
    """日次売上レポートを取得"""
    try:
        # 日付形式の検証
        datetime.strptime(target_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="日付形式が正しくありません (YYYY-MM-DD)")
    
    result = crud.get_daily_sales_report(target_date)
    if not result:
        return {
            "status": "success", 
            "data": {
                "date": target_date, 
                "total_sales": 0, 
                "transaction_count": 0, 
                "product_sales": []
            },
            "message": f"{target_date} の売上データがありません"
        }
    
    return {"status": "success", "data": json.loads(result)}

@app.get("/reports/product-summary", response_model=dict, tags=["売上レポート"])
def get_product_sales_summary():
    """商品別売上集計を取得"""
    result = crud.get_product_sales_summary()
    if not result:
        return {"status": "success", "data": [], "message": "売上データがありません"}
    
    return {"status": "success", "data": json.loads(result)}

# POSシステム専用エンドポイント
@app.post("/pos/checkout", response_model=dict, tags=["POSシステム"])
def pos_checkout(transaction: TransactionCreate):
    """POSレジでの会計処理"""
    try:
        print(f"=== デバッグ情報 ===")
        print(f"受信データ: {transaction}")
        print(f"emp_cd: {transaction.emp_cd}")
        print(f"products: {transaction.products}")
        print(f"products型: {type(transaction.products)}")
        
        # 各商品の詳細をチェック
        for i, product in enumerate(transaction.products):
            print(f"商品{i+1}: {product}")
            print(f"  prd_code: {product.prd_code}")
            print(f"  quantity: {product.quantity}")
        
        return create_transaction(transaction)
    except Exception as e:
        print(f"エラー詳細: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"処理エラー: {str(e)}")

@app.get("/pos/product-lookup/{product_code}", response_model=dict, tags=["POSシステム"])
def pos_product_lookup(product_code: str):
    """POSでの商品コード読み込み機能"""
    return get_product_by_code(product_code)

@app.get("/pos/barcode-scan/{barcode}", response_model=dict, tags=["POSシステム"])
def pos_barcode_scan(barcode: str):
    """バーコードスキャン機能"""
    result = crud.select_product_by_code(barcode)
    if not result:
        raise HTTPException(status_code=404, detail=f"バーコード {barcode} の商品が見つかりません")
    
    product_data = json.loads(result)
    return {
        "status": "success",
        "data": product_data,
        "message": f"商品をスキャンしました: {product_data['name']}"
    }

# システム管理用エンドポイント
@app.get("/system/health", response_model=dict, tags=["システム管理"])
def system_health():
    """システムヘルスチェック"""
    try:
        # データベース接続テスト
        test_result = crud.select_all_products()
        db_status = "connected" if test_result is not None else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": db_status,
        "version": "1.0.0",
        "tables": {
            "product_master": "商品マスタテーブル",
            "transaction": "取引テーブル", 
            "transaction_detail": "取引明細テーブル"
        }
    }

@app.get("/system/stats", response_model=dict, tags=["システム管理"])
def system_stats():
    """システム統計情報"""
    try:
        products = crud.select_all_products()
        transactions = crud.select_all_transactions()
        
        product_count = len(json.loads(products)) if products else 0
        transaction_count = len(json.loads(transactions)) if transactions else 0
        
        return {
            "status": "success",
            "data": {
                "total_products": product_count,
                "total_transactions": transaction_count,
                "database_name": "possystem",
                "last_updated": datetime.now()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"統計情報取得エラー: {str(e)}")

# テスト用エンドポイント
@app.get("/fetchtest", response_model=dict, tags=["テスト"])
def fetchtest():
    """外部API接続テスト"""
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/users')
        return {"status": "success", "data": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"外部API接続エラー: {str(e)}")

# デバッグ用エンドポイント
@app.get("/debug/database-structure", response_model=dict, tags=["デバッグ"])
def debug_database_structure():
    """データベース構造確認用（開発時のみ使用）"""
    return {
        "status": "success",
        "data": {
            "database": "possystem",
            "tables": {
                "product_master": {
                    "columns": ["prd_id", "code", "name", "price"],
                    "description": "商品マスタテーブル - 商品情報を管理"
                },
                "transaction": {
                    "columns": ["trd_id", "datetime", "emp_cd", "store_cd", "pos_no", "total_amt"],
                    "description": "取引テーブル - 取引の基本情報を管理"
                },
                "transaction_detail": {
                    "columns": ["trd_id", "dtl_id", "prd_id", "prd_code", "prd_name", "prd_price"],
                    "description": "取引明細テーブル - 取引の商品明細を管理"
                }
            }
        }
    }

# エラーハンドリング
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"status": "error", "message": "リソースが見つかりません", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"status": "error", "message": "内部サーバーエラーが発生しました", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
