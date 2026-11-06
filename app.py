import time
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import streamlit as st

# ページ設定
st.set_page_config(
    page_title="ソートアルゴリズム＆流れ図ビジュアルアナライザー", layout="wide"
)

# ----------------------------------------------------
# カスタムCSS: 上部余白の削減 ＆ 文字サイズを最大1.5rem以下に制限
# ----------------------------------------------------
st.markdown(
    """
    <style>
    /* 上部・周囲の余白を最小化 */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* タイトル・見出しのフォントサイズ制限 (最大1.5rem以下) と余白削減 */
    h1 {
        font-size: 1.4rem !important;
        margin-top: 0rem !important;
        margin-bottom: 0.3rem !important;
        padding-top: 0rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.3rem !important;
    }
    h3 {
        font-size: 1.05rem !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.2rem !important;
    }
    p, label, span {
        font-size: 0.9rem !important;
    }

    /* 引用・ステータス表示エリアのコンパクト化 */
    blockquote {
        margin: 0.2rem 0 !important;
        padding: 0.3rem 0.6rem !important;
    }

    /* Matplotlib等の画像表示上下の余白を排除 */
    .stImage, .stPlotlyChart {
        margin-bottom: 0rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ヘッダー領域にタイトルを配置
st.markdown("<h1>ソートアルゴリズム＆流れ図ビジュアライザ</h1>", unsafe_allow_html=True)

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
    "流れ図画像をドラッグ＆ドロップ", type=["png", "jpg", "jpeg"]
)

start_button = st.sidebar.button("ソート実行", type="primary")

# 左右2カラムレイアウト
col_left, col_right = st.columns([1, 1])

# ----------------------------------------------------
# 左カラム: 実行状態テキスト(上) ＋ 流れ図画像(下)
# ----------------------------------------------------
with col_left:
    st.markdown("### 📌 実行状態と流れ図")
    status_placeholder = st.empty()  # 上側のテキスト枠
    img_placeholder = st.empty()     # 下側の画像枠

    # ブラウザ縦幅700px内に収めるため、画像最大高さを 480px に設定
    MAX_IMG_HEIGHT = 480
    base_image = None

    if uploaded_file is not None:
        raw_img = Image.open(uploaded_file).convert("RGB")
        if raw_img.height > MAX_IMG_HEIGHT:
            aspect_ratio = raw_img.width / raw_img.height
            new_width = int(MAX_IMG_HEIGHT * aspect_ratio)
            base_image = raw_img.resize((new_width, MAX_IMG_HEIGHT))
        else:
            base_image = raw_img
        img_placeholder.image(base_image, caption="アップロードされた流れ図")
    else:
        img_placeholder.info(
            "👈 サイドバーから流れ図画像をドラッグ＆ドロップしてください。"
        )

# ----------------------------------------------------
# 右カラム: ソートアニメーション棒グラフ
# ----------------------------------------------------
with col_right:
    st.markdown("### 📊 ソートアニメーション")
    chart_placeholder = st.empty()


def draw_arrow_on_image(image, y_ratio):
    """画像上の指定高さ比率(0.0〜1.0)の位置に赤色矢印（⇦）を描画"""
    if image is None:
        return None

    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    w, h = img_copy.size

    y = int(h * y_ratio)
    arrow_color = (235, 40, 40)
    line_width = max(3, int(w * 0.015))

    x_end = int(w * 0.72)
    x_start = int(w * 0.95)

    draw.line([(x_start, y), (x_end, y)], fill=arrow_color, width=line_width)

    head_size = max(8, int(h * 0.025))
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
    """コンパクトサイズの棒グラフ描画"""
    colors = ["#1f77b4"] * len(arr)
    if active_indices:
        for idx in active_indices:
            if 0 <= idx < len(arr):
                colors[idx] = "#ff7f0e" if not swapped else "#2ca02c"

    # 全体サイズをコンパクト化 (figsize 縦幅を調整)
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    bars = ax.bar(range(len(arr)), arr, color=colors)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_ylim(0, max(arr) * 1.2 if len(arr) > 0 else 10)
    ax.set_xticks(range(len(arr)))
    ax.set_xticklabels([f"pointT({i})" for i in range(len(arr))], fontsize=9)
    plt.tight_layout()
    return fig


def update_display(node_text, arr, active_indices=None, swapped=False, y_ratio=0.1):
    """状態テキスト・矢印付き画像・グラフの一括更新"""
    status_placeholder.markdown(
        f"> **{node_text}**"
    )

    if base_image is not None:
        arrow_img = draw_arrow_on_image(base_image, y_ratio)
        img_placeholder.image(arrow_img)

    chart_placeholder.pyplot(
        draw_chart(arr, active_indices=active_indices, swapped=swapped)
    )

    time.sleep(speed)


# 初期表示
chart_placeholder.pyplot(draw_chart(initial_data))

# ソート処理の実行
if start_button:
    arr = initial_data.copy()
    n = len(arr)

    if "バブルソート" in algorithm:
        Y_LOOP1 = 0.10
        Y_LOOP2 = 0.22
        Y_COND = 0.35
        Y_SWAP1 = 0.48
        Y_SWAP2 = 0.58
        Y_SWAP3 = 0.68

        max_i = n - 2 if n >= 2 else 0

        for i in range(max_i, -1, -1):
            update_display(
                f"【ループ1】 i = {i} (i ≧ 0)",
                arr,
                y_ratio=Y_LOOP1,
            )

            for j in range(0, i + 1):
                update_display(
                    f"【ループ2】 j = {j} (j ≦ i)",
                    arr,
                    [j, j + 1],
                    y_ratio=Y_LOOP2,
                )

                if arr[j] > arr[j + 1]:
                    update_display(
                        f"【比較】 pointT({j})[{arr[j]}] > pointT({j+1})[{arr[j+1]}] ➔ **Yes**",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_COND,
                    )

                    save = arr[j]
                    update_display(
                        f"【退避】 pointT({j}) [{save}] ➔ save",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_SWAP1,
                    )

                    arr[j] = arr[j + 1]
                    update_display(
                        f"【代入】 pointT({j+1}) [{arr[j+1]}] ➔ pointT({j})",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_SWAP2,
                    )

                    arr[j + 1] = save
                    update_display(
                        f"【戻し】 save [{save}] ➔ pointT({j+1}) (交換完了)",
                        arr,
                        [j, j + 1],
                        swapped=True,
                        y_ratio=Y_SWAP3,
                    )
                else:
                    update_display(
                        f"【比較】 pointT({j})[{arr[j]}] > pointT({j+1})[{arr[j+1]}] ➔ **No**",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_COND,
                    )

    elif "選択ソート" in algorithm:
        for i in range(0, n - 1):
            min_idx = i
            update_display(
                f"【外側ループ】 i = {i} (探索開始: min_idx = {i})",
                arr,
                [i],
                y_ratio=0.15,
            )

            for j in range(i + 1, n):
                update_display(
                    f"【比較】 pointT({j}) と 最小値 pointT({min_idx})",
                    arr,
                    [min_idx, j],
                    y_ratio=0.35,
                )

                if arr[j] < arr[min_idx]:
                    min_idx = j
                    update_display(
                        f"【更新】 min_idx = {min_idx} (値: {arr[min_idx]})",
                        arr,
                        [min_idx],
                        y_ratio=0.50,
                    )

            if min_idx != i:
                save = arr[i]
                arr[i] = arr[min_idx]
                arr[min_idx] = save
                update_display(
                    f"【交換】 pointT({min_idx}) ↔ pointT({i})",
                    arr,
                    [i, min_idx],
                    swapped=True,
                    y_ratio=0.65,
                )

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
                    f"【比較＆シフト】 pointT({j})[{arr[j]}] > {key}",
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

    if base_image is not None:
        img_placeholder.image(base_image)