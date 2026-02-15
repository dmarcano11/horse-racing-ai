import Navbar from '../components/layout/Navbar'
import HorseCanvas from '../components/layout/HorseCanvas'
import TrustSection from '../components/landing/TrustSection'
import FeatureChatPreview from '../components/landing/FeatureChatPreview'
import FeatureDashPreview from '../components/landing/FeatureDashPreview'
import FeaturePredPreview from '../components/landing/FeaturePredPreview'
import FeatureResultsPreview from '../components/landing/FeatureResultsPreview'

export default function LandingPage() {
  return (
    <div style={{ background: 'var(--obsidian)' }}>
      <Navbar />
      
      {/* Horse Canvas Scroll Animation */}
      <HorseCanvas />
      
      {/* Trust Section */}
      <TrustSection />
      
      {/* Feature 01: Chat */}
      <section style={{ background: 'var(--obsidian)', padding: '96px 0' }}>
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left: Copy */}
            <div>
              <div className="font-mono text-[9px] tracking-[0.3em] uppercase mb-4" style={{ color: 'rgba(196,158,66,0.6)' }}>
                Feature 01 — Research
              </div>
              <h2 className="font-display text-5xl italic mb-6" style={{ color: 'var(--cream)' }}>
                Ask anything. Get race intelligence.
              </h2>
              <p className="font-body text-base leading-relaxed mb-6" style={{ color: 'var(--slate)' }}>
                Powered by Claude + RAG. Access today's race cards, ML predictions, historical data. Replace hours of manual research with one question.
              </p>
              <ul className="space-y-3 mb-8">
                {[
                  "Today's full race cards loaded automatically",
                  "ML predictions explained in plain language",
                  "Ask about any US track or race by name"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 font-body text-sm" style={{ color: 'var(--slate)' }}>
                    <span style={{ color: 'var(--gold)' }}>✓</span>
                    {item}
                  </li>
                ))}
              </ul>
              <a
                href="/chat"
                className="inline-block font-mono text-[11px] tracking-[0.2em] uppercase rounded px-6 py-3 transition-all"
                style={{
                  background: 'linear-gradient(135deg, var(--gold), #A8852E)',
                  color: 'var(--obsidian)',
                  textDecoration: 'none',
                  fontWeight: 600
                }}
              >
                Try the AI Expert →
              </a>
            </div>
            
            {/* Right: Preview */}
            <div>
              <FeatureChatPreview />
            </div>
          </div>
        </div>
      </section>
      
      {/* Feature 02: Dashboard */}
      <section style={{ background: 'var(--deep)', padding: '96px 0' }}>
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left: Preview */}
            <div>
              <FeatureDashPreview />
            </div>
            
            {/* Right: Copy */}
            <div>
              <div className="font-mono text-[9px] tracking-[0.3em] uppercase mb-4" style={{ color: 'rgba(196,158,66,0.6)' }}>
                Feature 02 — Dashboard
              </div>
              <h2 className="font-display text-5xl mb-6" style={{ color: 'var(--cream)' }}>
                Every US track. Every race. One view.
              </h2>
              <p className="font-body text-base leading-relaxed mb-6" style={{ color: 'var(--slate)' }}>
                Navigate by date. Filter by track. See all races for the day with surface, distance, purse, and live status at a glance.
              </p>
              <ul className="space-y-3 mb-8">
                {[
                  "15+ US tracks updated daily",
                  "Live race status in real time",
                  "Navigate any date — past or future"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 font-body text-sm" style={{ color: 'var(--slate)' }}>
                    <span style={{ color: 'var(--gold)' }}>✓</span>
                    {item}
                  </li>
                ))}
              </ul>
              <a
                href="/races"
                className="inline-block font-mono text-[11px] tracking-[0.2em] uppercase rounded px-6 py-3 transition-all"
                style={{
                  background: 'none',
                  border: '1px solid var(--border-hi)',
                  color: 'var(--gold)',
                  textDecoration: 'none'
                }}
              >
                Open the Dashboard →
              </a>
            </div>
          </div>
        </div>
      </section>
      
      {/* Feature 03: Predictions */}
      <section style={{ background: 'var(--obsidian)', padding: '96px 0' }}>
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left: Copy */}
            <div>
              <div className="font-mono text-[9px] tracking-[0.3em] uppercase mb-4" style={{ color: 'rgba(196,158,66,0.6)' }}>
                Feature 03 — Predictions
              </div>
              <h2 className="font-display text-5xl italic mb-6" style={{ color: 'var(--cream)' }}>
                ML predictions for every runner.
              </h2>
              <p className="font-body text-base leading-relaxed mb-6" style={{ color: 'var(--slate)' }}>
                Click any race to see the full field with ML win probabilities, odds comparison, jockey/trainer. The model's top pick is highlighted.
              </p>
              <ul className="space-y-3 mb-8">
                {[
                  "Win probability for every runner",
                  "Model top pick highlighted",
                  "Odds vs. model confidence comparison"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 font-body text-sm" style={{ color: 'var(--slate)' }}>
                    <span style={{ color: 'var(--gold)' }}>✓</span>
                    {item}
                  </li>
                ))}
              </ul>
              <a
                href="/races"
                className="inline-block font-mono text-[11px] tracking-[0.2em] uppercase rounded px-6 py-3 transition-all"
                style={{
                  background: 'linear-gradient(135deg, var(--gold), #A8852E)',
                  color: 'var(--obsidian)',
                  textDecoration: 'none',
                  fontWeight: 600
                }}
              >
                See a Race Card →
              </a>
            </div>
            
            {/* Right: Preview */}
            <div>
              <FeaturePredPreview />
            </div>
          </div>
        </div>
      </section>
      
      {/* Feature 04: Results */}
      <section style={{ background: 'var(--deep)', padding: '96px 0' }}>
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="font-mono text-[9px] tracking-[0.3em] uppercase mb-4" style={{ color: 'rgba(196,158,66,0.6)' }}>
            Feature 04 — Results
          </div>
          <h2 className="font-display text-5xl mb-6" style={{ color: 'var(--cream)' }}>
            See how the model performed.
          </h2>
          <p className="font-body text-base leading-relaxed mb-12 max-w-2xl mx-auto" style={{ color: 'var(--slate)' }}>
            Transparency is at the core of ATB. Browse completed races, see actual results, compare to the model's predictions. Hits and misses.
          </p>
          
          {/* Results Grid */}
          <div className="mb-12">
            <FeatureResultsPreview />
          </div>
          
          <ul className="space-y-3 mb-10 max-w-xl mx-auto text-left">
            {[
              "Historical results for every race",
              "Model accuracy tracked over time",
              "Free access — no paywall ever"
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2 font-body text-sm" style={{ color: 'var(--slate)' }}>
                <span style={{ color: 'var(--gold)' }}>✓</span>
                {item}
              </li>
            ))}
          </ul>
          
          <a
            href="/results"
            className="inline-block font-mono text-[11px] tracking-[0.2em] uppercase rounded px-6 py-3 transition-all"
            style={{
              background: 'none',
              border: '1px solid var(--border-hi)',
              color: 'var(--gold)',
              textDecoration: 'none'
            }}
          >
            Browse Results →
          </a>
        </div>
      </section>
      
      {/* Footer CTA */}
      <footer style={{ background: 'var(--obsidian)', borderTop: '1px solid var(--border)', padding: '80px 20px', textAlign: 'center' }}>
        <p className="font-mono text-[9px] tracking-[0.35em] uppercase mb-5" style={{ color: 'rgba(196,158,66,0.5)', letterSpacing: '0.35em' }}>
          The Free Edge
        </p>
        <h2 className="font-display font-bold italic mb-3" style={{ fontSize: 'clamp(48px,7vw,80px)', color: 'var(--gold)', lineHeight: 1 }}>
          Across the Board.
        </h2>
        <p className="font-mono text-[10px] tracking-[0.25em] mb-10" style={{ color: 'var(--slate)', letterSpacing: '0.25em' }}>
          Win · Place · Show — Research every angle.
        </p>
        <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 48 }}>
          <a
            href="/chat"
            className="font-mono text-[11px] tracking-[0.2em] uppercase font-semibold rounded px-8 py-3.5"
            style={{
              background: 'linear-gradient(135deg, var(--gold), #A8852E)',
              color: 'var(--obsidian)',
              textDecoration: 'none'
            }}
          >
            Explore the AI Expert →
          </a>
          <a
            href="/races"
            className="font-mono text-[11px] tracking-[0.2em] uppercase rounded px-7 py-3.5"
            style={{
              background: 'none',
              border: '1px solid var(--border-hi)',
              color: 'var(--gold)',
              textDecoration: 'none'
            }}
          >
            View Today's Races
          </a>
        </div>
        <p className="font-mono text-[9px] max-w-lg mx-auto leading-relaxed" style={{ color: 'var(--muted)' }}>
          Across the Board provides free research tools and ML-powered predictions for educational purposes. 
          Always bet responsibly.
        </p>
      </footer>
    </div>
  )
}
