import time
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="ソートアルゴリズム＆流れ図ビジュアルアナライザー", layout="wide"
)

st.title("ソートアルゴリズム＆流れ図ビジュアライザ")

# サイドバー設定
st.sidebar.header("設定")
algorithm = st.sidebar.selectbox(
    "ソートアルゴリズムの選択",
    ["バブルソート (Bubble Sort)", "選択ソート (Selection Sort)", "挿入ソート (Insertion Sort)"],
)

speed = st.sidebar.slider("アニメーション速度 (秒)", 0.1, 2.0, 0.5)

input_str = st.sidebar.text_input(
    "初期配列（カンマ区切り）", value="64, 34, 25, 12, 22"
)
try:
    initial_data = [int(x.strip()) for x in input_str.split(",")]
except ValueError:
    st.error("数字をカンマ区切りで入力してください。")
    initial_data = [64, 34, 25, 12, 22]

# 画像アップロード機能
st.sidebar.subheader("流れ図の読み込み")
uploaded_file = st.sidebar.file_uploader(
    "流れ図画像をドラッグ＆ドロップしてください", type=["png", "jpg", "jpeg"]
)

# 左右2カラムレイアウト
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📌 流れ図と実行状態")
    img_placeholder = st.empty()
    status_placeholder = st.empty()

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_placeholder.image(
            image, caption="アップロードされた流れ図", use_container_width=True
        )
    else:
        img_placeholder.info(
            "👈 左のサイドバーから流れ図画像をドラッグ＆ドロップするとここに表示されます。"
        )

with col_right:
    st.subheader("📊 ソートアニメーション")
    chart_placeholder = st.empty()

start_button = st.sidebar.button("ソート実行", type="primary")


def draw_chart(arr, active_indices=None, swapped=False):
    """配列の状態を棒グラフで表示する関数"""
    colors = ["#1f77b4"] * len(arr)
    if active_indices:
        for idx in active_indices:
            if 0 <= idx < len(arr):
                colors[idx] = "#ff7f0e" if not swapped else "#2ca02c"

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(range(len(arr)), arr, color=colors)

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


def update_display(node_text, arr, active_indices=None, swapped=False):
    """状態メッセージとグラフを更新するヘルパー関数"""
    status_placeholder.markdown(
        f"### 🔄 現在実行中の処理\n> **{node_text}**"
    )
    chart_placeholder.pyplot(
        draw_chart(arr, active_indices=active_indices, swapped=swapped)
    )
    time.sleep(speed)


# 初期のグラフ表示
chart_placeholder.pyplot(draw_chart(initial_data))

# ソート処理の実行
if start_button:
    arr = initial_data.copy()
    n = len(arr)

    # ----------------------------------------------------
    # 1. バブルソート (添付画像のフローチャートに基づく)
    # ----------------------------------------------------
    if "バブルソート" in algorithm:
        max_i = n - 2 if n >= 2 else 0

        for i in range(max_i, -1, -1):
            update_display(f"【ループ1】 i = {i} (i ≧ 0 の間)", arr)

            for j in range(0, i + 1):
                update_display(
                    f"【ループ2】 j = {j} (j ≦ i の間)", arr, [j, j + 1]
                )

                # 条件判定
                if arr[j] > arr[j + 1]:
                    update_display(
                        f"【条件判定】 pointT({j}) [{arr[j]}] > pointT({j+1}) [{arr[j+1]}] ➔ **Yes (Y)**",
                        arr,
                        [j, j + 1],
                    )

                    # 退避と交換
                    save = arr[j]
                    arr[j] = arr[j + 1]
                    arr[j + 1] = save

                    update_display(
                        f"【代入・交換】 save={save} 経由で pointT({j}) ↔ pointT({j+1}) を交換",
                        arr,
                        [j, j + 1],
                        swapped=True,
                    )
                else:
                    update_display(
                        f"【条件判定】 pointT({j}) [{arr[j]}] > pointT({j+1}) [{arr[j+1]}] ➔ **No (N)** (交換なし)",
                        arr,
                        [j, j + 1],
                    )

    # ----------------------------------------------------
    # 2. 選択ソート (Selection Sort)
    # ----------------------------------------------------
    elif "選択ソート" in algorithm:
        for i in range(0, n - 1):
            min_idx = i
            update_display(
                f"【外側ループ】 i = {i} (最小値の探索開始: min_idx = {i})",
                arr,
                [i],
            )

            for j in range(i + 1, n):
                update_display(
                    f"【内側ループ】 j = {j} (最小値と比較中)", arr, [min_idx, j]
                )

                if arr[j] < arr[min_idx]:
                    min_idx = j
                    update_display(
                        f"【最小値更新】 より小さな値発見! ➔ min_idx = {min_idx} (値: {arr[min_idx]})",
                        arr,
                        [min_idx],
                    )

            if min_idx != i:
                save = arr[i]
                arr[i] = arr[min_idx]
                arr[min_idx] = save
                update_display(
                    f"【交換実行】 最小値 pointT({min_idx}) と pointT({i}) を交換",
                    arr,
                    [i, min_idx],
                    swapped=True,
                )
            else:
                update_display(
                    f"【確認】 pointT({i}) が既に最小値のため交換なし", arr, [i]
                )

    # ----------------------------------------------------
    # 3. 挿入ソート (Insertion Sort)
    # ----------------------------------------------------
    elif "挿入ソート" in algorithm:
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            update_display(
                f"【外側ループ】 i = {i} (挿入要素 save = {key})", arr, [i]
            )

            while j >= 0 and arr[j] > key:
                update_display(
                    f"【比較＆シフト】 pointT({j}) [{arr[j]}] > {key} ➔ 右へシフト",
                    arr,
                    [j, j + 1],
                )
                arr[j + 1] = arr[j]
                j -= 1
                update_display("【シフト実行】 要素を1つ右へ移動", arr)

            arr[j + 1] = key
            update_display(
                f"【挿入完了】 pointT({j+1}) に save ({key}) を挿入",
                arr,
                [j + 1],
                swapped=True,
            )

    status_placeholder.success("🎉 ソート処理が完了しました！")
    chart_placeholder.pyplot(draw_chart(arr))