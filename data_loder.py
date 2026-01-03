import pandas as pd
import numpy as np
import streamlit as st

# ------------------------------------------------------------------
# 1. 売上データ：アパレル業界
# ------------------------------------------------------------------
@st.cache_data
def load_sales_data():
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
    channels = ["渋谷旗艦店", "新宿店", "銀座店", "ECサイト", "梅田店", "博多店"]
    categories = ["トップス", "ボトムス", "アウター", "アクセサリー"]
    
    sales_data = []
    rng = np.random.default_rng(42)
    
    for date in dates:
        for channel in channels:
            for category in categories:
                base_sales = rng.integers(300000, 1000000)
                month = date.month
                if month in [1, 2, 12] and category == "アウター":
                    base_sales = int(base_sales * 1.5)
                if channel in ["渋谷旗艦店", "ECサイト"]:
                    base_sales = int(base_sales * 1.2)
                
                sales = int(base_sales)
                target = int(sales * rng.uniform(0.9, 1.15))
                cost = int(sales * rng.uniform(0.35, 0.45))
                
                sales_data.append({
                    "Date": date,
                    "Month": date.strftime("%Y-%m"),
                    "Channel": channel,
                    "Category": category,
                    "Sales": sales,
                    "Target": target,
                    "Cost": cost,
                    "Profit": sales - cost
                })
                
    return pd.DataFrame(sales_data)

# ------------------------------------------------------------------
# 2. 在庫データ：工業部品
# ------------------------------------------------------------------
@st.cache_data
def load_inventory_data():
    warehouses = ["関東パーツセンター", "中部物流センター", "関西ハブ倉庫", "九州デポ"]
    products = [
        "ACサーボモーター", "プログラマブルコントローラ(PLC)", "電磁弁(ソレノイドバルブ)", 
        "精密ボールねじ", "産業用ベアリング", "高強度六角ボルト"
    ]
    
    inventory_data = []
    rng = np.random.default_rng(42)

    for w in warehouses:
        for p in products:
            if "PLC" in p: cost = rng.integers(150000, 300000)
            elif "モーター" in p: cost = rng.integers(50000, 120000)
            elif "ボールねじ" in p or "電磁弁" in p: cost = rng.integers(10000, 30000)
            elif "ベアリング" in p: cost = rng.integers(2000, 8000)
            else: cost = rng.integers(50, 500)

            if "ボルト" in p: monthly_demand = rng.integers(5000, 20000)
            else: monthly_demand = rng.integers(10, 100)
            
            safety_stock = int(monthly_demand * 0.5)
            stock_multiplier = 1.5 if "中部" in w else 1.0
            stock_scenario = rng.choice(["normal", "shortage", "excess"], p=[0.75, 0.1, 0.15])
            
            if stock_scenario == "shortage": stock = rng.integers(0, safety_stock + 1)
            elif stock_scenario == "excess": stock = rng.integers(monthly_demand * 3, monthly_demand * 5)
            else: stock = int(rng.integers(safety_stock, monthly_demand * 2) * stock_multiplier)

            inventory_data.append({
                "Warehouse": w, "Product": p, "Stock": stock, "UnitCost": cost,
                "TotalValue": stock * cost, "SafetyStock": safety_stock,
                "MonthlyDemand": monthly_demand,
                "InventoryMonths": round(stock / monthly_demand, 1) if monthly_demand > 0 else 0
            })
    
    df_inventory = pd.DataFrame(inventory_data)
    df_inventory["IsAlert"] = df_inventory["Stock"] < df_inventory["SafetyStock"]
    
    return df_inventory

# ------------------------------------------------------------------
# 3. サプライチェーンデータ（港→倉庫→店舗）
# ------------------------------------------------------------------
@st.cache_data
def load_supply_chain_data():
    ports = ["東京港", "横浜港", "神戸港", "博多港"]
    warehouses = ["関東DC", "中部ハブ", "関西物流センター", "九州デポ"]
    stores = [
        "新宿旗艦店", "渋谷店", "横浜店",
        "名古屋駅前店",
        "梅田店", "心斎橋店",
        "博多駅前店", "天神店"
    ]

    inbound_flows = [
        ("東京港", "関東DC", 8000), ("横浜港", "関東DC", 5000), ("横浜港", "中部ハブ", 2000),
        ("神戸港", "関西物流センター", 7000), ("神戸港", "中部ハブ", 3000), ("博多港", "九州デポ", 4000),
    ]

    outbound_flows = [
        ("関東DC", "新宿旗艦店", 5000), ("関東DC", "渋谷店", 4000), ("関東DC", "横浜店", 4000),
        ("中部ハブ", "名古屋駅前店", 5000),
        ("関西物流センター", "梅田店", 4000), ("関西物流センター", "心斎橋店", 3000),
        ("九州デポ", "博多駅前店", 2500), ("九州デポ", "天神店", 1500),
        ("関東DC", "梅田店", 500),
    ]

    return ports, warehouses, stores, inbound_flows, outbound_flows

@st.cache_data
def load_all_data():
    """
    全てのデータを一度に読み込む関数
    戻り値: (売上DF, 在庫DF, サプライチェーンデータタプル)
    """
    return load_sales_data(), load_inventory_data(), load_supply_chain_data()