import { useRef, useEffect, useState } from 'react'
import { useScroll, useSpring, useTransform } from 'framer-motion'
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion'

// Frame count and paths based on actual files in /public/sequence/
const FRAME_COUNT = 24
const FRAMES_PATH = '/sequence/frame_'

// Map of frame index to actual delay suffix (alternates between 0.041s and 0.042s)
const getFrameDelay = (index) => {
  // Frames 01, 04, 07, 10, 13, 16, 19, 22 use 0.041s, others use 0.042s
  return [1, 4, 7, 10, 13, 16, 19, 22].includes(index) ? '_delay-0.041s.jpg' : '_delay-0.042s.jpg'
}

export default function HorseCanvas() {
  const wrapperRef = useRef(null)
  const canvasRef = useRef(null)
  const imagesRef = useRef([])
  const [loaded, setLoaded] = useState(false)
  const [progress, setProgress] = useState(0)

  const { scrollYProgress } = useScroll({ 
    target: wrapperRef, 
    offset: ['start start', 'end end'] 
  })
  const smoothProgress = useSpring(scrollYProgress, { stiffness: 80, damping: 30 })

  // Preload all frames
  useEffect(() => {
    let loadedCount = 0
    const images = []
    const loadPromises = []
    
    for (let i = 0; i < FRAME_COUNT; i++) {
      const img = new Image()
      const paddedIndex = String(i).padStart(2, '0')
      const frameExt = getFrameDelay(i)
      img.src = `${FRAMES_PATH}${paddedIndex}${frameExt}`
      
      const promise = new Promise((resolve) => {
        img.onload = () => {
          loadedCount++
          setProgress(Math.round((loadedCount / FRAME_COUNT) * 100))
          resolve(true)
        }
        img.onerror = (e) => {
          console.error(`Failed to load frame ${paddedIndex}:`, img.src, e)
          loadedCount++
          setProgress(Math.round((loadedCount / FRAME_COUNT) * 100))
          resolve(false)
        }
      })
      
      loadPromises.push(promise)
      images.push(img)
    }
    
    imagesRef.current = images
    
    // Wait for all images to load (or fail) before marking as loaded
    Promise.all(loadPromises).then(() => {
      const successfulLoads = images.filter(img => img.complete && img.naturalWidth > 0).length
      console.log(`Loaded ${successfulLoads}/${FRAME_COUNT} frames successfully`)
      if (successfulLoads > 0) {
        setLoaded(true)
      }
    })
  }, [])

  // Draw frame on scroll
  useEffect(() => {
    return smoothProgress.on('change', (val) => {
      const canvas = canvasRef.current
      if (!canvas || !loaded) return
      const ctx = canvas.getContext('2d')
      const frameIndex = Math.min(Math.round(val * (FRAME_COUNT - 1)), FRAME_COUNT - 1)
      const img = imagesRef.current[frameIndex]
      
      // Check if image is valid and loaded successfully
      if (!img || !img.complete || !img.naturalWidth || img.naturalWidth === 0) return

      // Contain fit
      const { width: cw, height: ch } = canvas
      const scale = Math.min(cw / img.naturalWidth, ch / img.naturalHeight)
      const x = (cw - img.naturalWidth * scale) / 2
      const y = (ch - img.naturalHeight * scale) / 2
      ctx.clearRect(0, 0, cw, ch)
      ctx.drawImage(img, x, y, img.naturalWidth * scale, img.naturalHeight * scale)
    })
  }, [smoothProgress, loaded])

  // Resize canvas
  useEffect(() => {
    const resize = () => {
      if (!canvasRef.current) return
      canvasRef.current.width = window.innerWidth
      canvasRef.current.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [])

  return (
    <div ref={wrapperRef} style={{ height: '400vh', position: 'relative' }}>
      {/* Loading screen */}
      {!loaded && (
        <div style={{
          position: 'sticky', top: 0, height: '100vh', width: '100%',
          background: 'var(--obsidian)',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', gap: 24,
        }}>
          <div className="font-mono text-[11px] tracking-[0.3em] uppercase" style={{ color: 'rgba(196,158,66,0.6)', letterSpacing: '0.3em' }}>
            Loading Race Data... {progress}%
          </div>
          <div style={{ width: 200, height: 2, background: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
            <div style={{ height: '100%', borderRadius: 1, background: 'var(--gold)', width: `${progress}%`, transition: 'width 0.2s' }} />
          </div>
        </div>
      )}

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'sticky', top: 0,
          height: '100vh', width: '100%',
          display: loaded ? 'block' : 'none',
          opacity: loaded ? 1 : 0,
          transition: 'opacity 0.6s',
        }}
      />

      {/* Dark bottom gradient */}
      {loaded && (
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: '30vh',
          background: 'linear-gradient(to bottom, transparent, var(--obsidian))',
          pointerEvents: 'none',
        }} />
      )}

      {/* BEAT A: 0–22% — Hero brand reveal */}
      <BeatOverlay progress={smoothProgress} start={0} end={0.22} align="center">
        <div className="font-mono text-[10px] tracking-[0.4em] uppercase mb-5 flex items-center gap-3" style={{ color: 'rgba(196,158,66,0.6)' }}>
          <span style={{display:'inline-block',width:30,height:1,background:'linear-gradient(90deg,transparent,rgba(196,158,66,0.5))'}}/>
          AI-Powered Horse Racing Intelligence
          <span style={{display:'inline-block',width:30,height:1,background:'linear-gradient(90deg,rgba(196,158,66,0.5),transparent)'}}/>
        </div>
        <h1 className="font-display font-bold leading-tight mb-4" style={{ fontSize:'clamp(52px, 8vw, 96px)', color:'var(--cream)' }}>
          Across the<br/><em style={{fontStyle:'italic', color:'var(--gold)'}}>Board</em>
        </h1>
        <p className="font-mono text-[11px] tracking-[0.2em]" style={{ color:'var(--slate)' }}>
          Win · Place · Show — Research every angle
        </p>
      </BeatOverlay>

      {/* BEAT B: 25–48% — Win Place Show */}
      <BeatOverlay progress={smoothProgress} start={0.25} end={0.48} align="left">
        <h2 className="font-display font-bold mb-4" style={{ fontSize:'clamp(40px, 6vw, 72px)', color:'var(--gold)' }}>
          Win. Place. Show.
        </h2>
        <p className="font-body text-[15px] leading-relaxed" style={{ color:'var(--slate)', maxWidth:360 }}>
          Research all three outcomes before you wager. ML predictions for every US race, completely free.
        </p>
      </BeatOverlay>

      {/* BEAT C: 52–72% — The Model */}
      <BeatOverlay progress={smoothProgress} start={0.52} end={0.72} align="right">
        <h2 className="font-display font-bold mb-4" style={{ fontSize:'clamp(40px, 6vw, 72px)', color:'var(--cream)' }}>
          55 Features.<br/>One Model.
        </h2>
        <p className="font-body text-[15px] leading-relaxed" style={{ color:'var(--slate)', maxWidth:360 }}>
          Random Forest trained on speed figures, class, jockey form, surface history, and more. ROC-AUC 0.604.
        </p>
      </BeatOverlay>

      {/* BEAT D: 76–98% — CTA */}
      <BeatOverlay progress={smoothProgress} start={0.76} end={0.98} align="center">
        <h2 className="font-display font-bold italic mb-3" style={{ fontSize:'clamp(44px, 6vw, 72px)', color:'var(--gold)', lineHeight:1 }}>
          Start Your Research
        </h2>
        <p className="font-mono text-[11px] tracking-[0.2em] mb-9" style={{ color:'var(--muted)', letterSpacing:'0.2em' }}>
          No signup. No paywall. Just data.
        </p>
        <div style={{ display:'flex', gap:14, justifyContent:'center', flexWrap:'wrap' }}>
          <a href="/chat" className="font-mono text-[11px] tracking-[0.2em] font-semibold uppercase rounded px-8 py-3.5 transition-all" style={{
            background:'linear-gradient(135deg, var(--gold), #A8852E)',
            color:'var(--obsidian)',
            textDecoration:'none'
          }}>
            Explore the AI Expert →
          </a>
          <a href="/races" className="font-mono text-[11px] tracking-[0.2em] uppercase rounded px-7 py-3.5 transition-all" style={{
            background:'none',
            border:'1px solid var(--border-hi)',
            color:'var(--gold)',
            textDecoration:'none'
          }}>
            View Today's Races
          </a>
        </div>
      </BeatOverlay>

      {/* Scroll hint */}
      <ScrollHint progress={smoothProgress} />
    </div>
  )
}

