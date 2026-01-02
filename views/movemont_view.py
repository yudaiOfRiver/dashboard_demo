import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def show_movement_view(df_movement):
    """
    移動（ネットワーク）分析ダッシュボードを表示する関数
    """
    st.title("🚚 サプライチェーン")
    
    # ---------------------------------------------------------
    # 1. ネットワークフロー（Sankey Diagram）
    # ---------------------------------------------------------
    # (ここは変更なし)
    st.header("1. 物流ネットワーク")
    st.caption("国内工場から店舗までの商品の流れを可視化します。")
    
    all_nodes = list(pd.concat([df_movement["Source"], df_movement["Target"]]).unique())
    node_map = {name: i for i, name in enumerate(all_nodes)}
    
    df_movement["SourceID"] = df_movement["Source"].map(node_map)
    df_movement["TargetID"] = df_movement["Target"].map(node_map)
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = all_nodes,
            color = "navy" # 色を少し変更
        ),
        link = dict(
            source = df_movement["SourceID"],
            target = df_movement["TargetID"],
            value = df_movement["Value"],
            color = "rgba(100, 100, 100, 0.4)"
        )
    )])
    
    fig_sankey.update_layout(title_text="サプライチェーン・フロー図", font_size=12, height=500)
    st.plotly_chart(fig_sankey, use_container_width=True)


    # ---------------------------------------------------------
    # 2. 地理的ネットワーク（Map）
    # ---------------------------------------------------------
    st.header("2. 地理的ネットワーク（Map）")
    st.caption("拠点間の距離とリードタイム（LT）を確認します。")

    # 拠点ごとの緯度経度データ（国内版に更新）
    location_map = {
        # 工場
        "岡山デニム工場": {"lat": 34.5800, "lon": 133.7700}, # 倉敷市付近
        "群馬縫製工場": {"lat": 36.3800, "lon": 139.0600}, # 前橋市付近
        
        # 中継センター（旧：港）
        "関東中継センター": {"lat": 35.5000, "lon": 139.7500}, # 川崎/横浜付近
        "関西中継センター": {"lat": 34.8000, "lon": 135.5500}, # 茨木/高槻付近
        
        # 倉庫・ハブ
        "豊洲DC（東京）": {"lat": 35.6544, "lon": 139.7955},
        "南港DC（大阪）": {"lat": 34.6367, "lon": 135.4144},
        "札幌ハブ": {"lat": 42.85, "lon": 141.4},
        "福岡ハブ": {"lat": 33.6, "lon": 130.45},
        
        # 店舗
        "渋谷旗艦店": {"lat": 35.6580, "lon": 139.7016},
        "新宿店": {"lat": 35.6909, "lon": 139.7003},
        "銀座店": {"lat": 35.6712, "lon": 139.7665},
        "EC配送センター": {"lat": 35.75, "lon": 139.95}, # 市川付近
        "梅田店": {"lat": 34.7025, "lon": 135.4959},
        "心斎橋店": {"lat": 34.6713, "lon": 135.5005},
        "神戸店": {"lat": 34.6901, "lon": 135.1955},
        "博多店": {"lat": 33.5896, "lon": 130.4206},
        "天神店": {"lat": 33.5916, "lon": 130.4017},
        "札幌店": {"lat": 43.0686, "lon": 141.3508}
    }

    fig_map = go.Figure()

    # ライン描画
    for _, row in df_movement.iterrows():
        src = row["Source"]
        tgt = row["Target"]
        val = row["Value"]
        lt = row["LeadTime"] if "LeadTime" in row else "?"
        
        if src in location_map and tgt in location_map:
            start_pos = location_map[src]
            end_pos = location_map[tgt]
            
            line_width = max(1, val / 300) 
            
            fig_map.add_trace(go.Scattergeo(
                lon = [start_pos["lon"], end_pos["lon"]],
                lat = [start_pos["lat"], end_pos["lat"]],
                mode = 'lines',
                line = dict(width = line_width, color = 'red'),
                opacity = 0.6,
                name = f"{src} -> {tgt}",
                hoverinfo = 'text',
                text = f"{src} -> {tgt}<br>数量: {val}着<br>LT: {lt}日"
            ))

    # 拠点プロット
    loc_df = pd.DataFrame([
        {"Name": k, "lat": v["lat"], "lon": v["lon"]} 
        for k, v in location_map.items() 
        if k in all_nodes
    ])
    
    if not loc_df.empty:
        fig_map.add_trace(go.Scattergeo(
            lon = loc_df["lon"],
            lat = loc_df["lat"],
            text = loc_df["Name"],
            mode = 'markers+text',
            textposition="top center",
            marker = dict(size=7, color='navy', symbol='circle'),
            name = "拠点"
        ))

    # 地図のスタイル設定（平面豪華版：日本フォーカス）
    fig_map.update_layout(
        title_text="国内サプライチェーン・マップ",
        showlegend=False,
        geo = dict(
            projection_type = 'mercator',
            
            # 日本中心にズーム調整
            center = dict(lat=36, lon=138),
            projection_scale = 5.5, # 日本が大きく見える倍率
            
            # 豪華な色設定
            showland = True,
            landcolor = "rgb(100, 100, 100)",
            showocean = True,
            oceancolor = "rgb(100, 100, 255)",
            showcountries = True,
            countrycolor = "rgb(255, 255, 255)",
            countrywidth = 1.0,
            showcoastlines = True,
            coastlinecolor = "rgb(200, 200, 200)",
            showframe = False
        ),
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0},
        paper_bgcolor='white', 
    )

    st.plotly_chart(fig_map, use_container_width=True)