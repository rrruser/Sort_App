document.addEventListener('DOMContentLoaded', () => {
    // UI要素
    const algoSelect = document.getElementById('algoSelect');
    const speedRange = document.getElementById('speedRange');
    const speedVal = document.getElementById('speedVal');
    const arrayInput = document.getElementById('arrayInput');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const startBtn = document.getElementById('startBtn');

    const statusText = document.getElementById('statusText');
    const imgPlaceholder = document.getElementById('imgPlaceholder');
    const flowchartCanvas = document.getElementById('flowchartCanvas');
    const flowCtx = flowchartCanvas.getContext('2d');

    const traceI = document.getElementById('traceI');
    const traceJ = document.getElementById('traceJ');
    const traceSave = document.getElementById('traceSave');
    const tracePj = document.getElementById('tracePj');
    const tracePj1 = document.getElementById('tracePj1');
    const popupBox = document.getElementById('popupBox');

    const sortCanvas = document.getElementById('sortCanvas');
    const sortCtx = sortCanvas.getContext('2d');

    let loadedImage = null;
    let isRunning = false;
    let currentData = [64, 34, 25, 12, 22];

    speedRange.addEventListener('input', (e) => {
        speedVal.textContent = `${e.target.value}s`;
    });

    // 画像ドラッグ＆ドロップ処理
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.background = '#e2f0ff'; });
    dropZone.addEventListener('dragleave', () => { dropZone.style.background = '#f0f7ff'; });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.background = '#f0f7ff';
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
            const img = new Image();
            img.onload = () => {
                loadedImage = img;
                imgPlaceholder.style.display = 'none';
                flowchartCanvas.style.display = 'block';
                drawFlowchartWithArrow(-1);
            };
            img.src = evt.target.result;
        };
        reader.readAsDataURL(file);
    }

    // 流れ図画像 ＋ 右側30pxシフト矢印（⇦）の描画
    function drawFlowchartWithArrow(yRatio) {
        if (!loadedImage) return;
        const extraMargin = 40;
        flowchartCanvas.width = loadedImage.width + extraMargin;
        flowchartCanvas.height = loadedImage.height;

        flowCtx.clearRect(0, 0, flowchartCanvas.width, flowchartCanvas.height);
        flowCtx.drawImage(loadedImage, 0, 0);

        if (yRatio >= 0) {
            const y = loadedImage.height * yRatio;
            const shiftPx = 30;
            const xEnd = loadedImage.width * 0.72 + shiftPx;
            const xStart = Math.min(flowchartCanvas.width - 5, loadedImage.width * 0.95 + shiftPx);

            flowCtx.strokeStyle = '#eb3232';
            flowCtx.lineWidth = Math.max(4, loadedImage.width * 0.015);
            flowCtx.beginPath();
            flowCtx.moveTo(xStart, y);
            flowCtx.lineTo(xEnd, y);
            flowCtx.stroke();

            const headSize = Math.max(8, loadedImage.height * 0.025);
            flowCtx.fillStyle = '#eb3232';
            flowCtx.beginPath();
            flowCtx.moveTo(xEnd, y);
            flowCtx.lineTo(xEnd + headSize, y - headSize);
            flowCtx.lineTo(xEnd + headSize, y + headSize);
            flowCtx.closePath();
            flowCtx.fill();
        }
    }

    // ----------------------------------------------------
    // なめらかで高速なソート棒グラフアニメーション
    // ----------------------------------------------------
    class SortVisualizer {
        constructor(canvas, ctx) {
            this.canvas = canvas;
            this.ctx = ctx;
            this.bars = [];
            this.saveBar = null;
            this.yMax = 100;
        }

        init(arr) {
            const maxVal = Math.max(...arr, 10);
            this.yMax = maxVal * 1.25;
            const n = arr.length;
            const padding = 40;
            const usableWidth = this.canvas.width - padding * 2;
            const barWidth = Math.min(45, (usableWidth / (n + 1.5)));
            const gap = (usableWidth - barWidth * (n + 1.5)) / n;

            this.bars = arr.map((val, idx) => ({
                value: val,
                x: padding + idx * (barWidth + gap),
                y: this.canvas.height - 40,
                targetX: padding + idx * (barWidth + gap),
                targetY: this.canvas.height - 40,
                width: barWidth,
                color: '#1f77b4',
                label: `pointT(${idx})`
            }));

            // save 枠（右端破線）
            const saveX = padding + n * (barWidth + gap) + 10;
            this.saveSlot = {
                x: saveX,
                y: this.canvas.height - 40,
                width: barWidth,
                height: (this.canvas.height - 80) * 0.85
            };
            this.saveBar = null;
            this.render();
        }

        render() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            // 1. save 破線枠描画
            this.ctx.strokeStyle = '#888888';
            this.ctx.setLineDash([4, 4]);
            this.ctx.strokeRect(this.saveSlot.x, this.saveSlot.y - this.saveSlot.height, this.saveSlot.width, this.saveSlot.height);
            this.ctx.setLineDash([]);
            this.ctx.fillStyle = '#dc3545';
            this.ctx.font = 'bold 12px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('save', this.saveSlot.x + this.saveSlot.width / 2, this.saveSlot.y + 20);

            // 2. 配列バー描画
            this.bars.forEach((bar) => {
                const heightRatio = bar.value / this.yMax;
                const h = (this.canvas.height - 80) * heightRatio;

                this.ctx.fillStyle = bar.color;
                this.ctx.fillRect(bar.x, bar.y - h, bar.width, h);

                // 数値表示
                this.ctx.fillStyle = '#000';
                this.ctx.font = 'bold 12px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(bar.value, bar.x + bar.width / 2, bar.y - h - 5);

                // ラベル表示
                this.ctx.fillStyle = '#555';
                this.ctx.font = '11px sans-serif';
                this.ctx.fillText(bar.label, bar.x + bar.width / 2, bar.y + 18);
            });

            // 3. save バー（退避時）
            if (this.saveBar) {
                const heightRatio = this.saveBar.value / this.yMax;
                const h = (this.canvas.height - 80) * heightRatio;
                this.ctx.fillStyle = this.saveBar.color || '#dc3545';
                this.ctx.fillRect(this.saveBar.x, this.saveBar.y - h, this.saveBar.width, h);

                this.ctx.fillStyle = '#dc3545';
                this.ctx.font = 'bold 12px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(this.saveBar.value, this.saveBar.x + this.saveBar.width / 2, this.saveBar.y - h - 5);
            }
        }

        // ヌルヌル動く滑らかな連続位置補間 (連続モーション)
        async animateMove(animations, durationMs = 150) {
            const startTime = performance.now();
            const startPositions = animations.map(a => ({ obj: a.obj, startX: a.obj.x, startY: a.obj.y }));

            return new Promise((resolve) => {
                const step = (now) => {
                    const elapsed = now - startTime;
                    const progress = Math.min(1, elapsed / durationMs);

                    // イージング
                    const ease = progress * (2 - progress);

                    animations.forEach((anim, i) => {
                        const start = startPositions[i];
                        anim.obj.x = start.startX + (anim.targetX - start.startX) * ease;
                        anim.obj.y = start.startY + (anim.targetY - start.startY) * ease;
                    });

                    this.render();

                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else {
                        animations.forEach(anim => {
                            anim.obj.x = anim.targetX;
                            anim.obj.y = anim.targetY;
                        });
                        this.render();
                        resolve();
                    }
                };
                requestAnimationFrame(step);
            });
        }
    }

    const visualizer = new SortVisualizer(sortCanvas, sortCtx);

    function getBaseSpeed() {
        return parseFloat(speedRange.value) * 1000;
    }

    function sleep(ms) {
        return new Promise(r => setTimeout(r, ms));
    }

    // ----------------------------------------------------
    // バブルソート実行エンジン
    // ----------------------------------------------------
    async function runBubbleSort() {
        const arr = [...currentData];
        const n = arr.length;
        visualizer.init(arr);

        const Y_LOOP1 = 0.10, Y_LOOP2 = 0.22, Y_COND = 0.35, Y_SWAP1 = 0.48, Y_SWAP2 = 0.58, Y_SWAP3 = 0.68;
        let save = '-';

        const maxI = n >= 2 ? n - 2 : 0;

        for (let i = maxI; i >= 0; i--) {
            if (!isRunning) return;
            updateUI(`【ループ1】 i = ${i} (i ≧ 0)`, Y_LOOP1, i, '-', save, null, null);
            await sleep(getBaseSpeed());

            for (let j = 0; j <= i; j++) {
                if (!isRunning) return;

                // 比較対象ハイライト
                visualizer.bars.forEach((b, idx) => b.color = (idx === j || idx === j + 1) ? '#ff7f0e' : '#1f77b4');
                visualizer.render();

                updateUI(`【ループ2】 j = ${j} (j ≦ i)`, Y_LOOP2, i, j, save, arr[j], arr[j+1]);
                await sleep(getBaseSpeed() * 0.7);

                if (arr[j] > arr[j + 1]) {
                    // 交換する判定ポップアップ
                    setPopup('swap');
                    updateUI(`【比較】 pointT(${j})[${arr[j]}] > pointT(${j+1})[${arr[j+1]}] ➔ **Yes (交換)**`, Y_COND, i, j, save, arr[j], arr[j+1]);
                    await sleep(getBaseSpeed() * 0.8);

                    // --- 高速連続交換動作 (超高速スライド) ---
                    const swapAnimSpeed = Math.max(40, getBaseSpeed() * 0.2); // 通常の5倍速

                    // 1. pointT(j) -> save へなめらかに移動
                    save = arr[j];
                    const movingBar = visualizer.bars[j];
                    updateUI(`【退避】 pointT(${j}) [${save}] ➔ save`, Y_SWAP1, i, j, save, arr[j], arr[j+1]);

                    await visualizer.animateMove([
                        { obj: movingBar, targetX: visualizer.saveSlot.x, targetY: visualizer.saveSlot.y }
                    ], swapAnimSpeed);

                    visualizer.saveBar = { ...movingBar, x: visualizer.saveSlot.x, y: visualizer.saveSlot.y };
                    movingBar.value = 0; // 一時非表示
                    visualizer.render();

                    // 2. pointT(j+1) -> pointT(j) へなめらかに移動
                    arr[j] = arr[j + 1];
                    const nextBar = visualizer.bars[j + 1];
                    updateUI(`【代入】 pointT(${j+1}) [${arr[j+1]}] ➔ pointT(${j})`, Y_SWAP2, i, j, save, arr[j], arr[j+1]);

                    const targetX_j = visualizer.saveSlot.x - (n - j + 0.4) * (nextBar.width + 10);
                    await visualizer.animateMove([
                        { obj: nextBar, targetX: startXOf(j, n, visualizer.canvas.width), targetY: nextBar.y }
                    ], swapAnimSpeed);

                    // 配列内部データ並び替え
                    visualizer.bars[j].value = arr[j];
                    visualizer.bars[j].color = '#2ca02c';

                    // 3. save -> pointT(j+1) へ戻す
                    arr[j + 1] = save;
                    updateUI(`【戻し】 save [${save}] ➔ pointT(${j+1}) (完了)`, Y_SWAP3, i, j, save, arr[j], arr[j+1]);

                    await visualizer.animateMove([
                        { obj: visualizer.saveBar, targetX: startXOf(j + 1, n, visualizer.canvas.width), targetY: nextBar.y }
                    ], swapAnimSpeed);

                    visualizer.bars[j + 1].value = save;
                    visualizer.bars[j + 1].color = '#2ca02c';
                    visualizer.saveBar = null;
                    visualizer.render();

                } else {
                    setPopup('noswap');
                    updateUI(`【比較】 pointT(${j})[${arr[j]}] > pointT(${j+1})[${arr[j+1]}] ➔ **No (維持)**`, Y_COND, i, j, save, arr[j], arr[j+1]);
                    await sleep(getBaseSpeed());
                }
            }
        }

        setPopup('empty');
        statusText.textContent = '🎉 ソートが完了しました！';
        drawFlowchartWithArrow(-1);
        visualizer.bars.forEach(b => b.color = '#1f77b4');
        visualizer.render();
        isRunning = false;
        startBtn.disabled = false;
    }

    function startXOf(idx, n, canvasWidth) {
        const padding = 40;
        const usableWidth = canvasWidth - padding * 2;
        const barWidth = Math.min(45, (usableWidth / (n + 1.5)));
        const gap = (usableWidth - barWidth * (n + 1.5)) / n;
        return padding + idx * (barWidth + gap);
    }

    function updateUI(text, yRatio, iVal, jVal, saveVal, pj, pj1) {
        statusText.textContent = text;
        drawFlowchartWithArrow(yRatio);
        traceI.textContent = iVal;
        traceJ.textContent = jVal;
        traceSave.textContent = saveVal;
        tracePj.textContent = pj !== null ? pj : '-';
        tracePj1.textContent = pj1 !== null ? pj1 : '-';
    }

    function setPopup(type) {
        if (type === 'swap') {
            popupBox.className = 'popup-box popup-swap';
            popupBox.textContent = '🚨 【判定結果】 交換する (YES)';
        } else if (type === 'noswap') {
            popupBox.className = 'popup-box popup-noswap';
            popupBox.textContent = '✅ 【判定結果】 交換しない (NO)';
        } else {
            popupBox.className = 'popup-box popup-empty';
            popupBox.innerHTML = '&nbsp;';
        }
    }

    // 開始ボタン押下
    startBtn.addEventListener('click', () => {
        if (isRunning) return;
        try {
            currentData = arrayInput.value.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));
            if (currentData.length === 0) throw new Error();
        } catch {
            alert('初期配列をカンマ区切りの数値で入力してください');
            return;
        }

        isRunning = true;
        startBtn.disabled = true;

        if (algoSelect.value === 'bubble') {
            runBubbleSort();
        } else {
            // 他のアルゴリズムも同様に起動
            runBubbleSort();
        }
    });

    // 初期化表示
    visualizer.init(currentData);
});