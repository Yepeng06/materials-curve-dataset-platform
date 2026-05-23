import { useEffect, useMemo, useState } from 'react'

type PreviewItem = {
  image_path: string
  annotation_path: string
  csv_paths: string[]
  annotation: Record<string, unknown>
}

type TemplateItem = {
  template_id: string
  template_name: string
}

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
  num_curves: number
  curve_shape: string
  points_per_curve: number
  noise_level: number
  line_style: string
  line_width: number
  marker: string
  legend_position: string
}

const defaults: PreviewParams = {
  mode: 'explicit', template_id: 'real_mainstream', preview_count: 3, seed: 20260520, grid: false,
  x_label: 'Creep time', x_unit: 'h', y_label: 'Creep strain', y_unit: '%', num_curves: 3, curve_shape: 'near_linear',
  points_per_curve: 160, noise_level: 0.02, line_style: 'solid', line_width: 1.5, marker: 'none', legend_position: 'inside_upper_right',
}

const labelMap: Record<string, string> = {
  real_mainstream: '真实主流风格', multi_curve_comparison: '多曲线对比风格', black_white_paper: '黑白论文风格',
  marker_rich: '标记点丰富风格', grid_interference: '网格干扰风格', low_quality_screenshot: '低质量截图风格',
  three_stage_creep: '完整三阶段蠕变风格',
}

