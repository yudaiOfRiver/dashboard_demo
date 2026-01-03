import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def show_supply_chain_view(ports, warehouses, stores, inbound_flows, outbound_flows):
    """
    サプライチェーン全体の可視化ダッシュボード
    構成：
    1. フロー可視化 (Sankey)
    2. 地理的ネットワーク (Map)
    3. 遅延リスク分析 (Lead Time)
    4. コスト構造分析 (Cost)
    """
    st.title("🚢 サプライチェーン・マネジメント (SCM)")
    st.markdown("調達(Port)から販売(Store)までの「モノ・時間・カネ」の流れを一元管理します。")

    # 4つのタブに整理して表示
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌊 フロー分析 (Sankey)", 
        "🗺️ ネットワーク地図", 
        "⏱️ 遅延リスク分析", 
        "💰 コスト構造"
    ])

    # =================================================================
    # Tab 1: フロー分析 (Sankey Diagram) - 既存のロジック
    # =================================================================
    with tab1:
        st.subheader("物流ボリュームの全体像")
        st.caption("どこから・どこへ・どれだけの量が流れているか（線の太さ＝数量）")
        
        # --- データ前処理 ---
        all_labels = ports + warehouses + stores
        label_to_index = {label: i for i, label in enumerate(all_labels)}
        
        sources, targets, values = [], [], []
        node_colors = []
        
        # 色分け
        for label in all_labels:
            if label in ports: node_colors.append("#1f77b4")   # 青
            elif label in warehouses: node_colors.append("#ff7f0e") # オレンジ
            else: node_colors.append("#2ca02c")                 # 緑

        # フロー結合
        all_flows = inbound_flows + outbound_flows
        for src, tgt, val in all_flows:
            if src in label_to_index and tgt in label_to_index:
                sources.append(label_to_index[src])
                targets.append(label_to_index[tgt])
                values.append(val)

        # 描画
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20, thickness=20,
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=node_colors,
                hovertemplate='%{label}<br>総量: %{value} unit<extra></extra>'
            ),
            link=dict(
                source=sources, target=targets, value=values,
                color='rgba(200, 200, 200, 0.5)'
            )
        )])
        fig_sankey.update_layout(height=600, margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_sankey, use_container_width=True)

    # =================================================================
    # Tab 2: 地図分析 (Geospatial Map) - 新規追加
    # =================================================================
    with tab2:
        st.subheader("物流ネットワークマップ")
        
        # 簡易的なマスタデータ（実務ではDBから取得）
        locations = {
            "東京港": {"lat": 35.6267, "lon": 139.7758, "type": "Port"},
            "横浜港": {"lat": 35.4468, "lon": 139.6489, "type": "Port"},
            "神戸港": {"lat": 34.6850, "lon": 135.2656, "type": "Port"},
            "博多港": {"lat": 33.6101, "lon": 130.3970, "type": "Port"},
            "関東DC": {"lat": 35.8000, "lon": 139.7000, "type": "Warehouse"},
            "中部ハブ": {"lat": 35.0500, "lon": 136.8500, "type": "Warehouse"},
            "関西物流センター": {"lat": 34.7500, "lon": 135.4500, "type": "Warehouse"},
            "九州デポ": {"lat": 33.5500, "lon": 130.4500, "type": "Warehouse"},
            "新宿旗艦店": {"lat": 35.6909, "lon": 139.7002, "type": "Store"},
            "梅田店": {"lat": 34.7025, "lon": 135.4959, "type": "Store"},
            "博多駅前店": {"lat": 33.5902, "lon": 130.4207, "type": "Store"},
            "渋谷店": {"lat": 35.6580, "lon": 139.7016, "type": "Store"},
            "横浜店": {"lat": 35.4657, "lon": 139.6223, "type": "Store"},
            "名古屋駅前店": {"lat": 35.1709, "lon": 136.8815, "type": "Store"},
            "心斎橋店": {"lat": 34.6714, "lon": 135.5014, "type": "Store"},
            "天神店": {"lat": 33.5916, "lon": 130.3989, "type": "Store"},
        }

        # マップ用データ作成
        df_loc = pd.DataFrame.from_dict(locations, orient='index').reset_index()
        df_loc.columns = ["Name", "lat", "lon", "type"]
        
        # ベースマップ
        fig_map = px.scatter_mapbox(
            df_loc, lat="lat", lon="lon", color="type", size=[10]*len(df_loc),
            hover_name="Name", zoom=4, center={"lat": 36.0, "lon": 137.0},
            mapbox_style="carto-positron", height=600
        )
        
        # ルート線を描画
        for src, tgt, val in all_flows:
            if src in locations and tgt in locations:
                fig_map.add_trace(go.Scattermapbox(
                    mode="lines",
                    lon=[locations[src]["lon"], locations[tgt]["lon"]],
                    lat=[locations[src]["lat"], locations[tgt]["lat"]],
                    line=dict(width=val/2000 + 1, color="gray"), # 量が多いほど太く
                    hoverinfo="text", text=f"{src}→{tgt}: {val}"
                ))
        
        st.plotly_chart(fig_map, use_container_width=True)

    # =================================================================
    # Tab 3: リードタイム分析 (Lead Time) - 新規追加
    # =================================================================
    with tab3:
        st.subheader("配送リードタイムのばらつき")
        st.caption("平均日数だけでなく、遅延の振れ幅（リスク）を箱ひげ図で可視化")
        
        # ダミーデータ生成
        routes_list = ["東京港→関東DC", "横浜港→中部ハブ", "神戸港→関西物流", "関東DC→新宿店", "中部ハブ→名古屋店"]
        lead_data = []
        rng = np.random.default_rng(42)
        
        for r in routes_list:
            # 港発はばらつき大(scale=3)、国内は安定(scale=0.5)
            sigma = 3.0 if "港" in r else 0.5
            mu = 14.0 if "港" in r else 2.0
            
            days = rng.normal(mu, sigma, 50)
            for d in days:
                lead_data.append({"Route": r, "Days": max(0.5, d)})
                
        df_lead = pd.DataFrame(lead_data)
        
        fig_box = px.box(df_lead, x="Route", y="Days", color="Route", points="all")
        st.plotly_chart(fig_box, use_container_width=True)

    # =================================================================
    # Tab 4: コスト構造 (Waterfall) - 新規追加
    # =================================================================
    with tab4:
        st.subheader("着地原価 (Landed Cost) の内訳")
        
        # ウォーターフォール図用のデータ
        fig_water = go.Figure(go.Waterfall(
            name="Cost Breakdown", orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "total"],
            x=["製造原価", "海上輸送費", "関税", "通関・港湾費", "国内配送費", "着地原価(Total)"],
            textposition="outside",
            text=[5000, 500, 300, 100, 800, None],
            y=[5000, 500, 300, 100, 800, 0],
            connector={"line":{"color":"rgb(63, 63, 63)"}},
        ))
        fig_water.update_layout(title="主力製品のコスト積み上げ分析", showlegend=False)
        st.plotly_chart(fig_water, use_container_width=True)