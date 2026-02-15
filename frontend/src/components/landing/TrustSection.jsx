import { useInView } from 'framer-motion'
import { useRef } from 'react'

export default function TrustSection() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  const stats = [
    { value: '130+', label: 'Daily Races Covered' },
    { value: '15+', label: 'US Tracks Live' },
    { value: '0.604', label: 'Model ROC-AUC' },
    { value: '55', label: 'Predictive Features' },
  ]

  const features = [
    { label: 'Speed Figures', value: 88 },
    { label: 'Jockey Form', value: 74 },
    { label: 'Class Level', value: 65 },
    { label: 'Surface History', value: 61 },
    { label: 'Distance Profile', value: 58 },
    { label: 'Trainer Stats', value: 52 },
  ]

  return (
    <section style={{ background: 'var(--deep)', padding: '96px 0' }}>
      <div className="max-w-6xl mx-auto px-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16" ref={ref}>
          {stats.map((stat, i) => (
            <div
              key={i}
              className="rounded-xl p-6"
              style={{
                background: 'var(--card)',
                border: '1px solid rgba(196,158,66,0.10)',
                borderTop: '2px solid rgba(196,158,66,0.3)',
              }}
            >
              <div className="font-display text-4xl mb-2" style={{ color: 'var(--gold)' }}>
                {stat.value}
              </div>
              <div className="font-mono text-[9px] tracking-[0.2em] uppercase" style={{ color: 'var(--muted)' }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Two Column Section */}
        <div className="grid md:grid-cols-2 gap-12 mb-12">
          {/* Left: Copy */}
          <div>
            <h2 className="font-display text-4xl italic mb-6" style={{ color: 'var(--cream)' }}>
              An edge built on data, not guesswork.
            </h2>
            <div className="font-body text-base leading-relaxed space-y-4" style={{ color: 'var(--slate)' }}>
              <p>
                Across the Board gives you free access to the same ML-powered predictions and AI research tools that premium services charge $100+ per month for.
              </p>
              <p>
                Our Random Forest model analyzes 55 features for every runner — speed figures, jockey form, class level, surface history, and more. It's trained on thousands of real race results.
              </p>
              <p>
                Chat with our AI expert powered by Claude + RAG. Ask about any race, any runner, any betting strategy. Get instant, intelligent answers backed by real data.
              </p>
              <p>
                We show you when the model is right AND when it's wrong. Full transparency. No hidden agenda. Just data-driven research to help you make better decisions.
              </p>
            </div>
          </div>

          {/* Right: Feature Bars */}
          <div
            className="rounded-2xl p-6"
            style={{
              background: 'var(--surface)',
              border: '1px solid rgba(196,158,66,0.10)',
            }}
          >
            <h3 className="font-display text-2xl mb-6" style={{ color: 'var(--cream)' }}>
              ML Feature Importance
            </h3>
            <div className="space-y-4">
              {features.map((feature, i) => (
                <div key={i}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-[10px]" style={{ color: 'var(--slate)' }}>
                      {feature.label}
                    </span>
                    <span className="font-mono text-[10px]" style={{ color: 'var(--gold)' }}>
                      {feature.value}%
                    </span>
                  </div>
                  <div
                    className="h-1.5 rounded-full overflow-hidden"
                    style={{ background: 'rgba(255,255,255,0.05)' }}
                  >
                    <div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{
                        width: isInView ? `${feature.value}%` : '0%',
                        background: 'linear-gradient(90deg, var(--blue), var(--gold))',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Free Banner */}
        <div
          className="text-center py-4 rounded-lg"
          style={{
            background: 'rgba(196,158,66,0.05)',
            border: '1px solid rgba(196,158,66,0.12)',
            borderBottom: '1px solid rgba(196,158,66,0.12)',
          }}
        >
          <p className="font-mono text-[11px] tracking-[0.3em]" style={{ color: 'rgba(196,158,66,0.7)' }}>
            ✦  100% FREE — No subscription. No paywall. Research like a pro.  ✦
          </p>
        </div>
      </div>
    </section>
  )
}
