# V0fix-final-2 运行说明

## 模板与参数优先级
- explicit：手动参数优先；若点击“应用模板默认参数”，前端会把模板 `default_parameters` 写入表单。
- probabilistic：模板概率分布优先；前端默认值不会覆盖 `num_curves/curve_shape/line_style/marker/legend_position/grid` 的采样结果。

## 前端交互
- 模板区域新增“应用模板默认参数”按钮。
- 模板下方显示说明与关键效果。
- 页面可查看“本次请求参数”和“当前实际生效参数”。

## 曲线形态
- near_linear：近似线性但带轻微弯曲。
- primary_obvious：前期快、后期缓。
- accelerated_obvious：后期上翘明显。
- three_stage：主蠕变-稳态-加速三阶段。
- irregular：整体上升并带轻微实验波动。

## 模板预期效果
- real_mainstream：主流论文风格，实线或少量 marker。
- multi_curve_comparison：3-5 条，区分明显。
- black_white_paper：黑灰配色、黑白论文视觉。
- marker_rich：强 marker（不含 none）。
- grid_interference：高概率 grid=true。
- low_quality_screenshot：当前仅参数占位（V1/V2 再扩展真实退化）。
- three_stage_creep：高概率三阶段曲线。

## 未实现（保持 V0）
- YOLO/COCO/mask/OCR 导出。
- 真实截图退化流程。

## 当前稳定版本入口
- 当前推荐优先查看：`docs/V0fix-final-2_RELEASE.md`
