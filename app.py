import time
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="バブルソート アニメーション", layout="centered")

st.title("バブルソートの可視化アプリ")
st.write("流れ図に従って隣り合う要素を比較・交換しながらソートを進めます。")

# 初期データの設定（サイズ5の配列: インデックス 0〜4）
default_data = [64, 34, 25, 12, 22]

# ユーザー入力
input_str = st.text_input(
    "初期配列（カンマ区切りで5個の数字を入力）", value="64, 34, 25, 12, 22"
)
try:
    pointT = [int(x.strip()) for x in input_str.split(",")]
except ValueError:
    st.error("数字をカンマ区切りで入力してください。")
    pointT = default_data

speed = st.slider("アニメーション速度 (秒)", 0.1, 2.0, 0.5)

start_button = st.button("ソート開始")

# 描画用のエリア
chart_placeholder = st.empty()
info_placeholder = st.empty()


def draw_chart(arr, comparing_indices=None, swapped=False):
    """配列の状態を棒グラフで表示する関数"""
    colors = ["#1f77b4"] * len(arr)
    if comparing_indices:
        for idx in comparing_indices:
            colors[idx] = "#ff7f0e" if not swapped else "#2ca02c"

    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(range(len(arr)), arr, color=colors)

    # 棒グラフの上に数値を表示
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )

    ax.set_ylim(0, max(arr) * 1.2 if len(arr) > 0 else 10)
    ax.set_xticks(range(len(arr)))
    ax.set_xticklabels([f"pointT({i})" for i in range(len(arr))])
    plt.tight_layout()
    return fig


if start_button:
    arr = pointT.copy()
    n = len(arr)

    # 初期状態を表示
    chart_placeholder.pyplot(draw_chart(arr))
    info_placeholder.info("ソートを開始します...")
    time.sleep(speed)

    # 流れ図に基づくアルゴリズム実行
    # ループ1: i は 3 から 1 ずつ減らして i >= 0 の間 (要素数5の場合、index 0..4 に対して i=3 から開始)
    max_i = n - 2 if n >= 2 else 0

    for i in range(max_i, -1, -1):
        # ループ2: j は 0 から 1 ずつ増やして j <= i の間
        for j in range(0, i + 1):

            # 比較状態の描画
            info_placeholder.markdown(
                f"**ループ1 (i={i}), ループ2 (j={j})** <br>"
                f"比較中: `pointT({j})` [{arr[j]}] と `pointT({j+1})` [{arr[j+1]}]",
                unsafe_allow_html=True,
            )
            chart_placeholder.pyplot(draw_chart(arr, comparing_indices=[j, j + 1]))
            time.sleep(speed)

            # 条件判定: pointT(j) > pointT(j+1)
            if arr[j] > arr[j + 1]:
                # 交換処理 (流れ図の save を介した処理)
                save = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = save

                # 交換後の描画
                info_placeholder.markdown(
                    f"**ループ1 (i={i}), ループ2 (j={j})** <br>"
                    f"<span style='color:red;'>交換実行!</span> `pointT({j})` ↔ `pointT({j+1})`",
                    unsafe_allow_html=True,
                )
                chart_placeholder.pyplot(
                    draw_chart(arr, comparing_indices=[j, j + 1], swapped=True)
                )
                time.sleep(speed)

    info_placeholder.success("ソートが完了しました！")
    chart_placeholder.pyplot(draw_chart(arr))