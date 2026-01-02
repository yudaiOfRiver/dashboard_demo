import streamlit as st
from data_loder import load_all_data


# 各ビュー（画面）の関数をインポート
from views.sales_views import show_sales_view
from views.invenory_view import show_inventory_view
from views.movemont_view import show_movement_view

# ページ設定
st.set_page_config(page_title="統合分析ダッシュボード", layout="wide")

# データの読み込み
df_sales, df_inventory, df_movement = load_all_data()

# サイドバー設定
st.sidebar.title("MENU")
page = st.sidebar.radio(
    "機能を選択",
    ["1. 売上分析", "2. 在庫分析", "3. 移動分析"]
)

st.sidebar.markdown("---")
st.sidebar.caption("v2.0 - Multi-file Architecture")

# 画面の切り替え実行
if page == "1. 売上分析":
    show_sales_view(df_sales)

elif page == "2. 在庫分析":
    show_inventory_view(df_inventory)

elif page == "3. 移動分析":
    show_movement_view(df_movement)