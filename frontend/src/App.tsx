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
      const response = await fetch('http://127.0.0.1:8000/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preview_count: 3, num_curves: 3, curve_shape: 'near_linear', seed: 20260520 }),
      })
      if (!response.ok) {
        throw new Error(`请求失败: ${response.status}`)
      }
      const data = await response.json()
      setItems(data.items ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ margin: '2rem auto', maxWidth: 1000, fontFamily: 'Arial, sans-serif', lineHeight: 1.6 }}>
      <h1>Materials Curve Dataset Platform</h1>
      <p>V0 第二步：基础曲线预览生成（PNG + CSV + MCG-JSON）。</p>
      <button onClick={generatePreview} disabled={loading}>
        {loading ? '生成中...' : '生成 3 张预览图'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <section style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
        {items.map((item, index) => (
          <article key={index} style={{ border: '1px solid #ddd', padding: '1rem', borderRadius: 8 }}>
            <h3>预览图 {index + 1}</h3>
            <img
              src={`http://127.0.0.1:8000${item.image_path}`}
              alt={`preview-${index + 1}`}
              style={{ maxWidth: '100%', border: '1px solid #eee' }}
            />
            <details style={{ marginTop: '0.75rem' }}>
              <summary>查看标注 JSON</summary>
              <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: '0.75rem', overflowX: 'auto' }}>
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
