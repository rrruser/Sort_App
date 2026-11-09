import time
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import streamlit as st

# ページ設定
st.set_page_config(
    page_title="ソートアルゴリズム＆流れ図ビジュアルアナライザー", layout="wide"
)

# カスタムCSS: 上部余白の削減 ＆ 文字サイズを最大1.5rem以下に制限
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
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
    blockquote {
        margin: 0.2rem 0 !important;
        padding: 0.3rem 0.6rem !important;
    }
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

# 3カラムレイアウト（左：流れ図、中央：変数トレース、右：グラフ）
col_left, col_mid, col_right = st.columns([1.0, 0.6, 1.1])

# ----------------------------------------------------
# 1. 左カラム: 実行状態テキスト(上) ＋ 流れ図画像(下)
# ----------------------------------------------------
with col_left:
    st.markdown("### 📌 実行状態と流れ図")
    status_placeholder = st.empty()
    img_placeholder = st.empty()

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
# 2. 中央カラム: 変数トレース表示
# ----------------------------------------------------
with col_mid:
    st.markdown("### 🔍 変数トレース")
    trace_placeholder = st.empty()

# ----------------------------------------------------
# 3. 右カラム: ソートアニメーション棒グラフ
# ----------------------------------------------------
with col_right:
    st.markdown("### 📊 ソートアニメーション")
    chart_placeholder = st.empty()


def draw_arrow_on_image(image, y_ratio):
    """
    画像の右側に40pxの余白を追加し、元画像から30px程度右寄りに赤矢印（⇦）を描画する関数
    """
    if image is None:
        return None

    w, h = image.size
    extra_margin = 40  # 矢印表示用スペース
    new_w = w + extra_margin

    # キャンバスを右側に少し広げる
    img_extended = Image.new("RGB", (new_w, h), (255, 255, 255))
    img_extended.paste(image, (0, 0))

    draw = ImageDraw.Draw(img_extended)
    y = int(h * y_ratio)
    arrow_color = (235, 40, 40)
    line_width = max(3, int(w * 0.015))

    # 従来の比率位置より30px右側にシフト
    shift_px = 30
    x_end = int(w * 0.72) + shift_px
    x_start = min(new_w - 5, int(w * 0.95) + shift_px)

    # 線と頭を描画
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

    return img_extended


def draw_trace_table(i_val="-", j_val="-", save_val="-", arr=None, j_idx=None):
    """変数トレース用のテーブルHTMLを作成"""
    val_j = "-"
    val_j1 = "-"

    if arr is not None and j_idx is not None:
        if 0 <= j_idx < len(arr):
            val_j = str(arr[j_idx])
        if 0 <= j_idx + 1 < len(arr):
            val_j1 = str(arr[j_idx + 1])

    html = f"""
    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 12px;">
        <table style="width:100%; border-collapse: collapse; font-size: 0.92rem;">
            <tr style="border-bottom: 1px solid #e9ecef;">
                <td style="padding: 8px 4px; font-weight: bold; color: #495057;">ループ変数 <code style="color: #0d6efd;">i</code></td>
                <td style="padding: 8px 4px; text-align: right; font-weight: bold; font-size: 1.1rem; color: #0d6efd;">{i_val}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e9ecef;">
                <td style="padding: 8px 4px; font-weight: bold; color: #495057;">ループ変数 <code style="color: #0d6efd;">j</code></td>
                <td style="padding: 8px 4px; text-align: right; font-weight: bold; font-size: 1.1rem; color: #0d6efd;">{j_val}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e9ecef;">
                <td style="padding: 8px 4px; font-weight: bold; color: #495057;">退避変数 <code style="color: #dc3545;">save</code></td>
                <td style="padding: 8px 4px; text-align: right; font-weight: bold; font-size: 1.1rem; color: #dc3545;">{save_val}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e9ecef;">
                <td style="padding: 8px 4px; color: #495057;">要素 <code>pointT(j)</code></td>
                <td style="padding: 8px 4px; text-align: right; font-weight: bold; color: #198754;">{val_j}</td>
            </tr>
            <tr>
                <td style="padding: 8px 4px; color: #495057;">要素 <code>pointT(j+1)</code></td>
                <td style="padding: 8px 4px; text-align: right; font-weight: bold; color: #198754;">{val_j1}</td>
            </tr>
        </table>
    </div>
    """
    return html


def draw_chart(arr, active_indices=None, swapped=False):
    """棒グラフ描画"""
    colors = ["#1f77b4"] * len(arr)
    if active_indices:
        for idx in active_indices:
            if 0 <= idx < len(arr):
                colors[idx] = "#ff7f0e" if not swapped else "#2ca02c"

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


