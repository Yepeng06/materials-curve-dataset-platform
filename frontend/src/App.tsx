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
  num_curves: 3,
  curve_shape: 'near_linear',
  points_per_curve: 160,
  noise_level: 0.02,
  line_style: 'solid',
  line_width: 1.5,
  marker: 'none',
  legend_position: 'inside_upper_right',
}

function App() {
  const [items, setItems] = useState<PreviewItem[]>([])
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [params, setParams] = useState<PreviewParams>(defaults)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/templates')
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setTemplates(data.items ?? [])
      })
      .catch((e) => setError(`模板列表加载失败: ${(e as Error).message}`))
  }, [])

  const generatePreview = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://127.0.0.1:8000/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setItems(data.items ?? [])
    } catch (e) {
      setError(`预览生成失败: ${(e as Error).message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ margin: '2rem auto', maxWidth: 1100, fontFamily: 'Arial, sans-serif', lineHeight: 1.6 }}>
      <h1>Materials Curve Dataset Platform</h1>
      <p>V0 第四步：模板系统 + 概率采样模式。</p>

      <section style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
        <h2>参数面板</h2>
        <h3>0. 模板与生成模式</h3>
        <label>template: <select value={params.template_id} onChange={(e) => setParams({ ...params, template_id: e.target.value })}>{templates.map((t) => <option key={t.template_id} value={t.template_id}>{t.template_name}</option>)}</select></label>{' '}
        <label>mode: <select value={params.mode} onChange={(e) => setParams({ ...params, mode: e.target.value as 'explicit' | 'probabilistic' })}><option value="explicit">explicit</option><option value="probabilistic">probabilistic</option></select></label>
        {params.mode === 'probabilistic' && <p style={{ color: '#9a6700' }}>当前将根据模板概率分布采样，部分手动参数不会生效。</p>}

        <h3>A. 图像与预览设置</h3>
        <label>preview_count (3-6): <input type="number" min={3} max={6} value={params.preview_count} onChange={(e) => setParams({ ...params, preview_count: Number(e.target.value) })} /></label>{' '}
        <label>seed: <input type="number" value={params.seed} onChange={(e) => setParams({ ...params, seed: Number(e.target.value) })} /></label>{' '}
        <label>grid: <input type="checkbox" checked={params.grid} onChange={(e) => setParams({ ...params, grid: e.target.checked })} /></label>

        <h3>B. 坐标轴设置</h3>
        <label>x_label: <input value={params.x_label} onChange={(e) => setParams({ ...params, x_label: e.target.value })} /></label>{' '}
        <label>x_unit: <input value={params.x_unit} onChange={(e) => setParams({ ...params, x_unit: e.target.value })} /></label>{' '}
        <label>y_label: <input value={params.y_label} onChange={(e) => setParams({ ...params, y_label: e.target.value })} /></label>{' '}
        <label>y_unit: <input value={params.y_unit} onChange={(e) => setParams({ ...params, y_unit: e.target.value })} /></label>

        <h3>C. 曲线设置</h3>
        <label>num_curves (1-4): <input type="number" min={1} max={4} value={params.num_curves} onChange={(e) => setParams({ ...params, num_curves: Number(e.target.value) })} /></label>{' '}
        <label>curve_shape: <select value={params.curve_shape} onChange={(e) => setParams({ ...params, curve_shape: e.target.value })}><option value="near_linear">near_linear</option><option value="primary_obvious">primary_obvious</option><option value="accelerated_obvious">accelerated_obvious</option></select></label>{' '}
        <label>points_per_curve (50-500): <input type="number" min={50} max={500} value={params.points_per_curve} onChange={(e) => setParams({ ...params, points_per_curve: Number(e.target.value) })} /></label>{' '}
        <label>noise_level (0-0.1): <input type="number" min={0} max={0.1} step={0.005} value={params.noise_level} onChange={(e) => setParams({ ...params, noise_level: Number(e.target.value) })} /></label>

        <h3>D. 曲线视觉风格</h3>
        <label>line_style: <select value={params.line_style} onChange={(e) => setParams({ ...params, line_style: e.target.value })}><option value="solid">solid</option><option value="dashed">dashed</option><option value="dotted">dotted</option><option value="dashdot">dashdot</option></select></label>{' '}
        <label>line_width (0.5-4): <input type="number" min={0.5} max={4} step={0.1} value={params.line_width} onChange={(e) => setParams({ ...params, line_width: Number(e.target.value) })} /></label>{' '}
        <label>marker: <select value={params.marker} onChange={(e) => setParams({ ...params, marker: e.target.value })}><option value="none">none</option><option value="triangle">triangle</option><option value="circle">circle</option><option value="square">square</option></select></label>

        <h3>E. 图例设置</h3>
        <label>legend_position: <select value={params.legend_position} onChange={(e) => setParams({ ...params, legend_position: e.target.value })}><option value="none">none</option><option value="inside_upper_right">inside_upper_right</option><option value="inside_upper_left">inside_upper_left</option><option value="inside_lower_right">inside_lower_right</option><option value="outside_right">outside_right</option></select></label>
      </section>

      <button onClick={generatePreview} disabled={loading} style={{ marginTop: 16 }}>{loading ? '生成中...' : '生成预览图'}</button>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      <section style={{ marginTop: '1.5rem' }}>
        {items.map((item, idx) => (
          <article key={idx} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, marginBottom: 20 }}>
            <h3>预览图 {idx + 1}</h3>
            <img src={`http://127.0.0.1:8000/${item.image_path}`} alt={`preview-${idx + 1}`} style={{ maxWidth: '100%' }} />
            <p><strong>image_path:</strong> {item.image_path}</p>
            <p><strong>annotation_path:</strong> {item.annotation_path}</p>
            <p><strong>csv_paths:</strong> {item.csv_paths.join(', ')}</p>
            <details><summary>查看 MCG-JSON</summary><pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: 10 }}>{JSON.stringify(item.annotation, null, 2)}</pre></details>
          </article>
        ))}
      </section>
    </main>
  )
}

export default App
