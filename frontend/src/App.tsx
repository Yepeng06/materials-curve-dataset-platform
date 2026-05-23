import { useEffect, useMemo, useState } from 'react'
import './App.css'

type PreviewItem = { image_path: string; annotation_path: string; csv_paths: string[]; annotation: Record<string, unknown> }
type TemplateItem = { template_id: string; template_name: string; description?: string; default_parameters?: Record<string, unknown>; key_effects?: string[] }
type PreviewParams = {
  mode: 'explicit' | 'probabilistic'
  template_id: string
  preview_count: number
  seed: number
  grid: boolean
  x_label: string
  x_unit: string
  y_label: string
  y_unit: string
  x_range: [number, number]
  num_curves: number
  curve_shape: string
  points_per_curve: number
  noise_level: number
  line_style: string
  line_width: number
  marker: string
  legend_position: string
  template_defaults_applied?: boolean
}

type GenerateParams = {
  dataset_name: string
  version: string
  total_count: number
  split: { train: number; val: number; test: number }
}

const defaults: PreviewParams = {
  mode: 'explicit',
  template_id: 'real_mainstream',
  preview_count: 3,
  seed: 20260520,
  grid: false,
  x_label: 'Creep time',
  x_unit: 'h',
  y_label: 'Creep strain',
  y_unit: '%',
  x_range: [0, 1000],
  num_curves: 3,
  curve_shape: 'near_linear',
  points_per_curve: 160,
  noise_level: 0.02,
  line_style: 'solid',
  line_width: 1.5,
  marker: 'none',
  legend_position: 'inside_upper_right',
  template_defaults_applied: false,
}

const generateDefaults: GenerateParams = {
  dataset_name: 'creep_synth',
  version: 'v0.1',
  total_count: 30,
  split: { train: 0.7, val: 0.2, test: 0.1 },
}

const probOverriddenLabel = '曲线形态、曲线数量、线型、标记点、图例位置、网格'
const templateDisplayNameMap: Record<string, string> = {
  'Low Quality Screenshot': '低质量截图风格',
  'High Quality Paper': '高清论文风格',
  Default: '默认模板',
}

const curveShapeOptions = [
  { value: 'near_linear', label: '近似线性' },
  { value: 'primary_obvious', label: '初期阶段明显' },
  { value: 'accelerated_obvious', label: '加速阶段明显' },
  { value: 'three_stage', label: '三阶段蠕变' },
  { value: 'irregular', label: '不规则波动' },
]
const lineStyleOptions = [
  { value: 'solid', label: '实线' },
  { value: 'dashed', label: '虚线' },
  { value: 'dotted', label: '点线' },
  { value: 'dashdot', label: '点划线' },
]
const markerOptions = [
  { value: 'none', label: '无' },
  { value: 'circle', label: '圆点' },
  { value: 'square', label: '方块' },
  { value: 'triangle', label: '三角形' },
  { value: 'diamond', label: '菱形' },
]
const legendOptions = [
  { value: 'none', label: '无图例' },
  { value: 'inside_upper_right', label: '右上' },
  { value: 'inside_upper_left', label: '左上' },
  { value: 'inside_lower_right', label: '右下' },
  { value: 'inside_lower_left', label: '左下' },
  { value: 'outside_right', label: '自动（右侧外部）' },
]

const enumLabel = (list: Array<{ value: string; label: string }>, value: unknown) => list.find((i) => i.value === value)?.label ?? String(value ?? '-')
const getTemplateDisplayName = (template: TemplateItem) => templateDisplayNameMap[template.template_name] ?? template.template_name