def update_display(
    node_text,
    arr,
    active_indices=None,
    swapped=False,
    y_ratio=0.1,
    i_val="-",
    j_val="-",
    save_val="-",
    j_idx=None,
):
    """状態テキスト・矢印画像・トレース表・グラフを一括更新"""
    status_placeholder.markdown(f"> **{node_text}**")

    # トレース表更新
    trace_placeholder.markdown(
        draw_trace_table(i_val, j_val, save_val, arr, j_idx),
        unsafe_allow_html=True,
    )

    # 矢印付き画像更新
    if base_image is not None:
        arrow_img = draw_arrow_on_image(base_image, y_ratio)
        img_placeholder.image(arrow_img)

    # グラフ更新
    chart_placeholder.pyplot(
        draw_chart(arr, active_indices=active_indices, swapped=swapped)
    )

    time.sleep(speed)


# 初期画面の描画
trace_placeholder.markdown(
    draw_trace_table(arr=initial_data), unsafe_allow_html=True
)
chart_placeholder.pyplot(draw_chart(initial_data))

# ソート処理の実行
if start_button:
    arr = initial_data.copy()
    n = len(arr)
    save = "-"

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
                i_val=i,
                j_val="-",
                save_val=save,
            )

            for j in range(0, i + 1):
                update_display(
                    f"【ループ2】 j = {j} (j ≦ i)",
                    arr,
                    [j, j + 1],
                    y_ratio=Y_LOOP2,
                    i_val=i,
                    j_val=j,
                    save_val=save,
                    j_idx=j,
                )

                if arr[j] > arr[j + 1]:
                    update_display(
                        f"【比較】 pointT({j})[{arr[j]}] > pointT({j+1})[{arr[j+1]}] ➔ **Yes**",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_COND,
                        i_val=i,
                        j_val=j,
                        save_val=save,
                        j_idx=j,
                    )

                    save = arr[j]
                    update_display(
                        f"【退避】 pointT({j}) [{save}] ➔ save",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_SWAP1,
                        i_val=i,
                        j_val=j,
                        save_val=save,
                        j_idx=j,
                    )

                    arr[j] = arr[j + 1]
                    update_display(
                        f"【代入】 pointT({j+1}) [{arr[j+1]}] ➔ pointT({j})",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_SWAP2,
                        i_val=i,
                        j_val=j,
                        save_val=save,
                        j_idx=j,
                    )

                    arr[j + 1] = save
                    update_display(
                        f"【戻し】 save [{save}] ➔ pointT({j+1}) (交換完了)",
                        arr,
                        [j, j + 1],
                        swapped=True,
                        y_ratio=Y_SWAP3,
                        i_val=i,
                        j_val=j,
                        save_val=save,
                        j_idx=j,
                    )
                else:
                    update_display(
                        f"【比較】 pointT({j})[{arr[j]}] > pointT({j+1})[{arr[j+1]}] ➔ **No**",
                        arr,
                        [j, j + 1],
                        y_ratio=Y_COND,
                        i_val=i,
                        j_val=j,
                        save_val=save,
                        j_idx=j,
                    )

    elif "選択ソート" in algorithm:
        for i in range(0, n - 1):
            min_idx = i
            update_display(
                f"【外側ループ】 i = {i} (探索開始: min_idx = {i})",
                arr,
                [i],
                y_ratio=0.15,
                i_val=i,
                j_val="-",
                save_val=save,
            )

            for j in range(i + 1, n):
                update_display(
                    f"【比較】 pointT({j}) と 最小値 pointT({min_idx})",
                    arr,
                    [min_idx, j],
                    y_ratio=0.35,
                    i_val=i,
                    j_val=j,
                    save_val=save,
                    j_idx=j,
                )

                if arr[j] < arr[min_idx]:
                    min_idx = j
                    update_display(
                        f"【更新】 min_idx = {min_idx} (値: {arr[min_idx]})",
                        arr,
                        [min_idx],
                        y_ratio=0.50,
                        i_val=i,
                        j_val=j,
                        save_val=save,
                        j_idx=j,
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
                    i_val=i,
                    j_val="-",
                    save_val=save,
                )

    elif "挿入ソート" in algorithm:
        for i in range(1, n):
            key = arr[i]
            save = key
            j = i - 1
            update_display(
                f"【外側ループ】 i = {i} (挿入値 save = {key})",
                arr,
                [i],
                y_ratio=0.15,
                i_val=i,
                j_val=j,
                save_val=save,
                j_idx=j,
            )

            while j >= 0 and arr[j] > key:
                update_display(
                    f"【比較＆シフト】 pointT({j})[{arr[j]}] > {key}",
                    arr,
                    [j, j + 1],
                    y_ratio=0.40,
                    i_val=i,
                    j_val=j,
                    save_val=save,
                    j_idx=j,
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
                i_val=i,
                j_val=j + 1,
                save_val=save,
                j_idx=j + 1,
            )

    status_placeholder.success("🎉 ソート処理が完了しました！")
    trace_placeholder.markdown(
        draw_trace_table(i_val="完了", j_val="完了", save_val=save, arr=arr),
        unsafe_allow_html=True,
    )
    chart_placeholder.pyplot(draw_chart(arr))

    if base_image is not None:
        img_placeholder.image(base_image)