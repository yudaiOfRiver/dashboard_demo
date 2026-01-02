import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_sales_data():
    """
    売上分析用のデータを読み込む（生成する）関数
    """
    # --- 1. 売上データ（固定値） ---
    
    # 日付: 2024年1月〜9月の月末
    dates = pd.date_range(start="2024-01-01", periods=9, freq="M")
    
    # 売上（指定された固定値）
    sales = np.array([12000, 25000, 18000, 22000, 15000, 30000, 27000, 35000, 40000])
    
    # カテゴリ（定数で固定）
    categories = [
        "Electronics", "Furniture", "Office", 
        "Electronics", "Office", "Furniture", 
        "Electronics", "Electronics", "Furniture"
    ]
    
    # チャネル（定数で固定）
    channels = [
        "Online Store", "Retail Shop", "Distributor", 
        "Online Store", "Retail Shop", "Online Store", 
        "Distributor", "Online Store", "Retail Shop"
    ]
    
    sales_data = []
    cumulative = 0
    
    for i, date in enumerate(dates):
        current_sale = sales[i]
        cumulative += current_sale
        
        sales_data.append({
            "Date": date,
            "Sales": current_sale,
            "CumulativeSales": cumulative,
            "Category": categories[i],
            "Channel": channels[i]
        })
        
    df_sales = pd.DataFrame(sales_data)
    
    return df_sales


@st.cache_data
def load_inventory_data():
    """
    在庫分析用のデータを読み込む（生成する）関数
    【アパレル業界版】
    """
    # --- 2. 在庫データ ---
    warehouses = ["東京倉庫", "大阪倉庫", "福岡倉庫", "札幌倉庫"]
    
    # ポートフォリオとして見栄えが良い「アパレル商材」に変更
    products = [
        "Tシャツ",
        "Yシャツ", 
        "デニム", 
        "パーカー", 
        "スカート",
        "コート"
    ]
    
    inventory_data = []
    
    # 乱数のシードを固定
    rng = np.random.default_rng(42)

    for w in warehouses:
        for p in products:
            # 在庫数
            stock = rng.integers(0, 500)
            
            # 商品カテゴリに合わせて単価をリアルに設定（デモとしての説得力アップ）
            if "コート" in p:
                cost = rng.integers(18000, 50000) # アウターは高単価
            elif "デニム" in p or "スカート" in p:
                 cost = rng.integers(6000, 15000) # ボトムス
            elif "パーカー" in p or "シャツ" in p:
                 cost = rng.integers(4000, 9000)  # トップス（中価格帯）
            else:
                cost = rng.integers(2000, 4500)   # Tシャツ（低価格帯）

            inventory_data.append({
                "Warehouse": w,
                "Product": p,
                "Stock": stock,
                "UnitCost": cost,
                "TotalValue": stock * cost,
                "SafetyStock": 50 
            })
    
    df_inventory = pd.DataFrame(inventory_data)
    
    return df_inventory

@st.cache_data
def load_movement_data():
    """
    移動（ネットワーク）分析用のデータを読み込む（生成する）関数
    【アパレル業界版：国内生産モデル】
    """
    # --- 3. 移動（ネットワーク）データ ---
    # 国内工場からのトラック輸送フロー
    movement_data = [
        # 国内工場 -> 中継センター（トラック輸送：LT短い）
        {"Source": "岡山デニム工場", "Target": "関西中継センター", "Value": 1500, "LeadTime": 1},
        {"Source": "群馬縫製工場", "Target": "関東中継センター", "Value": 1000, "LeadTime": 1},
        
        # 中継センター -> 各DC/ハブ（幹線輸送）
        {"Source": "関東中継センター", "Target": "豊洲DC（東京）", "Value": 800, "LeadTime": 0.5},
        {"Source": "関東中継センター", "Target": "札幌ハブ", "Value": 200, "LeadTime": 2}, # フェリー/長距離トラック
        
        {"Source": "関西中継センター", "Target": "南港DC（大阪）", "Value": 1000, "LeadTime": 0.5},
        {"Source": "関西中継センター", "Target": "福岡ハブ", "Value": 200, "LeadTime": 1},
        {"Source": "関西中継センター", "Target": "豊洲DC（東京）", "Value": 300, "LeadTime": 1}, # 東西間輸送
        
        # 物流センターから各店舗へ（ラストワンマイル）
        {"Source": "豊洲DC（東京）", "Target": "渋谷旗艦店", "Value": 400, "LeadTime": 0.5},
        {"Source": "豊洲DC（東京）", "Target": "新宿店", "Value": 350, "LeadTime": 0.5},
        {"Source": "豊洲DC（東京）", "Target": "銀座店", "Value": 300, "LeadTime": 0.5},
        {"Source": "豊洲DC（東京）", "Target": "EC配送センター", "Value": 50, "LeadTime": 0.5},
        
        {"Source": "南港DC（大阪）", "Target": "梅田店", "Value": 300, "LeadTime": 0.5},
        {"Source": "南港DC（大阪）", "Target": "心斎橋店", "Value": 300, "LeadTime": 0.5},
        {"Source": "南港DC（大阪）", "Target": "神戸店", "Value": 200, "LeadTime": 0.5},
        {"Source": "南港DC（大阪）", "Target": "EC配送センター", "Value": 200, "LeadTime": 1},
        
        {"Source": "福岡ハブ", "Target": "博多店", "Value": 150, "LeadTime": 0.5},
        {"Source": "福岡ハブ", "Target": "天神店", "Value": 50, "LeadTime": 0.5},
        
        {"Source": "札幌ハブ", "Target": "札幌店", "Value": 200, "LeadTime": 0.5},
    ]
    df_movement = pd.DataFrame(movement_data)
    
    return df_movement


# 後方互換性のため（一括で読み込みたい場合用）のラッパー関数
@st.cache_data
def load_all_data():
    """
    全てのデータを一度に読み込む関数（旧仕様）
    """
    return load_sales_data(), load_inventory_data(), load_movement_data()