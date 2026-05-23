import { useEffect, useMemo, useState } from 'react'

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

const probOverridden = ['num_curves', 'curve_shape', 'line_style', 'marker', 'legend_position', 'grid']

export default function App() {
  const [items, setItems] = useState<PreviewItem[]>([])
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [params, setParams] = useState<PreviewParams>(defaults)
  const [generateParams, setGenerateParams] = useState<GenerateParams>(generateDefaults)
  const [requestSnapshot, setRequestSnapshot] = useState<Record<string, unknown> | null>(null)
  const [actualSnapshot, setActualSnapshot] = useState<Record<string, unknown> | null>(null)
  const [expandedJson, setExpandedJson] = useState<Record<number, boolean>>({})
  const [generateResult, setGenerateResult] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/templates').then((r) => r.json()).then((d) => setTemplates(d.items ?? []))
  }, [])

  const currentTemplate = useMemo(() => templates.find((t) => t.template_id === params.template_id), [templates, params.template_id])

  const applyTemplateDefaults = () => {
    const d = currentTemplate?.default_parameters ?? {}
    setParams((p) => ({ ...p, ...d, template_defaults_applied: true } as PreviewParams))
  }

  const generatePreview = async () => {
    const payload = { ...params }
    setRequestSnapshot(payload)
    const res = await fetch('http://127.0.0.1:8000/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    setItems(data.items ?? [])
    const first = data.items?.[0]?.annotation?.style?.actual_parameters
    setActualSnapshot(first ?? null)
    setExpandedJson({})
  }

  const generateDataset = async () => {
    const payload = {
      ...params,
      ...generateParams,
    }
    setRequestSnapshot(payload)
    const res = await fetch('http://127.0.0.1:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    setGenerateResult(data)
  }

  const copyJson = async (a: Record<string, unknown>) => navigator.clipboard.writeText(JSON.stringify(a, null, 2))

  return (
    <main style={{ padding: 16, maxWidth: 1080, margin: '0 auto' }}>
      <h1>Materials Curve Dataset Platform</h1>

      <section>
        <h2>模板与模式</h2>
        <label>
          模板
          <select value={params.template_id} onChange={(e) => setParams({ ...params, template_id: e.target.value })}>
            {templates.map((t) => (
              <option key={t.template_id} value={t.template_id}>
                {t.template_name}
              </option>
            ))}
          </select>
        </label>
        <button onClick={applyTemplateDefaults}>应用模板默认参数</button>
        <label>
          模式
          <select value={params.mode} onChange={(e) => setParams({ ...params, mode: e.target.value as PreviewParams['mode'] })}>
            <option value="explicit">explicit</option>
            <option value="probabilistic">probabilistic</option>
          </select>
        </label>
        <p>{currentTemplate?.description}</p>
        <p>{(currentTemplate?.key_effects ?? []).join('；')}</p>
        <p>
          {params.mode === 'probabilistic'
            ? `当前为概率采样模式，以下字段会被模板概率分布接管：${probOverridden.join('、')}。`
            : '当前为显式指定模式，手动参数优先，模板只补默认值。'}
        </p>
      </section>

      <section>
        <h2>预览参数</h2>
        <label>preview_count<input type="number" min={3} max={6} value={params.preview_count} onChange={(e) => setParams({ ...params, preview_count: Number(e.target.value) })} /></label>
        <label>seed<input type="number" value={params.seed} onChange={(e) => setParams({ ...params, seed: Number(e.target.value) })} /></label>

        <h3>曲线参数</h3>
        <label>num_curves<input type="number" min={1} max={5} value={params.num_curves} onChange={(e) => setParams({ ...params, num_curves: Number(e.target.value) })} /></label>
        <label>
          curve_shape
          <select value={params.curve_shape} onChange={(e) => setParams({ ...params, curve_shape: e.target.value })}>
            <option value="near_linear">near_linear</option>
            <option value="primary_obvious">primary_obvious</option>
            <option value="accelerated_obvious">accelerated_obvious</option>
            <option value="three_stage">three_stage</option>
            <option value="irregular">irregular</option>
          </select>
        </label>
        <label>points_per_curve<input type="number" min={50} max={500} value={params.points_per_curve} onChange={(e) => setParams({ ...params, points_per_curve: Number(e.target.value) })} /></label>
        <label>noise_level<input type="number" min={0} max={0.1} step={0.001} value={params.noise_level} onChange={(e) => setParams({ ...params, noise_level: Number(e.target.value) })} /></label>

        <h3>样式参数</h3>
        <label>line_style<input value={params.line_style} onChange={(e) => setParams({ ...params, line_style: e.target.value })} /></label>
        <label>line_width<input type="number" min={0.5} max={4} step={0.1} value={params.line_width} onChange={(e) => setParams({ ...params, line_width: Number(e.target.value) })} /></label>
        <label>marker<input value={params.marker} onChange={(e) => setParams({ ...params, marker: e.target.value })} /></label>
        <label>legend_position<input value={params.legend_position} onChange={(e) => setParams({ ...params, legend_position: e.target.value })} /></label>
        <label>grid<input type="checkbox" checked={params.grid} onChange={(e) => setParams({ ...params, grid: e.target.checked })} /></label>

        <h3>坐标轴参数</h3>
        <label>x_label<input value={params.x_label} onChange={(e) => setParams({ ...params, x_label: e.target.value })} /></label>
        <label>x_unit<input value={params.x_unit} onChange={(e) => setParams({ ...params, x_unit: e.target.value })} /></label>
        <label>y_label<input value={params.y_label} onChange={(e) => setParams({ ...params, y_label: e.target.value })} /></label>
        <label>y_unit<input value={params.y_unit} onChange={(e) => setParams({ ...params, y_unit: e.target.value })} /></label>
        <label>x_min<input type="number" value={params.x_range[0]} onChange={(e) => setParams({ ...params, x_range: [Number(e.target.value), params.x_range[1]] })} /></label>
        <label>x_max<input type="number" value={params.x_range[1]} onChange={(e) => setParams({ ...params, x_range: [params.x_range[0], Number(e.target.value)] })} /></label>
        <div><button onClick={generatePreview}>生成预览图</button></div>
      </section>

      <section>
        <h2>数据集生成（/generate）</h2>
        <label>dataset_name<input value={generateParams.dataset_name} onChange={(e) => setGenerateParams({ ...generateParams, dataset_name: e.target.value })} /></label>
        <label>version<input value={generateParams.version} onChange={(e) => setGenerateParams({ ...generateParams, version: e.target.value })} /></label>
        <label>total_count<input type="number" min={1} value={generateParams.total_count} onChange={(e) => setGenerateParams({ ...generateParams, total_count: Number(e.target.value) })} /></label>
        <label>split.train<input type="number" step={0.1} value={generateParams.split.train} onChange={(e) => setGenerateParams({ ...generateParams, split: { ...generateParams.split, train: Number(e.target.value) } })} /></label>
        <label>split.val<input type="number" step={0.1} value={generateParams.split.val} onChange={(e) => setGenerateParams({ ...generateParams, split: { ...generateParams.split, val: Number(e.target.value) } })} /></label>
        <label>split.test<input type="number" step={0.1} value={generateParams.split.test} onChange={(e) => setGenerateParams({ ...generateParams, split: { ...generateParams.split, test: Number(e.target.value) } })} /></label>
        <div><button onClick={generateDataset}>生成数据集</button></div>
        <details><summary>生成结果</summary><pre>{JSON.stringify(generateResult ?? {}, null, 2)}</pre></details>
      </section>

      <details><summary>本次请求参数</summary><pre>{JSON.stringify(requestSnapshot ?? params, null, 2)}</pre></details>
      <details><summary>当前实际生效参数</summary><pre>{JSON.stringify(actualSnapshot ?? {}, null, 2)}</pre></details>

      {items.map((it, idx) => {
        const ann = it.annotation
        const style = (ann.style ?? {}) as Record<string, unknown>
        const ds = (ann.dataset_info ?? {}) as Record<string, unknown>
        const actual = (style.actual_parameters ?? {}) as Record<string, unknown>
        return (
          <article key={idx}>
            <img src={`http://127.0.0.1:8000/${it.image_path}`} />
            <p>模板：{String(ds.template_name ?? '-')} | 模式：{String(ds.mode ?? '-')} | 曲线条数：{String(actual.num_curves ?? '-')} | 曲线形态：{String(actual.curve_shape ?? '-')} | 线型：{String(actual.line_style ?? '-')} | 标记点：{String(actual.marker ?? '-')} | 网格：{String(actual.grid ?? '-')} | 图例位置：{String(actual.legend_position ?? '-')}</p>
            <p>图片：{it.image_path.split('/').slice(-2).join('/')}，标注：{it.annotation_path.split('/').slice(-2).join('/')}，CSV数：{it.csv_paths.length}</p>
            <button onClick={() => setExpandedJson((p) => ({ ...p, [idx]: !p[idx] }))}>{expandedJson[idx] ? '隐藏 MCG-JSON' : '查看完整 MCG-JSON'}</button>
            <button onClick={() => copyJson(ann)}>复制 MCG-JSON</button>
            {expandedJson[idx] && <pre style={{ maxHeight: 300, overflow: 'auto' }}>{JSON.stringify(ann, null, 2)}</pre>}
          </article>
        )
      })}
    </main>
  )
}
