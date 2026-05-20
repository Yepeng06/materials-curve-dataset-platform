import { useEffect, useState } from 'react'

type PreviewItem = {
  image_path: string
  annotation_path: string
  csv_paths: string[]
  annotation: Record<string, unknown>
}

type TemplateItem = {
  template_id: string
  template_name: string
  description: string
  file_name: string
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

type GenerateResult = {
  dataset_id: string
  dataset_path: string
  total_count: number
  split_counts: Record<string, number>
  summary_path: string
  quality_report_path: string
}

const defaults: PreviewParams = {
  mode: 'explicit', template_id: 'real_mainstream', preview_count: 3, seed: 20260520, grid: false,
  x_label: 'Creep time', x_unit: 'h', y_label: 'Creep strain', y_unit: '%', num_curves: 3, curve_shape: 'near_linear',
  points_per_curve: 160, noise_level: 0.02, line_style: 'solid', line_width: 1.5, marker: 'none', legend_position: 'inside_upper_right',
}

function App() {
  const [items, setItems] = useState<PreviewItem[]>([])
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [params, setParams] = useState<PreviewParams>(defaults)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [generateLoading, setGenerateLoading] = useState(false)
  const [generateError, setGenerateError] = useState('')
  const [generateResult, setGenerateResult] = useState<GenerateResult | null>(null)
  const [datasetName, setDatasetName] = useState('creep_synth')
  const [version, setVersion] = useState('v0.1')
  const [totalCount, setTotalCount] = useState(30)
  const [trainRatio, setTrainRatio] = useState(0.7)
  const [valRatio, setValRatio] = useState(0.2)
  const [testRatio, setTestRatio] = useState(0.1)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/templates').then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json(); setTemplates(data.items ?? [])
    }).catch((e) => setError(`模板列表加载失败: ${(e as Error).message}`))
  }, [])

  const generatePreview = async () => {
    setLoading(true); setError('')
    try {
      const res = await fetch('http://127.0.0.1:8000/preview', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json(); setItems(data.items ?? [])
    } catch (e) { setError(`预览生成失败: ${(e as Error).message}`) } finally { setLoading(false) }
  }

  const generateDataset = async () => {
    setGenerateLoading(true); setGenerateError(''); setGenerateResult(null)
    try {
      const payload = { ...params, dataset_name: datasetName, version, total_count: totalCount, split: { train: trainRatio, val: valRatio, test: testRatio } }
      const res = await fetch('http://127.0.0.1:8000/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json(); setGenerateResult(data)
    } catch (e) { setGenerateError(`批量生成失败: ${(e as Error).message}`) } finally { setGenerateLoading(false) }
  }

  return (<main style={{ margin: '2rem auto', maxWidth: 1100, fontFamily: 'Arial, sans-serif', lineHeight: 1.6 }}>
    <h1>Materials Curve Dataset Platform</h1><p>V0 第五步：批量生成与数据集版本目录。</p>
    <section style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}><h2>参数面板</h2>
      <h3>0. 模板与生成模式</h3>
      <label>template: <select value={params.template_id} onChange={(e) => setParams({ ...params, template_id: e.target.value })}>{templates.map((t) => <option key={t.template_id} value={t.template_id}>{t.template_name}</option>)}</select></label>{' '}
      <label>mode: <select value={params.mode} onChange={(e) => setParams({ ...params, mode: e.target.value as 'explicit' | 'probabilistic' })}><option value="explicit">explicit</option><option value="probabilistic">probabilistic</option></select></label>
      <h3>A. 图像与预览设置</h3>
      <label>preview_count (3-6): <input type="number" min={3} max={6} value={params.preview_count} onChange={(e) => setParams({ ...params, preview_count: Number(e.target.value) })} /></label>{' '}
      <label>seed: <input type="number" value={params.seed} onChange={(e) => setParams({ ...params, seed: Number(e.target.value) })} /></label>{' '}
      <label>grid: <input type="checkbox" checked={params.grid} onChange={(e) => setParams({ ...params, grid: e.target.checked })} /></label>
    </section>

    <button onClick={generatePreview} disabled={loading} style={{ marginTop: 16 }}>{loading ? '生成中...' : '生成预览图'}</button>
    {error && <p style={{ color: 'crimson' }}>{error}</p>}

    <section style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16, marginTop: 20 }}>
      <h2>批量生成数据集</h2>
      <label>dataset_name: <input value={datasetName} onChange={(e) => setDatasetName(e.target.value)} /></label>{' '}
      <label>version: <input value={version} onChange={(e) => setVersion(e.target.value)} /></label>{' '}
      <label>total_count: <input type="number" min={1} value={totalCount} onChange={(e) => setTotalCount(Number(e.target.value))} /></label>{' '}
      <label>train ratio: <input type="number" step={0.1} value={trainRatio} onChange={(e) => setTrainRatio(Number(e.target.value))} /></label>{' '}
      <label>val ratio: <input type="number" step={0.1} value={valRatio} onChange={(e) => setValRatio(Number(e.target.value))} /></label>{' '}
      <label>test ratio: <input type="number" step={0.1} value={testRatio} onChange={(e) => setTestRatio(Number(e.target.value))} /></label>{' '}
      <div><button onClick={generateDataset} disabled={generateLoading} style={{ marginTop: 12 }}>{generateLoading ? '批量生成中...' : '批量生成数据集'}</button></div>
      {generateError && <p style={{ color: 'crimson' }}>{generateError}</p>}
      {generateResult && <pre style={{ background: '#f8f8f8', padding: 10 }}>{JSON.stringify(generateResult, null, 2)}</pre>}
    </section>

    <section style={{ marginTop: '1.5rem' }}>{items.map((item, idx) => <article key={idx} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, marginBottom: 20 }}><h3>预览图 {idx + 1}</h3><img src={`http://127.0.0.1:8000/${item.image_path}`} alt={`preview-${idx + 1}`} style={{ maxWidth: '100%' }} /><p><strong>image_path:</strong> {item.image_path}</p><p><strong>annotation_path:</strong> {item.annotation_path}</p><p><strong>csv_paths:</strong> {item.csv_paths.join(', ')}</p><details><summary>查看 MCG-JSON</summary><pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: 10 }}>{JSON.stringify(item.annotation, null, 2)}</pre></details></article>)}</section>
  </main>)
}

export default App