export default function App() {
  const [formError, setFormError] = useState<string>('')
  const [items, setItems] = useState<PreviewItem[]>([])
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [params, setParams] = useState<PreviewParams>(defaults)
  const [generateParams, setGenerateParams] = useState<GenerateParams>(generateDefaults)
  const [requestSnapshot, setRequestSnapshot] = useState<Record<string, unknown> | null>(null)
  const [actualSnapshot, setActualSnapshot] = useState<Record<string, unknown> | null>(null)
  const [expandedJson, setExpandedJson] = useState<Record<number, boolean>>({})
  const [generateResult, setGenerateResult] = useState<Record<string, unknown> | null>(null)
  const [previewCountInput, setPreviewCountInput] = useState(String(defaults.preview_count))
  const [seedInput, setSeedInput] = useState(String(defaults.seed))
  const [numCurvesInput, setNumCurvesInput] = useState(String(defaults.num_curves))
  const [pointsPerCurveInput, setPointsPerCurveInput] = useState(String(defaults.points_per_curve))
  const [noiseLevelInput, setNoiseLevelInput] = useState(String(defaults.noise_level))
  const [lineWidthInput, setLineWidthInput] = useState(String(defaults.line_width))
  const [xMinInput, setXMinInput] = useState(String(defaults.x_range[0]))
  const [xMaxInput, setXMaxInput] = useState(String(defaults.x_range[1]))
  const [totalCountInput, setTotalCountInput] = useState(String(generateDefaults.total_count))
  const [splitTrainInput, setSplitTrainInput] = useState(String(generateDefaults.split.train))
  const [splitValInput, setSplitValInput] = useState(String(generateDefaults.split.val))
  const [splitTestInput, setSplitTestInput] = useState(String(generateDefaults.split.test))

  const parseNumberInput = (value: string): number | null => {
    const trimmed = value.trim()
    if (trimmed === '') return null
    const n = Number(trimmed)
    return Number.isFinite(n) ? n : null
  }

  const validateAndClampNumber = (
    rawValue: string,
    opts: { label: string; min?: number; max?: number; integer?: boolean }
  ): number | null => {
    const parsed = parseNumberInput(rawValue)
    if (parsed === null) {
      setFormError(`${opts.label} 请输入合法数字`)
      return null
    }
    const normalized = opts.integer ? Math.trunc(parsed) : parsed
    if ((opts.min !== undefined && normalized < opts.min) || (opts.max !== undefined && normalized > opts.max)) {
      setFormError(`${opts.label} 超出范围`)
      return null
    }
    return normalized
  }

  useEffect(() => {
    fetch('http://127.0.0.1:8000/templates').then((r) => r.json()).then((d) => setTemplates(d.items ?? []))
  }, [])

  const currentTemplate = useMemo(() => templates.find((t) => t.template_id === params.template_id), [templates, params.template_id])

  const applyTemplateDefaults = () => {
    const d = currentTemplate?.default_parameters ?? {}
    setParams((p) => ({ ...p, ...d, template_defaults_applied: true } as PreviewParams))
  }

  const generatePreview = async () => {
    setFormError('')
    const previewCount = validateAndClampNumber(previewCountInput, { label: '预览数量', min: 3, max: 6, integer: true })
    const seed = validateAndClampNumber(seedInput, { label: '随机种子', integer: true })
    const numCurves = validateAndClampNumber(numCurvesInput, { label: '曲线数量', min: 1, max: 5, integer: true })
    const pointsPerCurve = validateAndClampNumber(pointsPerCurveInput, { label: '每条曲线采样点数', min: 50, max: 500, integer: true })
    const noiseLevel = validateAndClampNumber(noiseLevelInput, { label: '噪声强度', min: 0, max: 0.1 })
    const lineWidth = validateAndClampNumber(lineWidthInput, { label: '线宽', min: 0.5, max: 4 })
    const xMin = validateAndClampNumber(xMinInput, { label: 'X轴最小值' })
    const xMax = validateAndClampNumber(xMaxInput, { label: 'X轴最大值' })
    if ([previewCount, seed, numCurves, pointsPerCurve, noiseLevel, lineWidth, xMin, xMax].some((v) => v === null)) return
    if ((xMin as number) >= (xMax as number)) {
      setFormError('X轴最小值必须小于X轴最大值')
      return
    }
    const safeParams: PreviewParams = { ...params, preview_count: previewCount as number, seed: seed as number, num_curves: numCurves as number, points_per_curve: pointsPerCurve as number, noise_level: noiseLevel as number, line_width: lineWidth as number, x_range: [xMin as number, xMax as number] as [number, number] }
    setParams(safeParams)
    setRequestSnapshot(safeParams)
    const res = await fetch('http://127.0.0.1:8000/preview', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(safeParams) })
    const data = await res.json()
    setItems(data.items ?? [])
    setActualSnapshot(data.items?.[0]?.annotation?.style?.actual_parameters ?? null)
    setExpandedJson({})
  }

  const generateDataset = async () => {
    setFormError('')
    const totalCount = validateAndClampNumber(totalCountInput, { label: '样本总数', min: 1, integer: true })
    const train = validateAndClampNumber(splitTrainInput, { label: '训练集比例', min: 0, max: 1 })
    const val = validateAndClampNumber(splitValInput, { label: '验证集比例', min: 0, max: 1 })
    const test = validateAndClampNumber(splitTestInput, { label: '测试集比例', min: 0, max: 1 })
    if ([totalCount, train, val, test].some((v) => v === null)) return
    if (Math.abs((train as number) + (val as number) + (test as number) - 1) > 1e-6) return setFormError('训练/验证/测试比例之和必须等于 1.0')

    const safeGenerateParams: GenerateParams = { ...generateParams, total_count: totalCount as number, split: { train: train as number, val: val as number, test: test as number } }
    setGenerateParams(safeGenerateParams)
    const payload = { ...params, ...safeGenerateParams }
    setRequestSnapshot(payload)
    const res = await fetch('http://127.0.0.1:8000/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    setGenerateResult(await res.json())
  }

  return (
    <main className="app-container">
      <header className="page-header">
        <h1>材料科学曲线数据集生成平台</h1>
        <p>面向 SRTP 中期演示的钢蠕变曲线合成与标注预览界面（V0 + P1 UI）。</p>
      </header>

      <section className="card">
        <h2>模板与模式</h2>
        <div className="grid-2">
          <label>模板<select value={params.template_id} onChange={(e) => setParams({ ...params, template_id: e.target.value })}>{templates.map((t) => <option key={t.template_id} value={t.template_id}>{getTemplateDisplayName(t)}</option>)}</select></label>
          <label>生成模式<select value={params.mode} onChange={(e) => setParams({ ...params, mode: e.target.value as PreviewParams['mode'] })}><option value="explicit">显式模式</option><option value="probabilistic">概率采样模式</option></select></label>
        </div>
        <div className="action-row"><button className="btn-secondary" onClick={applyTemplateDefaults}>应用模板默认参数</button></div>
        <p className="muted">模板说明：{currentTemplate?.description ?? '暂无说明'}</p>
        <p className="muted">模板特性：{(currentTemplate?.key_effects ?? []).join('；') || '暂无'}</p>
        <div className="mode-note">显式模式：手动参数优先，模板只补充默认值。<br/>概率采样模式：模板中的概率分布会接管部分字段，适合批量生成风格多样的数据集。</div>
        {params.mode === 'probabilistic' && <div className="warn-card">当前为概率采样模式，{probOverriddenLabel}等字段可能由模板采样决定，手动输入不一定完全生效。</div>}
      </section>

      <section className="card">
        {formError && <p className="error-text">{formError}</p>}
        <h2>预览参数</h2>
        <div className="grid-2">
          <label>预览数量<input type="number" min={3} max={6} value={previewCountInput} onChange={(e) => setPreviewCountInput(e.target.value)} /></label>
          <label>随机种子<input type="number" value={seedInput} onChange={(e) => setSeedInput(e.target.value)} /></label>
        </div>
        <h3>曲线参数</h3><div className="grid-2">
          <label>曲线数量<input type="number" min={1} max={5} value={numCurvesInput} onChange={(e) => setNumCurvesInput(e.target.value)} /></label>
          <label>曲线形态<select value={params.curve_shape} onChange={(e) => setParams({ ...params, curve_shape: e.target.value })}>{curveShapeOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></label>
          <label>每条曲线采样点数<input type="number" min={50} max={500} value={pointsPerCurveInput} onChange={(e) => setPointsPerCurveInput(e.target.value)} /></label>
          <label>噪声强度<input type="number" min={0} max={0.1} step={0.001} value={noiseLevelInput} onChange={(e) => setNoiseLevelInput(e.target.value)} /></label>
        </div>
        <h3>样式参数</h3><div className="grid-2">
          <label>线型<select value={params.line_style} onChange={(e) => setParams({ ...params, line_style: e.target.value })}>{lineStyleOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></label>
          <label>线宽<input type="number" min={0.5} max={4} step={0.1} value={lineWidthInput} onChange={(e) => setLineWidthInput(e.target.value)} /></label>
          <label>标记点<select value={params.marker} onChange={(e) => setParams({ ...params, marker: e.target.value })}>{markerOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></label>
          <label>图例位置<select value={params.legend_position} onChange={(e) => setParams({ ...params, legend_position: e.target.value })}>{legendOptions.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></label>
          <label className="checkbox-label"><input type="checkbox" checked={params.grid} onChange={(e) => setParams({ ...params, grid: e.target.checked })} />显示网格</label>
        </div>
        <h3>坐标轴参数</h3><div className="grid-2">
          <label>X轴名称<input value={params.x_label} onChange={(e) => setParams({ ...params, x_label: e.target.value })} /></label>
          <label>X轴单位<input value={params.x_unit} onChange={(e) => setParams({ ...params, x_unit: e.target.value })} /></label>
          <label>Y轴名称<input value={params.y_label} onChange={(e) => setParams({ ...params, y_label: e.target.value })} /></label>
          <label>Y轴单位<input value={params.y_unit} onChange={(e) => setParams({ ...params, y_unit: e.target.value })} /></label>
          <label>X轴最小值<input type="number" value={xMinInput} onChange={(e) => setXMinInput(e.target.value)} /></label>
          <label>X轴最大值<input type="number" value={xMaxInput} onChange={(e) => setXMaxInput(e.target.value)} /></label>
        </div>
        <div className="action-row"><button className="btn-primary" onClick={generatePreview}>生成预览图</button></div>
      </section>

      <section className="card">
        <h2>数据集生成</h2>
        <p className="muted">dataset_name 为数据集名称；dataset_id 将由后端自动生成。</p>
        <div className="grid-2">
          <label>数据集名称<input value={generateParams.dataset_name} onChange={(e) => setGenerateParams({ ...generateParams, dataset_name: e.target.value })} /></label>
          <label>数据集版本<input value={generateParams.version} onChange={(e) => setGenerateParams({ ...generateParams, version: e.target.value })} /></label>
          <label>样本总数<input type="number" min={1} value={totalCountInput} onChange={(e) => setTotalCountInput(e.target.value)} /></label>
          <label>训练集比例<input type="number" step={0.1} value={splitTrainInput} onChange={(e) => setSplitTrainInput(e.target.value)} /></label>
          <label>验证集比例<input type="number" step={0.1} value={splitValInput} onChange={(e) => setSplitValInput(e.target.value)} /></label>
          <label>测试集比例<input type="number" step={0.1} value={splitTestInput} onChange={(e) => setSplitTestInput(e.target.value)} /></label>
        </div>
        <div className="action-row"><button className="btn-primary" onClick={generateDataset}>生成数据集</button></div>
        {generateResult && <p className="success-card">dataset_id: {String(generateResult.dataset_id ?? '-')} ｜ dataset_path: {String(generateResult.dataset_path ?? '-')} ｜ split_counts: {JSON.stringify(generateResult.split_counts ?? {})}</p>}
        <details><summary>生成结果</summary><pre>{JSON.stringify(generateResult ?? {}, null, 2)}</pre></details>
      </section>

      <details className="card"><summary>本次请求参数</summary><pre>{JSON.stringify(requestSnapshot ?? params, null, 2)}</pre></details>
      <details className="card"><summary>当前实际生效参数</summary><pre>{JSON.stringify(actualSnapshot ?? {}, null, 2)}</pre></details>

      <section className="preview-grid">
        {items.map((it, idx) => {
          const ann = it.annotation
          const style = (ann.style ?? {}) as Record<string, unknown>
          const ds = (ann.dataset_info ?? {}) as Record<string, unknown>
          const actual = (style.actual_parameters ?? {}) as Record<string, unknown>
          return (
            <article className="preview-card" key={idx}>
              <img src={`http://127.0.0.1:8000/${it.image_path}`} alt={`preview-${idx}`} />
              <p>模板：{String(ds.template_name ?? '-')} ｜ 模式：{String(ds.mode ?? '-')} ｜ 曲线条数：{String(actual.num_curves ?? '-')} ｜ 曲线形态：{enumLabel(curveShapeOptions, actual.curve_shape)} ｜ 线型：{enumLabel(lineStyleOptions, actual.line_style)} ｜ 标记点：{enumLabel(markerOptions, actual.marker)} ｜ 网格：{String(actual.grid ?? '-')} ｜ 图例位置：{enumLabel(legendOptions, actual.legend_position)}</p>
              <p>图片：{it.image_path.split('/').slice(-2).join('/')}；标注：{it.annotation_path.split('/').slice(-2).join('/')}；CSV数：{it.csv_paths.length}</p>
              <div className="action-row"><button className="btn-secondary" onClick={() => setExpandedJson((p) => ({ ...p, [idx]: !p[idx] }))}>{expandedJson[idx] ? '隐藏 MCG-JSON' : '查看完整 MCG-JSON'}</button><button className="btn-secondary" onClick={() => navigator.clipboard.writeText(JSON.stringify(ann, null, 2))}>复制 MCG-JSON</button></div>
              {expandedJson[idx] && <pre>{JSON.stringify(ann, null, 2)}</pre>}
            </article>
          )
        })}
      </section>
    </main>
  )
}