function App() {
  const [items, setItems] = useState<PreviewItem[]>([])
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [params, setParams] = useState<PreviewParams>(defaults)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [requestSnapshot, setRequestSnapshot] = useState<PreviewParams | null>(null)
  const [cacheBuster, setCacheBuster] = useState('')

  const [datasetName, setDatasetName] = useState('creep_synth')
  const [version, setVersion] = useState('v0.1')
  const [totalCount, setTotalCount] = useState(30)
  const [trainRatio, setTrainRatio] = useState(0.7)
  const [valRatio, setValRatio] = useState(0.2)
  const [testRatio, setTestRatio] = useState(0.1)
  const [generateLoading, setGenerateLoading] = useState(false)
  const [generateError, setGenerateError] = useState('')
  const [generateResult, setGenerateResult] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/templates').then(async (res) => {
      const data = await res.json(); setTemplates(data.items ?? [])
    }).catch((e) => setError(`模板列表加载失败: ${(e as Error).message}`))
  }, [])

  const templateOptions = useMemo(() => templates.map((t) => ({ value: t.template_id, label: labelMap[t.template_id] ?? t.template_name })), [templates])

  const generatePreview = async () => {
    const payload: PreviewParams = { ...params }
    setRequestSnapshot(payload)
    setLoading(true); setError(''); setItems([])
    try {
      const res = await fetch('http://127.0.0.1:8000/preview', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setItems(data.items ?? [])
      setCacheBuster(data.preview_run_id ?? `${Date.now()}`)
    } catch (e) { setError(`预览生成失败: ${(e as Error).message}`) } finally { setLoading(false) }
  }

  const generateDataset = async () => {
    setGenerateLoading(true); setGenerateError(''); setGenerateResult(null)
    try {
      const payload = { ...params, dataset_name: datasetName, version, total_count: totalCount, split: { train: trainRatio, val: valRatio, test: testRatio } }
      const res = await fetch('http://127.0.0.1:8000/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      const data = await res.json(); if (!res.ok) throw new Error(data.detail ?? `HTTP ${res.status}`)
      setGenerateResult(data)
    } catch (e) { setGenerateError(`批量生成失败: ${(e as Error).message}`) } finally { setGenerateLoading(false) }
  }

  const cardStyle = { border: '1px solid #ddd', borderRadius: 10, padding: 16, background: '#fff', marginBottom: 16 }
  const inputStyle = { width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #ccc', boxSizing: 'border-box' as const }
  const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(210px,1fr))', gap: 12 }

  return <main style={{ margin: '24px auto', maxWidth: 1180, padding: '0 12px', fontFamily: 'Arial, sans-serif', background: '#f6f8fb' }}>
    <h1>Materials Curve Dataset Platform</h1>
    <p>材料科学曲线图合成数据集生成与标注平台</p>

    <section style={cardStyle}><h2>参数配置</h2>
      <h3>1. 模板与生成模式</h3><div style={gridStyle}>
        <label>模板
          <select style={inputStyle} value={params.template_id} onChange={(e) => setParams({ ...params, template_id: e.target.value })}>{templateOptions.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}</select>
        </label>
        <label>生成模式
          <select style={inputStyle} value={params.mode} onChange={(e) => setParams({ ...params, mode: e.target.value as 'explicit' | 'probabilistic' })}><option value="explicit">显式指定模式</option><option value="probabilistic">概率采样模式</option></select>
        </label></div>
      {params.mode === 'probabilistic' && <p style={{ color: '#9b6a00' }}>当前将根据模板概率分布采样，部分手动参数可能不生效。</p>}

      <h3>2. 图像与预览设置</h3><div style={gridStyle}>
        <label>预览数量 (3-6)<input style={inputStyle} type="number" min={3} max={6} value={params.preview_count} onChange={(e) => setParams({ ...params, preview_count: Number(e.target.value) })} /></label>
        <label>随机种子<input style={inputStyle} type="number" value={params.seed} onChange={(e) => setParams({ ...params, seed: Number(e.target.value) })} /></label>
        <label>显示网格<select style={inputStyle} value={String(params.grid)} onChange={(e) => setParams({ ...params, grid: e.target.value === 'true' })}><option value="false">否</option><option value="true">是</option></select></label></div>

      <h3>3. 坐标轴设置</h3><div style={gridStyle}>
        <label>横轴含义<input list="x_label_options" style={inputStyle} value={params.x_label} onChange={(e) => setParams({ ...params, x_label: e.target.value })} /></label>
        <label>横轴单位<input list="x_unit_options" style={inputStyle} value={params.x_unit} onChange={(e) => setParams({ ...params, x_unit: e.target.value })} /></label>
        <label>纵轴含义<input list="y_label_options" style={inputStyle} value={params.y_label} onChange={(e) => setParams({ ...params, y_label: e.target.value })} /></label>
        <label>纵轴单位<input list="y_unit_options" style={inputStyle} value={params.y_unit} onChange={(e) => setParams({ ...params, y_unit: e.target.value })} /></label></div>

      <h3>4. 曲线设置</h3><div style={gridStyle}>
        <label>曲线条数(1-4)<input style={inputStyle} type="number" min={1} max={4} value={params.num_curves} onChange={(e) => setParams({ ...params, num_curves: Number(e.target.value) })} /></label>
        <label>曲线形态<select style={inputStyle} value={params.curve_shape} onChange={(e) => setParams({ ...params, curve_shape: e.target.value })}><option value="near_linear">近似线性</option><option value="primary_obvious">初期蠕变明显</option><option value="accelerated_obvious">加速段明显</option></select></label>
        <label>采样点数(50-500)<input style={inputStyle} type="number" min={50} max={500} value={params.points_per_curve} onChange={(e) => setParams({ ...params, points_per_curve: Number(e.target.value) })} /></label>
        <label>噪声强度(0-0.1)<input style={inputStyle} type="number" min={0} max={0.1} step={0.005} value={params.noise_level} onChange={(e) => setParams({ ...params, noise_level: Number(e.target.value) })} /></label></div>

      <h3>5. 曲线视觉风格</h3><div style={gridStyle}>
        <label>线型<select style={inputStyle} value={params.line_style} onChange={(e) => setParams({ ...params, line_style: e.target.value })}><option value="solid">实线</option><option value="dashed">虚线</option><option value="dotted">点线</option><option value="dashdot">点划线</option></select></label>
        <label>线宽(0.5-4)<input style={inputStyle} type="number" min={0.5} max={4} step={0.1} value={params.line_width} onChange={(e) => setParams({ ...params, line_width: Number(e.target.value) })} /></label>
        <label>标记点<select style={inputStyle} value={params.marker} onChange={(e) => setParams({ ...params, marker: e.target.value })}><option value="none">无标记点</option><option value="circle">圆点</option><option value="triangle">三角形</option><option value="square">方形</option></select></label></div>

      <h3>6. 图例设置</h3><div style={gridStyle}><label>图例位置<select style={inputStyle} value={params.legend_position} onChange={(e) => setParams({ ...params, legend_position: e.target.value })}><option value="none">无图例</option><option value="inside_upper_right">图内右上</option><option value="inside_upper_left">图内左上</option><option value="inside_lower_right">图内右下</option><option value="outside_right">图外右侧</option></select></label></div>
      <button onClick={generatePreview} disabled={loading} style={{ marginTop: 12, padding: '10px 18px' }}>{loading ? '生成中...' : '生成预览图'}</button>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      <details><summary>本次请求参数</summary><pre>{JSON.stringify(requestSnapshot ?? params, null, 2)}</pre></details>
    </section>

    <section style={cardStyle}><h2>批量生成数据集</h2><div style={gridStyle}>
      <label>数据集名称<input style={inputStyle} value={datasetName} onChange={(e) => setDatasetName(e.target.value)} /></label>
      <label>版本<input style={inputStyle} value={version} onChange={(e) => setVersion(e.target.value)} /></label>
      <label>数量<input style={inputStyle} type="number" min={1} value={totalCount} onChange={(e) => setTotalCount(Number(e.target.value))} /></label>
      <label>train<input style={inputStyle} type="number" step={0.1} value={trainRatio} onChange={(e) => setTrainRatio(Number(e.target.value))} /></label>
      <label>val<input style={inputStyle} type="number" step={0.1} value={valRatio} onChange={(e) => setValRatio(Number(e.target.value))} /></label>
      <label>test<input style={inputStyle} type="number" step={0.1} value={testRatio} onChange={(e) => setTestRatio(Number(e.target.value))} /></label></div>
      <button onClick={generateDataset} disabled={generateLoading} style={{ marginTop: 12, padding: '10px 18px' }}>{generateLoading ? '批量生成中...' : '批量生成数据集'}</button>
      {generateError && <p style={{ color: 'crimson' }}>{generateError}</p>}
      {generateResult && <pre>{JSON.stringify(generateResult, null, 2)}</pre>}
    </section>

    <section style={cardStyle}><h2>预览结果</h2>{items.map((item, idx) => <article key={`${item.image_path}_${idx}`} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, marginBottom: 18, textAlign: 'center' }}>
      <h3>预览图 {idx + 1}</h3><img src={`http://127.0.0.1:8000/${item.image_path}?run=${cacheBuster}`} alt={`preview-${idx + 1}`} style={{ maxWidth: '100%', margin: '0 auto' }} />
      <p><strong>image_path:</strong> {item.image_path}</p><details><summary>查看 MCG-JSON</summary><pre style={{ textAlign: 'left', whiteSpace: 'pre-wrap' }}>{JSON.stringify(item.annotation, null, 2)}</pre></details></article>)}</section>

    <datalist id="x_label_options"><option value="Time" /><option value="Creep time" /><option value="Duration time" /><option value="t" /></datalist>
    <datalist id="x_unit_options"><option value="h" /><option value="hr" /><option value="hour" /><option value="day" /><option value="min" /><option value="s" /><option value="none" /></datalist>
    <datalist id="y_label_options"><option value="Strain" /><option value="Creep strain" /><option value="Residual strain" /><option value="ε" /></datalist>
    <datalist id="y_unit_options"><option value="%" /><option value="strain" /><option value="microstrain" /><option value="none" /></datalist>
  </main>
}

export default App
