import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const SOURCE_TYPES = [
  'support_ticket', 'prd', 'meeting_note', 'github_issue', 'interview', 'release_note'
]

export default function App() {
  const [question, setQuestion] = useState('')
  const [mode, setMode] = useState('standard')
  const [filters, setFilters] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

  const toggleFilter = (type) => {
    setFilters(prev => prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type])
  }

  const ask = async () => {
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          mode,
          source_type_filter: filters.length ? filters : null,
        }),
      })
      if (!res.ok) throw new Error(`Request failed: ${res.status}`)
      const data = await res.json()
      setResult(data)
      setHistory(prev => [{ question, answer: data.answer }, ...prev].slice(0, 10))
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Product Intelligence Analyst</h1>
        <p style={styles.subtitle}>Autonomous multi-agent RAG over support tickets, PRDs, GitHub issues, meeting notes & interviews</p>
      </header>

      <div style={styles.controlsRow}>
        <div style={styles.modeToggle}>
          <button
            style={mode === 'standard' ? styles.modeBtnActive : styles.modeBtn}
            onClick={() => setMode('standard')}
          >Standard</button>
          <button
            style={mode === 'deep_research' ? styles.modeBtnActive : styles.modeBtn}
            onClick={() => setMode('deep_research')}
          >Deep Research</button>
        </div>
        <div style={styles.filters}>
          {SOURCE_TYPES.map(t => (
            <button
              key={t}
              onClick={() => toggleFilter(t)}
              style={filters.includes(t) ? styles.filterChipActive : styles.filterChip}
            >{t.replace('_', ' ')}</button>
          ))}
        </div>
      </div>

      <div style={styles.inputRow}>
        <textarea
          style={styles.textarea}
          placeholder="e.g. What are the most common customer complaints during the last six months?"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask() } }}
        />
        <button style={styles.askBtn} onClick={ask} disabled={loading}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </div>

      {error && <div style={styles.errorBox}>{error}</div>}

      {result && (
        <div style={styles.resultGrid}>
          <div style={styles.answerCol}>
            <h3 style={styles.sectionTitle}>Answer</h3>
            <div style={styles.answerBox}>{result.answer}</div>

            <h3 style={styles.sectionTitle}>Agent Trace</h3>
            <div style={styles.traceBox}>
              {result.agent_trace.map((step, i) => (
                <div key={i} style={styles.traceStep}>
                  <span style={styles.traceAgent}>{step.agent}</span>
                  <span style={styles.traceAction}>{step.action}</span>
                  <span style={styles.traceDetail}>{step.detail}</span>
                </div>
              ))}
              <div style={styles.latency}>Total latency: {result.latency_ms} ms</div>
            </div>
          </div>

          <div style={styles.evidenceCol}>
            <h3 style={styles.sectionTitle}>Evidence ({result.evidence.length})</h3>
            {result.evidence.map(c => (
              <div key={c.chunk_id} style={styles.evidenceCard}>
                <div style={styles.evidenceMeta}>
                  <span style={styles.badge}>{c.source_type.replace('_', ' ')}</span>
                  <span style={styles.evidenceScore}>score {c.score.toFixed(2)}</span>
                </div>
                <div style={styles.evidenceTitle}>{c.title}</div>
                <div style={styles.evidenceText}>{c.text}</div>
                <div style={styles.evidenceId}>[{c.chunk_id}] {c.date}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div style={styles.historySection}>
          <h3 style={styles.sectionTitle}>Recent Questions</h3>
          {history.map((h, i) => (
            <div key={i} style={styles.historyItem} onClick={() => setQuestion(h.question)}>
              {h.question}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const styles = {
  page: { maxWidth: 1100, margin: '0 auto', padding: '32px 20px', fontFamily: 'system-ui, sans-serif', color: '#1a1a2e' },
  header: { marginBottom: 24 },
  title: { fontSize: 28, fontWeight: 700, margin: 0 },
  subtitle: { color: '#666', marginTop: 6, fontSize: 14 },
  controlsRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 },
  modeToggle: { display: 'flex', gap: 8 },
  modeBtn: { padding: '8px 16px', borderRadius: 8, border: '1px solid #ddd', background: '#fff', cursor: 'pointer', fontSize: 13 },
  modeBtnActive: { padding: '8px 16px', borderRadius: 8, border: '1px solid #4f46e5', background: '#4f46e5', color: '#fff', cursor: 'pointer', fontSize: 13 },
  filters: { display: 'flex', gap: 6, flexWrap: 'wrap' },
  filterChip: { padding: '5px 10px', borderRadius: 14, border: '1px solid #ddd', background: '#fafafa', cursor: 'pointer', fontSize: 12 },
  filterChipActive: { padding: '5px 10px', borderRadius: 14, border: '1px solid #4f46e5', background: '#eef2ff', color: '#4f46e5', cursor: 'pointer', fontSize: 12 },
  inputRow: { display: 'flex', gap: 10, marginBottom: 20 },
  textarea: { flex: 1, minHeight: 60, padding: 12, borderRadius: 10, border: '1px solid #ddd', fontSize: 14, resize: 'vertical', fontFamily: 'inherit' },
  askBtn: { padding: '0 24px', borderRadius: 10, border: 'none', background: '#4f46e5', color: '#fff', cursor: 'pointer', fontWeight: 600 },
  errorBox: { background: '#fee2e2', color: '#991b1b', padding: 12, borderRadius: 8, marginBottom: 16 },
  resultGrid: { display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 24 },
  sectionTitle: { fontSize: 14, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, color: '#555', marginBottom: 8, marginTop: 20 },
  answerCol: {},
  answerBox: { background: '#f8f9fc', border: '1px solid #eee', borderRadius: 10, padding: 16, whiteSpace: 'pre-wrap', fontSize: 14, lineHeight: 1.6 },
  traceBox: { background: '#fff', border: '1px solid #eee', borderRadius: 10, padding: 12 },
  traceStep: { display: 'flex', gap: 8, fontSize: 12, padding: '6px 0', borderBottom: '1px solid #f0f0f0' },
  traceAgent: { fontWeight: 700, color: '#4f46e5', minWidth: 70 },
  traceAction: { color: '#888', minWidth: 110 },
  traceDetail: { color: '#333', flex: 1 },
  latency: { fontSize: 11, color: '#999', marginTop: 8 },
  evidenceCol: { maxHeight: 700, overflowY: 'auto' },
  evidenceCard: { background: '#fff', border: '1px solid #eee', borderRadius: 10, padding: 12, marginBottom: 10 },
  evidenceMeta: { display: 'flex', justifyContent: 'space-between', marginBottom: 6 },
  badge: { fontSize: 10, background: '#eef2ff', color: '#4f46e5', padding: '2px 8px', borderRadius: 10, fontWeight: 600 },
  evidenceScore: { fontSize: 11, color: '#999' },
  evidenceTitle: { fontWeight: 600, fontSize: 13, marginBottom: 4 },
  evidenceText: { fontSize: 12, color: '#555', lineHeight: 1.5 },
  evidenceId: { fontSize: 10, color: '#bbb', marginTop: 6 },
  historySection: { marginTop: 30 },
  historyItem: { padding: '8px 12px', background: '#fafafa', borderRadius: 8, marginBottom: 6, fontSize: 13, cursor: 'pointer', border: '1px solid #eee' },
}
