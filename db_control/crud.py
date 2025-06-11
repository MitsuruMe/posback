# uname() error回避
import platform
print("platform", platform.uname())

from sqlalchemy import create_engine, insert, delete, update, select
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import json
import pandas as pd
from datetime import datetime

from db_control.connect import engine
from db_control.mymodels import Product
from db_control.mymodels import Transaction
from db_control.mymodels import TransactionDetail

# 商品マスタ操作関数
def insert_product(values):
    """商品マスタにデータを挿入"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    query = insert(Product).values(values)
    try:
        with session.begin():
            result = session.execute(query)
            print(f"商品が正常に登録されました: {values}")
    except sqlalchemy.exc.IntegrityError as e:
        print(f"商品登録に失敗しました（一意制約違反）: {e}")
        session.rollback()
    except Exception as e:
        print(f"商品登録でエラーが発生しました: {e}")
        session.rollback()
    finally:
        session.close()
    return "商品登録完了"

def select_product_by_code(product_code):
    """商品コードで商品情報を検索"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = session.query(Product).filter(Product.code == product_code)
            result = query.first()
            
        if result:
            product_dict = {
                "prd_id": result.prd_id,
                "code": result.code,
                "name": result.name,
                "price": result.price
            }
            return json.dumps(product_dict, ensure_ascii=False)
        else:
            return None
    except Exception as e:
        print(f"商品検索でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

def select_all_products():
    """全商品情報を取得"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = select(Product)
            df = pd.read_sql_query(query, con=engine)
            result_json = df.to_json(orient='records', force_ascii=False)
        return result_json
    except Exception as e:
        print(f"商品一覧取得でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

def update_product(values):
    """商品情報を更新"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    prd_id = values.pop("prd_id")
    
    query = update(Product).where(Product.prd_id == prd_id).values(values)
    try:
        with session.begin():
            result = session.execute(query)
            print(f"商品ID {prd_id} の情報を更新しました")
    except sqlalchemy.exc.IntegrityError as e:
        print(f"商品更新に失敗しました（一意制約違反）: {e}")
        session.rollback()
    except Exception as e:
        print(f"商品更新でエラーが発生しました: {e}")
        session.rollback()
    finally:
        session.close()
    return "商品更新完了"

def delete_product(prd_id):
    """商品を削除"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    query = delete(Product).where(Product.prd_id == prd_id)
    try:
        with session.begin():
            result = session.execute(query)
            print(f"商品ID {prd_id} を削除しました")
    except sqlalchemy.exc.IntegrityError as e:
        print(f"商品削除に失敗しました（外部キー制約違反）: {e}")
        session.rollback()
    except Exception as e:
        print(f"商品削除でエラーが発生しました: {e}")
        session.rollback()
    finally:
        session.close()
    return f"商品ID {prd_id} は削除されました"

# 取引テーブル操作関数
def insert_transaction(values):
    """取引データを挿入"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 現在日時を自動設定
    if 'datetime' not in values:
        values['datetime'] = datetime.now()
    
    query = insert(Transaction).values(values)
    try:
        with session.begin():
            result = session.execute(query)
            # 挿入されたIDを取得
            transaction_id = result.inserted_primary_key[0]
            print(f"取引が正常に登録されました。取引ID: {transaction_id}")
            return transaction_id
    except sqlalchemy.exc.IntegrityError as e:
        print(f"取引登録に失敗しました（一意制約違反）: {e}")
        session.rollback()
        return None
    except Exception as e:
        print(f"取引登録でエラーが発生しました: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def select_transactions_by_date(target_date):
    """指定日の取引データを取得"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = session.query(Transaction).filter(
                sqlalchemy.func.date(Transaction.datetime) == target_date
            )
            results = query.all()
            
        result_list = []
        for transaction in results:
            result_list.append({
                "trd_id": transaction.trd_id,
                "datetime": str(transaction.datetime),
                "emp_cd": transaction.emp_cd,
                "store_cd": transaction.store_cd,
                "pos_no": transaction.pos_no,
                "total_amt": transaction.total_amt
            })
        
        return json.dumps(result_list, ensure_ascii=False)
    except Exception as e:
        print(f"取引データ取得でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

def select_all_transactions():
    """全取引データを取得"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = select(Transaction)
            df = pd.read_sql_query(query, con=engine)
            result_json = df.to_json(orient='records', force_ascii=False)
        return result_json
    except Exception as e:
        print(f"取引一覧取得でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

# 取引明細テーブル操作関数
def insert_transaction_detail(values):
    """取引明細データを挿入"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    query = insert(TransactionDetail).values(values)
    try:
        with session.begin():
            result = session.execute(query)
            print(f"取引明細が正常に登録されました: {values}")
    except sqlalchemy.exc.IntegrityError as e:
        print(f"取引明細登録に失敗しました（一意制約違反）: {e}")
        session.rollback()
    except Exception as e:
        print(f"取引明細登録でエラーが発生しました: {e}")
        session.rollback()
    finally:
        session.close()
    return "取引明細登録完了"

def select_transaction_details(transaction_id):
    """指定取引IDの明細データを取得"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = session.query(TransactionDetail).filter(
                TransactionDetail.trd_id == transaction_id
            )
            results = query.all()
            
        result_list = []
        for detail in results:
            result_list.append({
                "trd_id": detail.trd_id,
                "dtl_id": detail.dtl_id,
                "prd_id": detail.prd_id,
                "prd_code": detail.prd_code,
                "prd_name": detail.prd_name,
                "prd_price": detail.prd_price
            })
        
        return json.dumps(result_list, ensure_ascii=False)
    except Exception as e:
        print(f"取引明細取得でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

# POSシステム専用の複合操作関数（修正版）
def complete_transaction(emp_cd, products_list):
    """完全な取引処理（取引テーブル + 取引明細テーブル）"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            # 合計金額を計算
            total_amount = sum(product['prd_price'] for product in products_list)
            
            # 取引テーブルに挿入
            transaction_values = {
                'datetime': datetime.now(),
                'emp_cd': emp_cd,
                'store_cd': '30',
                'pos_no': '90',
                'total_amt': total_amount
            }
            
            transaction_query = insert(Transaction).values(transaction_values)
            transaction_result = session.execute(transaction_query)
            transaction_id = transaction_result.inserted_primary_key[0]
            
            # 取引明細テーブルに挿入（dtl_idを手動で管理）
            for idx, product in enumerate(products_list, 1):
                detail_values = {
                    'trd_id': transaction_id,
                    'dtl_id': idx,  # 手動でIDを設定
                    'prd_id': product['prd_id'],
                    'prd_code': product['prd_code'],
                    'prd_name': product['prd_name'],
                    'prd_price': product['prd_price']
                }
                detail_query = insert(TransactionDetail).values(detail_values)
                session.execute(detail_query)
            
            print(f"取引が完了しました。取引ID: {transaction_id}, 合計金額: {total_amount}円")
            return {
                "transaction_id": transaction_id,
                "total_amount": total_amount,
                "status": "success"
            }
            
    except Exception as e:
        print(f"取引処理でエラーが発生しました: {e}")
        session.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        session.close()

# 売上レポート関数
def get_daily_sales_report(target_date):
    """日次売上レポートを取得"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            # 日次売上合計
            total_query = session.query(
                sqlalchemy.func.sum(Transaction.total_amt).label('total_sales'),
                sqlalchemy.func.count(Transaction.trd_id).label('transaction_count')
            ).filter(
                sqlalchemy.func.date(Transaction.datetime) == target_date
            )
            total_result = total_query.first()
            
            # 商品別売上
            product_query = session.query(
                TransactionDetail.prd_name,
                sqlalchemy.func.count(TransactionDetail.prd_id).label('quantity'),
                sqlalchemy.func.sum(TransactionDetail.prd_price).label('sales')
            ).join(
                Transaction, TransactionDetail.trd_id == Transaction.trd_id
            ).filter(
                sqlalchemy.func.date(Transaction.datetime) == target_date
            ).group_by(
                TransactionDetail.prd_name
            ).all()
            
        report = {
            "date": str(target_date),
            "total_sales": total_result.total_sales or 0,
            "transaction_count": total_result.transaction_count or 0,
            "product_sales": [
                {
                    "product_name": item.prd_name,
                    "quantity": item.quantity,
                    "sales": item.sales
                }
                for item in product_query
            ]
        }
        
        return json.dumps(report, ensure_ascii=False)
        
    except Exception as e:
        print(f"売上レポート取得でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

# 汎用検索関数
def search_products_by_name(search_term):
    """商品名による部分一致検索"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = session.query(Product).filter(
                Product.name.like(f'%{search_term}%')
            )
            results = query.all()
            
        result_list = []
        for product in results:
            result_list.append({
                "prd_id": product.prd_id,
                "code": product.code,
                "name": product.name,
                "price": product.price
            })
        
        return json.dumps(result_list, ensure_ascii=False)
    except Exception as e:
        print(f"商品検索でエラーが発生しました: {e}")
        return None
    finally:
        session.close()

# 商品別売上集計関数
def get_product_sales_summary():
    """商品別売上集計"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with session.begin():
            query = session.query(
                Product.name,
                sqlalchemy.func.count(TransactionDetail.prd_id).label('sold_count'),
                sqlalchemy.func.sum(TransactionDetail.prd_price).label('total_sales')
            ).join(
                TransactionDetail, Product.prd_id == TransactionDetail.prd_id
            ).group_by(
                Product.prd_id, Product.name
            ).order_by(
                sqlalchemy.func.sum(TransactionDetail.prd_price).desc()
            )
            
            results = query.all()
            
        summary_list = []
        for item in results:
            summary_list.append({
                "product_name": item.name,
                "sold_count": item.sold_count,
                "total_sales": item.total_sales
            })
        
        return json.dumps(summary_list, ensure_ascii=False)
    except Exception as e:
        print(f"売上集計でエラーが発生しました: {e}")
        return None
    finally:
        session.close()
