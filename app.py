import time
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
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

# ----------------------------------------------------
# 画面配置: 左側に「実行中テキスト (上) ➔ 流れ図画像 (下)」
# ----------------------------------------------------
with col_left:
    st.subheader("📌 実行状態と流れ図")
    status_placeholder = st.empty()  # 上側にテキスト表示箇所を設定
    img_placeholder = st.empty()     # 下側に画像表示箇所を設定

    # 画像の読み込みとサイズ制御 (高さ700px制限)
    base_image = None
    if uploaded_file is not None:
        raw_img = Image.open(uploaded_file).convert("RGB")
        if raw_img.height > 700:
            aspect_ratio = raw_img.width / raw_img.height
            new_width = int(700 * aspect_ratio)
            base_image = raw_img.resize((new_width, 700))
        else:
            base_image = raw_img
        img_placeholder.image(base_image, caption="アップロードされた流れ図")
    else:
        img_placeholder.info(
            "👈 左のサイドバーから流れ図画像をドラッグ＆ドロップするとここに表示されます。"
        )

with col_right:
    st.subheader("📊 ソートアニメーション")
    chart_placeholder = st.empty()

start_button = st.sidebar.button("ソート実行", type="primary")


def draw_arrow_on_image(image, y_ratio):
    """
    画像上の指定された高さ比率(0.0〜1.0)の場所に「⇦」矢印を上書き描画する関数
    """
    if image is None:
        return None

    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    w, h = img_copy.size

    y = int(h * y_ratio)

    # 矢印の色と太さの設定
    arrow_color = (235, 50, 50)  # 鮮やかな赤色
    line_width = max(4, int(w * 0.015))

    # 矢印の位置計算 (右端から中央・ノード側に向けて指す)
    x_end = int(w * 0.72)    # 矢の先端 (ノードのすぐ右)
    x_start = int(w * 0.95)  # 矢の末端

    # 幹の線を描画
    draw.line([(x_start, y), (x_end, y)], fill=arrow_color, width=line_width)

    # 矢印の頭（←）を描画
    head_size = max(10, int(h * 0.025))
    draw.polygon(
        [
            (x_end, y),
            (x_end + head_size, y - head_size),
            (x_end + head_size, y + head_size),
        ],
        fill=arrow_color,
    )

    return img_copy


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


def update_display(node_text, arr, active_indices=None, swapped=False, y_ratio=0.1):
    """状態メッセージ・矢印付き画像・棒グラフを同期更新するヘルパー関数"""
    # 1. 上側に実行中のテキストメッセージを表示
    status_placeholder.markdown(
        f"### 🔄 現在実行中の処理\n> **{node_text}**"
    )

    # 2. 流れ図画像上の該当位置に矢印を描画して更新
    if base_image is not None:
        arrow_img = draw_arrow_on_image(base_image, y_ratio)
        img_placeholder.image(arrow_img, caption="実行中のノードを矢印で表示中")

    # 3. 画面右側の棒グラフアニメーションを更新
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
    # 1. バブルソート (添付された画像の流れ図座標に対応)
    # ----------------------------------------------------
    if "バブルソート" in algorithm:
        # 画像各ノードの高さ位置 (y_ratio)
        Y_LOOP1 = 0.10      # ループ1
        Y_LOOP2 = 0.22      # ループ2
        Y_COND = 0.35       # 条件分岐 (pointT(j) > pointT(j+1))
        Y_SWAP1 = 0.48      # pointT(j) -> save
        Y_SWAP2 = 0.58      # pointT(j+1) -> pointT(j)
        Y_SWAP3 = 0.68      # save -> pointT(j+1)

        max_i = n - 2 if n >= 2 else 0

        for i in range(max_i, -1, -1):
            update_display(
                f"【ループ1】 i = {i} (i ≧ 0 の間)",
                arr,
                y_ratio=Y_LOOP1,
            )

            for j in range(0, i + 1):
                update_display(
                    f"【ループ2】 j = {j} (j ≦ i の間)",
                    arr,
                    [j, j + 1],
                    y_ratio=Y_LOOP2,
                )

                # 条件判定
                if arr[j] > arr[j + 1]:
                    update_display(
                        f"【条件判定】 pointT({j}) [{arr[j]}] > pointT({j+1}) [{arr[j+1]}] ➔ **Yes (Y)**",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_COND,
                    )

                    # 退避と交換（各ステップを細かく矢印追従）
                    save = arr[j]
                    update_display(
                        f"【退避】 pointT({j}) [{save}] ➔ save に保存",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_SWAP1,
                    )

                    arr[j] = arr[j + 1]
                    update_display(
                        f"【代入】 pointT({j+1}) [{arr[j+1]}] ➔ pointT({j}) に上書き",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_SWAP2,
                    )

                    arr[j + 1] = save
                    update_display(
                        f"【戻し】 save [{save}] ➔ pointT({j+1}) に代入 (交換完了)",
                        arr,
                        [j, j + 1],
                        swapped=True,
                        y_ratio=Y_SWAP3,
                    )
                else:
                    update_display(
                        f"【条件判定】 pointT({j}) [{arr[j]}] > pointT({j+1}) [{arr[j+1]}] ➔ **No (N)** (交換なし)",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_COND,
                    )

    # ----------------------------------------------------
    # 2. 選択ソート
    # ----------------------------------------------------
    elif "選択ソート" in algorithm:
        for i in range(0, n - 1):
            min_idx = i
            update_display(
                f"【外側ループ】 i = {i} (最小値探索: min_idx = {i})",
                arr,
                [i],
                y_ratio=0.15,
            )

            for j in range(i + 1, n):
                update_display(
                    f"【比較】 pointT({j}) と 最小値 pointT({min_idx}) を比較",
                    arr,
                    [min_idx, j],
                    y_ratio=0.35,
                )

                if arr[j] < arr[min_idx]:
                    min_idx = j
                    update_display(
                        f"【最小値更新】 min_idx = {min_idx} (値: {arr[min_idx]})",
                        arr,
                        [min_idx],
                        y_ratio=0.50,
                    )

            if min_idx != i:
                save = arr[i]
                arr[i] = arr[min_idx]
                arr[min_idx] = save
                update_display(
                    f"【交換】 pointT({min_idx}) と pointT({i}) を交換",
                    arr,
                    [i, min_idx],
                    swapped=True,
                    y_ratio=0.65,
                )

    # ----------------------------------------------------
    # 3. 挿入ソート
    # ----------------------------------------------------
    elif "挿入ソート" in algorithm:
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            update_display(
                f"【外側ループ】 i = {i} (挿入値 save = {key})",
                arr,
                [i],
                y_ratio=0.15,
            )

            while j >= 0 and arr[j] > key:
                update_display(
                    f"【比較＆シフト】 pointT({j}) [{arr[j]}] > {key} ➔ 右へシフト",
                    arr,
                    [j, j + 1],
                    y_ratio=0.40,
                )
                arr[j + 1] = arr[j]
                j -= 1

            arr[j + 1] = key
            update_display(
                f"【挿入】 pointT({j+1}) に {key} を挿入",
                arr,
                [j + 1],
                swapped=True,
                y_ratio=0.65,
            )

    status_placeholder.success("🎉 ソート処理が完了しました！")
    chart_placeholder.pyplot(draw_chart(arr))

    # 完了時は矢印なしで元画像を表示
    if base_image is not None:
        img_placeholder.image(base_image, caption="ソート完了")