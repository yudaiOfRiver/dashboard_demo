
import streamlit as st
import plotly.express as px
import pandas as pd

def show_inventory_view(df_inventory):
    st.title("📦 在庫詳細分析")
    
    # リスク分析
    risk_df = df_inventory[df_inventory["Stock"] < df_inventory["SafetyStock"]]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.warning(f"⚠️ 在庫アラート: {len(risk_df)} 品目")
        st.metric("在庫総額", f"¥{df_inventory['TotalValue'].sum():,.0f}")
        if not risk_df.empty:
            st.dataframe(risk_df[["Warehouse", "Product", "Stock", "SafetyStock"]], height=200)
            
    with col2:
        st.subheader("倉庫別 在庫金額分布")
        fig_val = px.bar(df_inventory, x="Warehouse", y="TotalValue", color="Product", 
                         title="倉庫ごとの在庫資産額 (製品内訳)")
        st.plotly_chart(fig_val, use_container_width=True)

    st.markdown("---")

    # ABC分析 (パレート図) のシミュレーション
    st.subheader("ABC分析 (在庫金額パレート図)")
    st.info("在庫金額が高い上位品目を「Aランク」として管理するための分析です。")
    
    # 全倉庫合算でABC分析
    abc_df = df_inventory.groupby("Product")["TotalValue"].sum().reset_index()
    abc_df = abc_df.sort_values("TotalValue", ascending=False)
    abc_df["Cumulative"] = abc_df["TotalValue"].cumsum()
    abc_df["CumulativeRatio"] = abc_df["Cumulative"] / abc_df["TotalValue"].sum()
    
    # グラフ作成（棒グラフ＋折れ線グラフ）
    fig_abc = px.bar(abc_df, x="Product", y="TotalValue", title="製品別在庫金額と累積構成比")
    # 線グラフを追加するためにadd_scatterを使用（Plotly Graph Objectsの方が柔軟だが簡易的に実装）
    fig_abc.add_scatter(x=abc_df["Product"], y=abc_df["CumulativeRatio"], 
                        yaxis="y2", name="累積比率", mode="lines+markers")
    
    # 2軸設定
    fig_abc.update_layout(
        yaxis2=dict(overlaying="y", side="right", range=[0, 1.1], showgrid=False),
        showlegend=False
    )
    
    st.plotly_chart(fig_abc, use_container_width=True)