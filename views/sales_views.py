import streamlit as st
import plotly.express as px
import pandas as pd

def show_sales_view(df_sales):
    """
    売上分析ダッシュボード
    構成：
    1. 主要KPI（最新月）
    2. 店舗別積み上げ棒グラフ
    3. 商品別積み上げ棒グラフ
    """
    st.title("📊 売上分析ダッシュボード")
    st.caption("1. 主要KPI（最新月）")

    # データ処理：日付型確認
    df = df_sales.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    # ---------------------------------------------------------
    # 1. 主要KPI（最新月のデータを表示）
    # ---------------------------------------------------------
    st.subheader("1. 今月のハイライト")
    
    # 最新月を取得
    latest_date = df["Date"].max()
    current_month_df = df[df["Date"] == latest_date]
    
    # 集計
    total_sales = current_month_df["Sales"].sum()
    total_target = current_month_df["Target"].sum()
    total_profit = current_month_df["Profit"].sum()
    
    # 達成率計算
    achievement_rate = (total_sales / total_target) * 100
    
    # 前月比を出したい場合（オプション）
    prev_date = latest_date - pd.DateOffset(months=1)
    prev_month_df = df[df["Date"] == prev_date]
    prev_sales = prev_month_df["Sales"].sum() if not prev_month_df.empty else total_sales
    mom_diff = total_sales - prev_sales

    # KPIカードの表示（3カラム）
    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        label="今月の売上",
        value=f"¥{total_sales:,.0f}",
        delta=f"前月比 {mom_diff:,.0f}円"
    )
    
    kpi2.metric(
        label="目標達成率",
        value=f"{achievement_rate:.1f}%",
        delta=f"目標差 ¥{total_sales - total_target:,.0f}",
        delta_color="normal" if achievement_rate >= 100 else "inverse" # 未達なら赤字
    )
    
    kpi3.metric(
        label="今月の粗利益",
        value=f"¥{total_profit:,.0f}",
        delta=f"利益率 {(total_profit/total_sales*100):.1f}%"
    )
    
    st.markdown("---") # 区切り線

    # ---------------------------------------------------------
    # 2. 売上推移：店舗（チャネル）別 積み上げ棒グラフ
    # ---------------------------------------------------------
    st.subheader("2. 店舗別 売上推移")
    st.caption("どの店舗が全体の売上を支えているかを確認します。")
    
    # 月×チャネルで集計
    df_channel = df.groupby(["Month", "Channel"])["Sales"].sum().reset_index()
    
    fig_channel = px.bar(
        df_channel,
        x="Month",
        y="Sales",
        color="Channel",
        title="月次売上推移（店舗別 積み上げ）",
        text_auto='.2s', # 数値を短縮表示
        category_orders={"Month": sorted(df["Month"].unique())} # 月順に並べる
    )
    fig_channel.update_layout(xaxis_title="月", yaxis_title="売上 (円)")
    st.plotly_chart(fig_channel, use_container_width=True)

    # ---------------------------------------------------------
    # 3. 売上推移：商品（カテゴリ）別 積み上げ棒グラフ
    # ---------------------------------------------------------
    st.subheader("3. 商品カテゴリ別 売上推移")
    st.caption("季節ごとの売れ筋商品の変化（トレンド）を確認します。")
    
    # 月×カテゴリで集計
    df_category = df.groupby(["Month", "Category"])["Sales"].sum().reset_index()
    
    fig_category = px.bar(
        df_category,
        x="Month",
        y="Sales",
        color="Category",
        title="月次売上推移（カテゴリ別 積み上げ）",
        text_auto='.2s',
        category_orders={"Month": sorted(df["Month"].unique())},
        color_discrete_sequence=px.colors.qualitative.Pastel # 色味を変えて区別
    )
    fig_category.update_layout(xaxis_title="月", yaxis_title="売上 (円)")
    st.plotly_chart(fig_category, use_container_width=True)