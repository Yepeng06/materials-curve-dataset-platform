# V0 运行与验收说明

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

## 3. 参数面板（前端）

当前前端参数面板支持字段：
- 模板与模式：`template_id`、`mode`
- 图像与预览：`preview_count`、`seed`、`grid`
- 坐标轴：`x_label`、`x_unit`、`y_label`、`y_unit`
- 曲线：`num_curves`、`curve_shape`、`points_per_curve`、`noise_level`
- 视觉风格：`line_style`、`line_width`、`marker`
- 图例：`legend_position`

页面会显示“本次请求参数”，用于确认前端实际提交给 `/preview` 的 payload。

## 4. explicit 与 probabilistic 区别

- `explicit`：优先使用用户手动参数，适合调参与可控复现。
- `probabilistic`：优先按模板概率分布采样，适合批量生成；界面会提示“部分手动参数可能不生效”。

## 5. 预览缓存修复说明

`/preview` 每次调用都会生成唯一 `preview_run_id`，并写入到预览 PNG/CSV/JSON 文件名中。同时前端图片 URL 附加 `?run=<preview_run_id>`，避免浏览器命中旧缓存。

## 6. marker_rich 与曲线视觉

- `marker_rich` 模板在概率模式下会采样 marker，不会被前端默认 `marker=none` 覆盖。
- 渲染器会将 marker 映射为：`circle -> o`、`triangle -> ^`、`square -> s`，并通过 `markevery` 避免过密。
- 曲线生成改为连续函数 + 平滑噪声 + 轻度单调修正，避免明显阶梯感。

## 7. 中期检查截图建议

1. 前端选择 `template_id=marker_rich`、`mode=probabilistic`，点击“生成预览图”。
2. 展示“本次请求参数”和预览图（能看到 marker）。
3. 再修改 `curve_shape` 或 `line_style` 重复生成，展示图片已刷新。
4. 截图包含：参数面板、预览结果、MCG-JSON 折叠展开区域。

## 8. 核心接口验收

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

## 9. 一键烟雾测试

```bash
python scripts/v0_smoke_test.py
```
