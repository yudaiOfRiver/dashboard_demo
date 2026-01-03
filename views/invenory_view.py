import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def show_inventory_view(df_inventory):
    """
    在庫分析ダッシュボード（既存）
    """
    st.title("🏭 部品在庫管理ダッシュボード")
    st.caption("物流センター長向け：供給責任の完遂と適正資産の維持")

    # ---------------------------------------------------------
    # 1. 重要KPIとアラート
    # ---------------------------------------------------------
    st.header("1. 現在のステータス（リスク管理）")

    total_value = df_inventory["TotalValue"].sum()
    alert_df = df_inventory[df_inventory["IsAlert"]]
    alert_count = len(alert_df)
    excess_df = df_inventory[df_inventory["InventoryMonths"] >= 3.0]
    excess_count = len(excess_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("在庫資産総額", f"¥{total_value:,.0f}")
    col2.metric("🚨 欠品アラート", f"{alert_count} SKU", delta="- 供給停止リスク" if alert_count > 0 else "正常", delta_color="inverse")
    col3.metric("⚠️ 滞留・過剰在庫", f"{excess_count} SKU", delta="キャッシュフロー圧迫", delta_color="off")

    st.markdown("---")

    # ---------------------------------------------------------
    # 2. アクション：緊急発注リスト
    # ---------------------------------------------------------
    if alert_count > 0:
        st.subheader("🚨 緊急手配リスト")
        st.error("以下の部品は安全在庫を下回っています。至急手配してください。")
        st.dataframe(
            alert_df[["Warehouse", "Product", "Stock", "SafetyStock", "InventoryMonths"]].sort_values("Stock"),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("現在、欠品リスクのある部品はありません。")

    # ---------------------------------------------------------
    # 3. 資産分布 (既存のSankeyまたはTreemap)
    # ---------------------------------------------------------
    st.subheader("3. 資産構成の分析")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Treemap
        fig_wh = px.treemap(
            df_inventory,
            path=["Warehouse", "Product"], 
            values="TotalValue",
            title="在庫資産の構成比（倉庫 > 部品）",
        )
        fig_wh.update_traces(textinfo="label+value", texttemplate="%{label}<br>¥%{value:,.0f}")
        st.plotly_chart(fig_wh, use_container_width=True)
        
    with col_chart2:
        # Scatter
        fig_risk = px.scatter(
            df_inventory,
            x="InventoryMonths",
            y="TotalValue",
            size="MonthlyDemand",
            color="IsAlert",
            hover_name="Product",
            title="在庫回転率 × 資産額マップ",
            color_discrete_map={True: "red", False: "navy"}
        )
        fig_risk.add_vline(x=3.0, line_dash="dash", line_color="orange")
        fig_risk.add_vline(x=0.5, line_dash="dash", line_color="red")
        
        st.plotly_chart(fig_risk, use_container_width=True)


def show_logistics_sankey(ports, warehouses, stores, inbound_flows, outbound_flows):
    """
    新規追加: 物流サプライチェーン（港->倉庫->店舗）のSankey Diagramを表示
    """
    st.header("🚢 サプライチェーン可視化")
    st.markdown("輸入(Port) から 店舗(Store) までの商品の流れとボリュームを追跡します。")

    # --- Sankey Diagram用のデータ前処理 ---
    
    # 1. 全ノードのリストを作成し、一意なID(index)を振る
    all_labels = ports + warehouses + stores
    label_to_index = {label: i for i, label in enumerate(all_labels)}
    
    # 2. ソース、ターゲット、値をリスト化
    sources = []
    targets = []
    values = []
    
    # 色の設定
    node_colors = []
    for label in all_labels:
        if label in ports:
            node_colors.append("blue")
        elif label in warehouses:
            node_colors.append("orange")
        else:
            node_colors.append("green")

    # フローデータの結合
    all_flows = inbound_flows + outbound_flows

    for src, tgt, val in all_flows:
        if src in label_to_index and tgt in label_to_index:
            sources.append(label_to_index[src])
            targets.append(label_to_index[tgt])
            values.append(val)

    # --- 描画 ---
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=node_colors,
            hovertemplate='%{label}<br>総量: %{value} unit<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(200, 200, 200, 0.5)'
        )
    )])

    fig.update_layout(
        title_text="物流フロー：港(左) → 倉庫(中) → 店舗(右)",
        font_size=12,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **💡 分析のヒント**
    - **ボトルネックの特定:** 線が集中している倉庫（例：関東DC）が停止した際の影響範囲を確認できます。
    - **依存度の可視化:** 各店舗がどの港・倉庫からの供給に依存しているかがわかります。
    """)