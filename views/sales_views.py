import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

def show_sales_view(df_sales):
    """
    売上分析ダッシュボードを表示する関数
    
    Parameters:
    df_sales (pd.DataFrame): 売上データ
        必須カラム: ['Date', 'Category', 'Sales']
        推奨カラム: ['Channel'] (販売チャネル分析用)
    """
    st.title("📊 売上分析ダッシュボード")

    # データのコピーと日付型への変換（元のデータを変更しないようにコピー）
    df = df_sales.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        st.error("データに 'Date' カラムがありません。")
        return

    # ---------------------------------------------------------
    # 1. 時間軸：年間目標と進捗管理（1月〜12月固定）
    # ---------------------------------------------------------
    st.subheader("1. 年間目標と進捗管理")
    
    # 年間目標の設定（サイドバーではなくメインエリアで設定できるようにしています）
    yearly_goal = st.number_input("今期の年間売上目標（円）", value=300000, step=1000, min_value=0)

    # データの期間から、表示する「年」を決定（データ内の最新年を採用）
    if not df.empty:
        target_year = df["Date"].dt.year.max()
    else:
        target_year = datetime.date.today().year

    st.caption(f"対象年度: {target_year}年")

    # 1月〜12月までの枠（空のデータフレーム）を作成
    all_months = pd.date_range(start=f"{target_year}-01-01", end=f"{target_year}-12-01", freq="MS")
    df_all_months = pd.DataFrame({"MonthDate": all_months})
    # ▼変更点1：表示用文字列を「年-月」から「月のみ」に変更
    df_all_months["MonthStr"] = df_all_months["MonthDate"].dt.strftime("%m月")

    # 実績データの集計
    df_monthly = df[df["Date"].dt.year == target_year].copy()
    # 月ごとに売上合計を算出
    df_monthly = df_monthly.set_index("Date").resample("MS")["Sales"].sum().reset_index()
    # ▼変更点2：こちらも「月のみ」に合わせてフォーマットを変更（マージキーにするため）
    df_monthly["MonthStr"] = df_monthly["Date"].dt.strftime("%m月")

    # 1〜12月の枠に実績をマージ（左外部結合）
    df_merged = pd.merge(df_all_months, df_monthly, on="MonthStr", how="left")
    df_merged["Sales"] = df_merged["Sales"].fillna(0) # 売上がない月は0で埋める
    
    # 累積売上の計算
    # ※未来の月（まだ実績がない月）をグラフ上で途切れさせる処理
    
    # 売上が発生している（または今日以前の）最後の月を探す
    # ここでは簡易的に「売上が0より大きい最後の月」までを実績とするロジック
    last_sales_idx = df_merged[df_merged["Sales"] > 0].index.max()
    
    if pd.isna(last_sales_idx):
        last_sales_idx = -1 # 売上がまだ全くない場合
        
    df_merged["Cumulative Sales"] = df_merged["Sales"].cumsum()
    
    # 未来の月の累積値はグラフに描画させないように None (NaN) にする
    df_merged.loc[last_sales_idx+1:, "Cumulative Sales"] = None

    # 現在の進捗率（最新の実績累積値を使用）
    current_total = df_merged["Cumulative Sales"].max() if not pd.isna(df_merged["Cumulative Sales"].max()) else 0
    progress_rate = (current_total / yearly_goal) * 100

    # メトリクス（数値）表示
    col_kpi1, col_kpi2 = st.columns(2)
    col_kpi1.metric("現在の累積売上", f"¥{current_total:,.0f}")
    col_kpi2.metric("対目標進捗率", f"{progress_rate:.1f}%")

    # グラフ描画 (Plotly Graph Objects)
    fig_time = go.Figure()

    # A. 累積売上のライン（実績）
    fig_time.add_trace(go.Scatter(
        x=df_merged["MonthStr"], 
        y=df_merged["Cumulative Sales"],
        mode='lines+markers',
        name='累積売上実績',
        line=dict(color='blue', width=3),
        connectgaps=False # データがない区間（未来）をつながない
    ))

    # B. 年間目標ライン（1月〜12月すべてに目標線を引く）
    fig_time.add_trace(go.Scatter(
        x=df_merged["MonthStr"], 
        y=[yearly_goal] * 12,
        mode='lines',
        name='年間目標',
        line=dict(color='red', dash='dash')
    ))

    # C. 目標ペース（理想的な進捗ライン）
    # 12ヶ月で均等に売り上げると仮定したライン
    target_pace = [yearly_goal / 12 * i for i in range(1, 13)]
    fig_time.add_trace(go.Scatter(
        x=df_merged["MonthStr"],
        y=target_pace,
        mode='lines',
        name='目標ペース',
        line=dict(color='gray', dash='dot', width=1),
        opacity=0.5
    ))

    # D. 月単体の売上（棒グラフ）
    # 未来の0円を表示したくない場合は、ここもフィルタリング
    bar_data = df_merged.copy()
    bar_data.loc[last_sales_idx+1:, "Sales"] = None
    
    fig_time.add_trace(go.Bar(
        x=bar_data["MonthStr"],
        y=bar_data["Sales"],
        name='月次売上',
        opacity=0.3,
        yaxis='y2' # 第2軸を使用
    ))

    # レイアウト調整
    fig_time.update_layout(
        title=f"{target_year}年 売上進捗（1月〜12月）",
        xaxis_title="月",
        yaxis_title="累積売上 (円)",
        yaxis2=dict(
            title="月次売上 (円)",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(x=0, y=1.1, orientation="h"),
        xaxis=dict(
            tickmode='array',
            tickvals=df_merged["MonthStr"], # 1月〜12月のラベルを強制表示
            fixedrange=True # ズーム不可にして全体を見せる
        ),
        hovermode="x unified"
    )
    st.plotly_chart(fig_time, use_container_width=True)


    # 画面分割（カテゴリ分析とチャネル分析）
    col_cat, col_chan = st.columns(2)

    # ---------------------------------------------------------
    # 2. カテゴリ軸：各カテゴリの売上
    # ---------------------------------------------------------
    with col_cat:
        st.subheader("2. カテゴリ別進捗")
        
        if "Category" in df.columns:
            # カテゴリごとの実績集計
            df_category = df.groupby("Category")["Sales"].sum().reset_index()
            
            # --- カテゴリごとの目標設定 ---
            # 実務では別途マスタから読み込むか、辞書で定義します
            # ここではサンプルとして、全カテゴリ合計目標をカテゴリ数で割った値を基準に少しバラつきを持たせます
            # または、簡易的に「一律 80,000円」などの固定値でもOKです
            
            # サンプル: カテゴリ名をキーにした目標辞書（なければデフォルト値）
            # ※必要に応じて書き換えてください
            target_dict = {
                "Electronics": 120000,
                "Clothing": 80000,
                "Home & Garden": 60000,
                "Books": 40000
            }
            # 辞書にないカテゴリは平均値などを割り当てる
            default_target = yearly_goal / len(df_category)
            
            df_category["Target"] = df_category["Category"].map(target_dict).fillna(default_target)
            
            # 進捗率の計算
            df_category["Progress"] = (df_category["Sales"] / df_category["Target"]) * 100
            
            # グラフ描画（Barチャートを重ねて進捗バーに見せる）
            fig_cat = go.Figure()

            # 背景：目標値（グレーのバー）
            fig_cat.add_trace(go.Bar(
                y=df_category["Category"],
                x=df_category["Target"],
                orientation='h',
                name='目標',
                marker=dict(color='lightgray'),
                opacity=0.5
            ))

            # 前景：実績値（色付きバー）
            # 進捗率によって色を変えるなどの工夫も可能
            fig_cat.add_trace(go.Bar(
                y=df_category["Category"],
                x=df_category["Sales"],
                orientation='h',
                name='実績',
                text=df_category["Progress"].apply(lambda x: f"{x:.1f}%"), # 進捗率を表示
                textposition='auto',
                marker=dict(color='teal')
            ))

            fig_cat.update_layout(
                title="カテゴリ別 目標達成状況",
                barmode='overlay', # 重ねて表示
                xaxis_title="売上 (円)",
                yaxis=dict(autorange="reversed"), # 上から順に表示
                legend=dict(orientation="h", x=0, y=1.1)
            )
            
            st.plotly_chart(fig_cat, use_container_width=True)
            
            # 詳細データの表示（アコーディオン）
            with st.expander("詳細データを見る"):
                st.dataframe(df_category)
                
        else:
            st.warning("'Category' カラムが見つかりません。")

    # ---------------------------------------------------------
    # 3. 販売先軸：流通経路ごとの構成比
    # ---------------------------------------------------------
    with col_chan:
        st.subheader("3. 販売チャネル別")
        
        # 販売チャネルごとの集計（カラム名 'Channel' があると仮定）
        # もしデータセットのカラム名が違う場合は、ここを修正してください
        channel_col = "Channel" 
        
        if channel_col in df.columns:
            df_channel = df.groupby(channel_col)["Sales"].sum().reset_index()
            
            fig_chan = px.pie(
                df_channel, 
                values="Sales", 
                names=channel_col, 
                title="販売チャネル別 売上構成比",
                hole=0.4 # ドーナツチャートにする
            )
            fig_chan.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_chan, use_container_width=True)
        else:
            st.info(f"データに '{channel_col}' 列が見つかりません。（販売先分析スキップ）")

# --- 動作確認用メインブロック ---
if __name__ == "__main__":
    # ダミーデータの作成
    import numpy as np
    
    # 現在の年のデータを作成
    this_year = datetime.date.today().year
    dates = pd.date_range(start=f"{this_year}-01-01", periods=120, freq="D")
    
    categories = ["Electronics", "Clothing", "Home & Garden", "Books"]
    channels = ["Online Store", "Retail Shop A", "Retail Shop B", "Distributor"]
    
    data = {
        "Date": dates,
        "Category": np.random.choice(categories, size=len(dates)),
        "Channel": np.random.choice(channels, size=len(dates)),
        "Sales": np.random.randint(1000, 50000, size=len(dates))
    }
    df_test = pd.DataFrame(data)
    
    # 関数呼び出し
    show_sales_view(df_test)