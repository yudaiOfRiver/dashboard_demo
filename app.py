import streamlit as st
from data_loder import load_all_data 

# 各ビューのインポート
from views.sales_views import show_sales_view
from views.invenory_view import show_inventory_view
from views.suply_chain_view import show_supply_chain_view

st.set_page_config(page_title="統合分析ダッシュボード", layout="wide")

# データの読み込み
df_sales, df_inventory, supply_chain_data = load_all_data()

# サイドバー
st.sidebar.title("MENU")
page = st.sidebar.radio(
    "機能を選択",
    [
        "1. 売上分析 (Sales)", 
        "2. 在庫分析 (Inventory)", 
        "3. サプライチェーン (SCM)" # 名前を少しリッチに
    ]
)
st.sidebar.markdown("---")

# 画面切り替え
if page == "1. 売上分析 (Sales)":
    show_sales_view(df_sales)

elif page == "2. 在庫分析 (Inventory)":
    show_inventory_view(df_inventory)

elif page == "3. サプライチェーン (SCM)":
    # ★ここを変更：新しい関数を呼び出し
    show_supply_chain_view(*supply_chain_data)