// Helper: positions a beat overlay sticky on screen
function BeatOverlay({ children, progress, start, end, align }) {
  const opacity = useTransform(progress, [start, start+0.08, end-0.08, end], [0,1,1,0])
  const y = useTransform(progress, [start, start+0.08, end-0.08, end], [20,0,0,-20])
  const justifyMap = { left: 'flex-start', right: 'flex-end', center: 'center' }
  const textAlign = align === 'left' ? 'left' : align === 'right' ? 'right' : 'center'
  
  return (
    <motion.div style={{
      position: 'absolute',
      top: `${start * 100}%`,
      left: 0, right: 0,
      height: `${(end - start) * 400}vh`,
      display: 'flex', alignItems: 'center',
      justifyContent: justifyMap[align],
      padding: align === 'left' ? '0 0 0 8vw' : align === 'right' ? '0 8vw 0 0' : '0 20px',
      pointerEvents: 'none',
      zIndex: 10,
    }}>
      <motion.div style={{ opacity, y, textAlign, pointerEvents: 'auto' }}>
        {children}
      </motion.div>
    </motion.div>
  )
}

function ScrollHint({ progress }) {
  const opacity = useTransform(progress, [0, 0.08], [1, 0])
  
  return (
    <motion.div style={{
      position: 'absolute', bottom: '74%', left: '50%', transform: 'translateX(-50%)',
      opacity, textAlign: 'center', zIndex: 10, pointerEvents: 'none',
    }}>
      <div className="font-mono text-[8px] tracking-[0.3em] uppercase mb-2" style={{ color:'var(--muted)', letterSpacing:'0.3em' }}>
        Scroll to explore
      </div>
      <motion.div
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
        style={{ color:'rgba(196,158,66,0.5)', fontSize:18 }}
      >
        ↓
      </motion.div>
    </motion.div>
  )
}
