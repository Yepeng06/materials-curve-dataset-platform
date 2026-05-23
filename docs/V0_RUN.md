# V0 运行与验收说明（V0fix-final）

## 1. 安装依赖

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend
```bash
cd frontend
npm install
cd ..
```

## 2. 启动服务

### 启动 backend
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 启动 frontend
```bash
cd frontend
npm run dev
```
默认前端访问：`http://127.0.0.1:5173`

## 3. V0fix-final 修复点

### 3.1 曲线生成逻辑：连续曲线 / 平滑折线
- 曲线生成采用“正斜率积分法”：先生成连续 slope，再叠加平滑噪声并做正值约束，最后积分得到 y。
- 不使用 step/steps 绘图方式。
- 不对 y 做不必要离散化/整数化，保持连续变化和真实感。

### 3.2 三种曲线形态视觉区别
- `near_linear`：整体接近线性，允许轻微弯曲与扰动。
- `primary_obvious`：前期更快增长，中后期明显变缓。
- `accelerated_obvious`：前中期较平缓，后期出现明显上翘加速。
- 多曲线会有起点、终点、斜率和弯曲强度差异，减少重合。

### 3.3 MCG-JSON 预览优化
- 默认仅展示“标注摘要”（sample_id、mode、template_id、num_curves、curve_shape、marker、line_style、路径与 CSV 数量）。
- 点击“查看完整 MCG-JSON”后展开完整 JSON。
- 支持“隐藏 MCG-JSON”和“复制 MCG-JSON”。
- JSON 区域有 `max-height` 与滚动，避免页面过长。

### 3.4 当前版本边界
- 当前仍为 **V0fix-final**。
- 仍不包含 YOLO、COCO、mask、OCR 导出。

## 4. 参数面板（前端）

当前前端参数面板支持字段：
- 模板与模式：`template_id`、`mode`
- 图像与预览：`preview_count`、`seed`、`grid`
- 坐标轴：`x_label`、`x_unit`、`y_label`、`y_unit`
- 曲线：`num_curves`、`curve_shape`、`points_per_curve`、`noise_level`
- 视觉风格：`line_style`、`line_width`、`marker`
- 图例：`legend_position`

页面会显示“本次请求参数”，用于确认前端实际提交给 `/preview` 的 payload。

## 5. explicit 与 probabilistic 区别

- `explicit`：优先使用用户手动参数，适合调参与可控复现。
- `probabilistic`：优先按模板概率分布采样，适合批量生成；界面会提示“部分手动参数可能不生效”。

## 6. 预览缓存与 marker

- `/preview` 每次调用都会生成唯一 `preview_run_id`，并写入到预览 PNG/CSV/JSON 文件名中。
- 前端图片 URL 附加 `?run=<preview_run_id>`，避免浏览器命中旧缓存。
- marker 映射：`circle -> o`、`triangle -> ^`、`square -> s`，`none` 不显示 marker。

## 7. 核心接口验收

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/templates
```

```bash
curl -X POST http://127.0.0.1:8000/preview \
  -H 'Content-Type: application/json' \
  -d '{"mode":"probabilistic","template_id":"marker_rich","preview_count":3,"seed":20260520}'
```

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"dataset_name":"creep_synth","version":"v0.1","total_count":6,"mode":"probabilistic","template_id":"marker_rich","seed":20260520,"split":{"train":0.7,"val":0.2,"test":0.1}}'
```

## 8. 一键烟雾测试

```bash
python scripts/v0_smoke_test.py
```
