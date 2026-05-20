import { useState } from 'react'

type PreviewItem = {
  image_path: string
  annotation_path: string
  csv_paths: string[]
  annotation: Record<string, unknown>
}

function App() {
  const [items, setItems] = useState<PreviewItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const generatePreview = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://127.0.0.1:8000/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preview_count: 3, num_curves: 3, curve_shape: 'near_linear', seed: 20260520 }),
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
    <main style={{ margin: '2rem auto', maxWidth: 1000, fontFamily: 'Arial, sans-serif', lineHeight: 1.6 }}>
      <h1>Materials Curve Dataset Platform</h1>
      <p>V0 第二步：基础曲线生成器 + /preview + MCG-JSON 预览输出。</p>
      <button onClick={generatePreview} disabled={loading}>
        {loading ? '生成中...' : '生成 3 张预览图'}
      </button>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      <section style={{ marginTop: '1.5rem' }}>
        {items.map((item, idx) => (
          <article key={idx} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, marginBottom: 20 }}>
            <h3>预览图 {idx + 1}</h3>
            <img src={`http://127.0.0.1:8000/${item.image_path}`} alt={`preview-${idx + 1}`} style={{ maxWidth: '100%' }} />
            <p><strong>图片路径:</strong> {item.image_path}</p>
            <p><strong>标注路径:</strong> {item.annotation_path}</p>
            <details>
              <summary>查看标注 JSON</summary>
              <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: 10 }}>
                {JSON.stringify(item.annotation, null, 2)}
              </pre>
            </details>
          </article>
        ))}
      </section>
    </main>
  )
}

export default App
