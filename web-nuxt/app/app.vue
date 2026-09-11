<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { 
  Zap, 
  Gauge, 
  Sparkles, 
  CheckCircle2, 
  ArrowDownRight, 
  ArrowUpRight, 
  Activity,
  ShieldCheck,
  AlertTriangle,
  Flame,
  Radio,
  SlidersHorizontal
} from 'lucide-vue-next'

useHead({
  title: 'VoltIQ - EV Battery Health Simulator',
  htmlAttrs: {
    class: 'bg-[#070b14] overflow-x-hidden'
  },
  bodyAttrs: {
    class: 'bg-[#070b14] m-0 p-0 text-slate-100 font-sans antialiased overflow-x-hidden selection:bg-cyan-500 selection:text-black'
  }
})

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://127.0.0.1:8000'

const form = reactive({
  depth_of_discharge: 70,
  state_of_charge: 90,
  fast_charge_ratio: 0.55,
  hard_braking_score: 65,
  average_speed: 85
})

const defaultPresets = {
  eco: { depth_of_discharge: 45, state_of_charge: 75, fast_charge_ratio: 0.15, hard_braking_score: 20, average_speed: 45 },
  commuter: { depth_of_discharge: 60, state_of_charge: 85, fast_charge_ratio: 0.35, hard_braking_score: 40, average_speed: 65 },
  aggressive: { depth_of_discharge: 85, state_of_charge: 98, fast_charge_ratio: 0.80, hard_braking_score: 85, average_speed: 105 }
}

const activePreset = ref('custom')

const riskData = ref({
  risk_percentage: 1.07,
  risk_level: 'HEALTHY'
})

const optimization = ref(null)
const isPredicting = ref(false)
const isOptimizing = ref(false)
let debounceTimer = null

const calculateRisk = async () => {
  isPredicting.value = true
  try {
    const res = await fetch(`${apiBase}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    if (res.ok) riskData.value = await res.json()
  } catch (err) {
    console.error('API predict error:', err)
  } finally {
    isPredicting.value = false
  }
}

const onSliderChange = () => {
  activePreset.value = 'custom'
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    calculateRisk()
  }, 100)
}

const runOptimization = async () => {
  isOptimizing.value = true
  try {
    const res = await fetch(`${apiBase}/api/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    if (res.ok) optimization.value = await res.json()
  } catch (err) {
    console.error('API optimize error:', err)
  } finally {
    isOptimizing.value = false
  }
}

const applyPreset = (mode) => {
  activePreset.value = mode
  Object.assign(form, defaultPresets[mode])
  optimization.value = null
  calculateRisk()
}

const applyRecommendation = () => {
  if (!optimization.value) return
  for (const item of optimization.value.recommendations) {
    form[item.feature] = item.recommended_value
  }
  activePreset.value = 'custom'
  calculateRisk()
}

const riskTheme = computed(() => {
  const p = riskData.value.risk_percentage
  if (p >= 65) {
    return {
      text: 'text-rose-400',
      gradientText: 'from-rose-400 via-rose-300 to-amber-300',
      glow: 'shadow-[0_0_50px_-12px_rgba(244,63,94,0.35)]',
      border: 'border-rose-500/30',
      bar: 'from-amber-500 to-rose-500',
      badge: 'bg-rose-500/10 text-rose-300 border-rose-500/30 shadow-[0_0_15px_rgba(244,63,94,0.2)]',
      icon: Flame,
      statusDesc: 'Probabilitas degradasi fatal tinggi. Parameter operasional perlu penyesuaian secepatnya.'
    }
  }
  if (p >= 35) {
    return {
      text: 'text-amber-400',
      gradientText: 'from-amber-300 via-amber-200 to-yellow-400',
      glow: 'shadow-[0_0_50px_-12px_rgba(245,158,11,0.35)]',
      border: 'border-amber-500/30',
      bar: 'from-cyan-500 to-amber-500',
      badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.2)]',
      icon: AlertTriangle,
      statusDesc: 'Baterai mengalami stres operasional moderat. Disarankan menurunkan batas atas pengisian harian.'
    }
  }
  return {
    text: 'text-emerald-400',
    gradientText: 'from-emerald-400 via-teal-300 to-cyan-300',
    glow: 'shadow-[0_0_50px_-12px_rgba(16,185,129,0.35)]',
    border: 'border-emerald-500/30',
    bar: 'from-teal-500 to-emerald-400',
    badge: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)]',
    icon: ShieldCheck,
    statusDesc: 'Kombinasi penggunaan berada di zona aman optimal. Laju degradasi sel baterai minimum.'
  }
})

const sliders = [
  { key: 'depth_of_discharge', label: 'Depth of Discharge (DoD)', unit: '%', min: 30, max: 95, step: 1, desc: 'Tingkat pengurasan kapasitas baterai sebelum siklus charge berikutnya' },
  { key: 'state_of_charge', label: 'Target State of Charge (SoC)', unit: '%', min: 50, max: 100, step: 1, desc: 'Batas ambang atas pengisian harian yang disarankan (rekomendasi ≤ 80%)' },
  { key: 'fast_charge_ratio', label: 'DC Fast Charge Share', unit: '', min: 0.0, max: 1.0, step: 0.05, desc: 'Rasio sesi pengisian SPKLU arus cepat (DC) dibanding pengisian biasa' },
  { key: 'hard_braking_score', label: 'Hard Braking Intensity', unit: 'pts', min: 0, max: 100, step: 1, desc: 'Intensitas deselerasi ekstrem yang memicu lonjakan arus regeneratif berlebih' },
  { key: 'average_speed', label: 'Operational Cruising Speed', unit: 'km/h', min: 20, max: 120, step: 1, desc: 'Kecepatan rerata berkendara yang mempengaruhi laju pengosongan daya' }
]

// Komputasi Titik Poligon Radar Chart (Current Profile vs Recommended Profile)
const radarData = computed(() => {
  if (!optimization.value) return null
  const cx = 130
  const cy = 100
  const rMax = 62
  const total = sliders.length

  const optMap = {}
  optimization.value.recommendations.forEach(item => {
    optMap[item.feature] = item.recommended_value
  })

  const calcPoint = (val, min, max, index, customRadius = null) => {
    const norm = customRadius !== null ? customRadius : Math.max(0.12, Math.min(1, (val - min) / (max - min)))
    const radius = customRadius !== null ? customRadius : rMax * norm
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle)
    }
  }

  const currentPoints = sliders.map((s, i) => calcPoint(form[s.key], s.min, s.max, i))
  const optimalPoints = sliders.map((s, i) => {
    const val = optMap[s.key] !== undefined ? optMap[s.key] : form[s.key]
    return calcPoint(val, s.min, s.max, i)
  })

  const currentPolygon = currentPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const optimalPolygon = optimalPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')

  const gridLevels = [0.35, 0.7, 1.0].map(lvl => {
    return sliders.map((_, i) => {
      const p = calcPoint(0, 0, 1, i, rMax * lvl)
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`
    }).join(' ')
  })

  const axes = sliders.map((_, i) => {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2
    return {
      x2: (cx + rMax * Math.cos(angle)).toFixed(1),
      y2: (cy + rMax * Math.sin(angle)).toFixed(1)
    }
  })

  const shortLabels = ['DoD', 'SoC', 'Fast Chg', 'Braking', 'Speed']
  const labelPositions = sliders.map((_, i) => {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2
    const labelRadius = rMax + 16
    let anchor = 'middle'
    if (i === 1 || i === 2) anchor = 'start'
    if (i === 3 || i === 4) anchor = 'end'
    return {
      text: shortLabels[i],
      x: (cx + labelRadius * Math.cos(angle)).toFixed(1),
      y: (cy + labelRadius * Math.sin(angle) + 3).toFixed(1),
      anchor
    }
  })

  return {
    cx,
    cy,
    currentPolygon,
    optimalPolygon,
    gridLevels,
    axes,
    labelPositions
  }
})

onMounted(() => {
  calculateRisk()
})
</script>

<template>
  <div class="w-full min-h-screen bg-[#070b14] text-slate-100 relative overflow-x-hidden box-border">
    
    <!-- Background Ambient Glows -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div class="absolute -top-32 left-1/4 w-[32rem] h-[32rem] bg-cyan-500/10 rounded-full blur-[150px]" />
      <div class="absolute top-1/3 -right-32 w-[34rem] h-[34rem] bg-indigo-600/10 rounded-full blur-[160px]" />
      <div class="absolute -bottom-20 left-10 w-[28rem] h-[28rem] bg-emerald-500/10 rounded-full blur-[150px]" />
    </div>

    <!-- Main Container Full Screen -->
    <div class="relative z-10 w-full min-h-screen px-4 sm:px-6 lg:px-10 py-6 flex flex-col justify-between space-y-6 box-border max-w-[1600px] mx-auto">
      
      <!-- Top Navigation Bar -->
      <header class="w-full flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl bg-slate-900/40 border border-white/10 backdrop-blur-xl shadow-2xl shadow-black/50 box-border">
        
        <!-- Brand / Identity -->
        <div class="flex items-center gap-3.5 min-w-0">
          <div class="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-400/20 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)] shrink-0">
            <Zap class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h1 class="text-lg font-bold tracking-tight text-white truncate">VoltIQ Telemetry</h1>
              <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 shrink-0">
                <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                LIGHTGBM OP-CORE
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5 truncate">Simulasi Komparasi Kebiasaan Pengemudi & Preservasi Sel Baterai EV</p>
          </div>
        </div>

        <!-- Controls: Presets Segmented Bar & Auto-Optimize Action -->
        <div class="flex flex-wrap items-center gap-3 shrink-0 w-full md:w-auto justify-start md:justify-end">
          
          <!-- Segmented Preset Selector -->
          <div class="inline-flex items-center p-1 rounded-xl bg-slate-950/70 border border-white/10 backdrop-blur-md">
            <button 
              @click="applyPreset('eco')" 
              :class="[
                'px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer',
                activePreset === 'eco' 
                  ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-[0_0_12px_rgba(16,185,129,0.15)]' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
              ]"
            >
              Eco-Safe
            </button>
            <button 
              @click="applyPreset('commuter')" 
              :class="[
                'px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer',
                activePreset === 'commuter' 
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-[0_0_12px_rgba(6,182,212,0.15)]' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
              ]"
            >
              Commuter
            </button>
            <button 
              @click="applyPreset('aggressive')" 
              :class="[
                'px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer',
                activePreset === 'aggressive' 
                  ? 'bg-rose-500/15 text-rose-300 border border-rose-500/30 shadow-[0_0_12px_rgba(244,63,94,0.15)]' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
              ]"
            >
              Abusive
            </button>
          </div>

          <!-- Professional Minimalist Auto-Optimize Button -->
          <button 
            @click="runOptimization"
            :disabled="isOptimizing"
            class="group relative inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl text-cyan-300 bg-cyan-950/40 hover:bg-cyan-900/40 border border-cyan-500/30 hover:border-cyan-400/60 shadow-[0_0_20px_rgba(6,182,212,0.15)] hover:shadow-[0_0_25px_rgba(6,182,212,0.3)] transition-all duration-300 disabled:opacity-40 cursor-pointer shrink-0 whitespace-nowrap active:scale-[0.98]"
          >
            <Sparkles class="w-3.5 h-3.5 text-cyan-400 transition-transform duration-300 group-hover:rotate-12" />
            <span>{{ isOptimizing ? 'Mengoptimalkan...' : 'Auto-Optimize' }}</span>
          </button>

        </div>
      </header>

      <!-- Main Dashboard Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start flex-1 box-border w-full">
        
        <!-- Left Panel: Sliders (7 Cols) -->
        <div class="lg:col-span-7 space-y-6 box-border">
          <div class="p-5 sm:p-6 rounded-3xl bg-slate-900/40 border border-white/10 backdrop-blur-2xl shadow-xl space-y-5 box-border">
            
            <div class="flex items-center justify-between pb-4 border-b border-white/5">
              <div class="flex items-center gap-2.5">
                  <Gauge class="w-4.5 h-4.5 text-cyan-400" />
                  <h2 class="text-sm font-bold tracking-wider uppercase text-slate-200">Kontrol Parameter Perilaku</h2>
                </div>
              <span class="text-[11px] font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-full border border-white/5 shrink-0">
                5 Actionable Inputs
              </span>
            </div>

            <!-- Sliders Container -->
            <div class="space-y-4">
              <div 
                v-for="s in sliders" 
                :key="s.key"
                class="group p-4 rounded-2xl bg-slate-950/50 border border-white/5 hover:border-cyan-500/30 transition-all duration-300 space-y-3 box-border"
              >
                <div class="flex items-center justify-between text-xs">
                  <span class="text-sm font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">
                    {{ s.label }}
                  </span>
                  <div class="flex items-baseline gap-1 font-mono shrink-0">
                    <span class="text-base font-bold text-white tracking-tight">
                      {{ s.key === 'fast_charge_ratio' ? (form[s.key] * 100).toFixed(0) : form[s.key] }}
                    </span>
                    <span class="text-[11px] text-slate-400">{{ s.unit || (s.key === 'fast_charge_ratio' ? '%' : '') }}</span>
                  </div>
                </div>

                <!-- Range Slider -->
                <div class="relative flex items-center">
                  <input 
                    type="range" 
                    :min="s.min" 
                    :max="s.max" 
                    :step="s.step"
                    v-model.number="form[s.key]" 
                    @input="onSliderChange"
                    class="custom-slider w-full h-2 rounded-lg appearance-none cursor-pointer focus:outline-none"
                  />
                </div>

                <p class="text-xs sm:text-[12px] text-slate-300 leading-relaxed">
                  {{ s.desc }}
                </p>
              </div>
            </div>

          </div>
        </div>

        <!-- Right Panel: Gauge & Output (5 Cols) -->
        <div class="lg:col-span-5 space-y-6 box-border">
          
          <!-- Risk Indicator Card -->
          <div :class="['p-5 sm:p-6 rounded-3xl bg-slate-900/40 border backdrop-blur-2xl transition-all duration-500 relative overflow-hidden box-border', riskTheme.border, riskTheme.glow]">
            
            <div class="flex items-center justify-between mb-5">
              <div class="flex items-center gap-2">
                <Activity class="w-4 h-4 text-cyan-400 animate-pulse" />
                <span class="text-xs font-semibold tracking-wider uppercase text-slate-300">Failure Risk Index</span>
              </div>
              <span :class="['inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border transition-colors shrink-0', riskTheme.badge]">
                <component :is="riskTheme.icon" class="w-3.5 h-3.5" />
                {{ riskData.risk_level }}
              </span>
            </div>

            <!-- Big Metric Value -->
            <div class="flex items-baseline gap-2.5 my-2">
              <span :class="['text-4xl sm:text-5xl font-extrabold font-mono tracking-normal leading-normal py-1 inline-block bg-gradient-to-br bg-clip-text text-transparent', riskTheme.gradientText]">
                    {{ riskData.risk_percentage }}%
              </span>
              <span class="text-xs font-medium text-slate-400 uppercase tracking-widest">Calculated Risk</span>
            </div>

            <!-- Progress Bar -->
            <div class="relative w-full h-3 rounded-full bg-slate-950/80 p-0.5 border border-white/5 overflow-hidden mb-4 box-border">
              <div 
                :class="['h-full rounded-full bg-gradient-to-r transition-all duration-500 ease-out', riskTheme.bar]"
                :style="{ width: `${Math.min(riskData.risk_percentage, 100)}%` }"
              />
            </div>

            <p class="text-xs text-slate-400 leading-relaxed border-t border-white/5 pt-3">
              {{ riskTheme.statusDesc }}
            </p>
          </div>

          <!-- Counterfactual / What-If Result Card -->
          <div 
            v-if="optimization" 
            class="p-5 sm:p-6 rounded-3xl bg-slate-900/60 border border-cyan-500/40 backdrop-blur-2xl shadow-[0_0_40px_-10px_rgba(6,182,212,0.25)] space-y-4 box-border"
          >
            <div class="flex items-center justify-between pb-3 border-b border-white/10">
              <div class="flex items-center gap-2">
                <Sparkles class="w-4 h-4 text-cyan-400" />
                <h3 class="text-xs font-bold text-white uppercase tracking-wider">Hasil Optimasi Kebiasaan</h3>
              </div>
              <span class="text-[10px] font-mono text-cyan-300 bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-500/30 shrink-0">
                ⚡ {{ optimization.latency_ms }} ms
              </span>
            </div>

            <!-- Metric Difference Banner -->
            <div class="grid grid-cols-2 gap-3 p-3.5 rounded-2xl bg-slate-950/60 border border-white/5 box-border">
              <div>
                <p class="text-[10px] text-slate-400 uppercase font-medium">Potensi Reduksi</p>
                <p class="text-xl font-bold font-mono text-emerald-400">
                  -{{ optimization.risk_reduced_percent }}%
                </p>
              </div>
              <div class="text-right border-l border-white/5 pl-3">
                <p class="text-[10px] text-slate-400 uppercase font-medium">Proyeksi Risiko Baru</p>
                <p class="text-xl font-bold font-mono text-cyan-300">
                  {{ (optimization.optimized_risk * 100).toFixed(2) }}%
                </p>
              </div>
            </div>

            <!-- Radar Chart: Current Habit vs Optimal Habit -->
            <div v-if="radarData" class="p-3.5 rounded-2xl bg-slate-950/70 border border-white/5 space-y-2.5 box-border">
              <div class="flex items-center justify-between text-[11px]">
                <Polygon class="text-xs sm:text-sm font-semibold text-slate-100"></Polygon Komparasi Parameter</span>
                <div class="flex items-center gap-3">
                  <span class="flex items-center gap-1.5 text-cyan-300 font-mono text-[10px]">
                    <span class="w-2 h-2 rounded-full bg-cyan-400" />
                    Saat Ini
                  </span>
                  <span class="flex items-center gap-1.5 text-emerald-300 font-mono text-[10px]">
                    <span class="w-2 h-2 rounded-full bg-emerald-400" />
                    Optimal
                  </span>
                </div>
              </div>

              <div class="w-full flex justify-center py-1">
                <svg viewBox="0 0 260 200" class="w-full max-w-[280px] h-auto overflow-visible select-none">
                  <!-- Web Ring Grids -->
                  <polygon 
                    v-for="(ring, idx) in radarData.gridLevels" 
                    :key="'ring-' + idx"
                    :points="ring"
                    fill="none"
                    stroke="#334155"
                    stroke-width="1"
                    stroke-dasharray="3,3"
                    opacity="0.6"
                  />

                  <!-- Axis Rays -->
                  <line 
                    v-for="(axis, idx) in radarData.axes" 
                    :key="'axis-' + idx"
                    :x1="radarData.cx"
                    :y1="radarData.cy"
                    :x2="axis.x2"
                    :y2="axis.y2"
                    stroke="#1e293b"
                    stroke-width="1.2"
                  />

                  <!-- Current Profile Polygon (Cyan) -->
                  <polygon 
                    :points="radarData.currentPolygon"
                    fill="rgba(34, 211, 238, 0.2)"
                    stroke="#22d3ee"
                    stroke-width="1.8"
                    class="transition-all duration-300"
                  />

                  <!-- Optimal Profile Polygon (Emerald) -->
                  <polygon 
                    :points="radarData.optimalPolygon"
                    fill="rgba(16, 185, 129, 0.25)"
                    stroke="#10b981"
                    stroke-width="2"
                    class="transition-all duration-300"
                  />

                  <!-- Text Labels for 5 Features -->
                  <text 
                    v-for="(lbl, idx) in radarData.labelPositions" 
                    :key="'lbl-' + idx"
                    :x="lbl.x" 
                    :y="lbl.y" 
                    :text-anchor="lbl.anchor"
                    fill="#94a3b8" 
                    font-size="4.5" 
                    font-family="monospace"
                    font-weight="300"
                  >
                    {{ lbl.text }}
                  </text>
                </svg>
              </div>
            </div>

            <!-- Recommendation Changes -->
            
<div class="space-y-2.5">
  <div 
    v-for="rec in optimization.recommendations" 
    :key="rec.feature"
    class="flex items-center justify-between p-3 rounded-xl bg-slate-950/40 border border-white/5 hover:border-white/10 transition-colors box-border"
  >
    <!-- Label Nama Parameter (Dinaikkan ke text-sm & font-semibold) -->
    <span class="text-sm font-semibold text-slate-100 truncate pr-2">
      {{ sliders.find(s => s.key === rec.feature)?.label.split('(')[0] || rec.feature }}
    </span>
    
    <div class="flex items-center gap-2.5 font-mono shrink-0">
      <!-- Nilai Lama -->
      <span class="text-xs sm:text-sm text-slate-400 line-through">{{ rec.current_value }}</span>
      <span class="text-slate-500 text-xs">→</span>
      <!-- Nilai Rekomendasi Baru (Dinaikkan ke text-sm sm:text-base) -->
      <span class="text-sm sm:text-base text-cyan-300 font-bold">{{ rec.recommended_value }}</span>
      
      <!-- Badge Aksi Turunkan / Pertahankan (Dinaikkan ke text-xs) -->
      <span 
        :class="[
          'text-xs px-2.5 py-1 rounded-md font-sans font-medium flex items-center gap-1 shrink-0',
          rec.delta < 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
          rec.delta > 0 ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20' : 
          'bg-slate-800 text-slate-400'
        ]"
      >
        <ArrowDownRight v-if="rec.delta < 0" class="w-3.5 h-3.5" />
        <ArrowUpRight v-else-if="rec.delta > 0" class="w-3.5 h-3.5" />
        {{ rec.action }}
      </span>
    </div>
  </div>
</div>
            <!-- Apply Button -->
            <button 
              @click="applyRecommendation"
              class="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs tracking-wide uppercase transition-all shadow-[0_0_25px_rgba(16,185,129,0.3)] cursor-pointer"
            >
              <CheckCircle2 class="w-4 h-4 text-slate-950" />
              Terapkan Rekomendasi ke Slider
            </button>
          </div>

          <!-- Empty State Helper -->
          <div 
            v-else 
            class="p-6 rounded-3xl bg-slate-900/20 border border-dashed border-white/10 text-center space-y-2.5 box-border"
          >
            <div class="w-10 h-10 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mx-auto text-cyan-400">
              <Radio class="w-5 h-5 animate-pulse" />
            </div>
            <p class="text-xs font-medium text-slate-300">Siap Mensimulasikan Kebiasaan</p>
            <p class="text-[11px] text-slate-400 max-w-xs mx-auto">
              Klik tombol <strong class="text-cyan-400">Auto-Optimize</strong> di atas buat nyari konfigurasi kebiasaan paling aman dalam hitungan milidetik.
            </p>
          </div>

        </div>

      </div>

      <!-- Footer Bar -->
      <footer class="w-full pt-4 pb-2 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 gap-2 box-border">
        <p>VoltIQ Systems • Predictive Battery Degradation Intelligence</p>
        <p>Inference Engine: FastAPI & LightGBM Coordinate Search</p>
      </footer>

    </div>
  </div>
</template>

<style>
/* CSS Reset Global & Button Reset */
*, *::before, *::after {
  box-sizing: border-box !important;
}

html, body, #__nuxt {
  margin: 0 !important;
  padding: 0 !important;
  width: 100%;
  max-width: 100%;
  min-height: 100vh;
  background-color: #070b14;
  overflow-x: hidden;
}

button {
  background-color: transparent;
  border-width: 0;
  font-family: inherit;
  font-size: 100%;
  line-height: inherit;
  color: inherit;
  margin: 0;
  padding: 0;
}

/* Custom Range Slider Track & Thumb */
.custom-slider {
  background: #1e293b;
}

.custom-slider::-webkit-slider-runnable-track {
  height: 6px;
  border-radius: 9999px;
  background: #1e293b;
}

.custom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #22d3ee;
  cursor: pointer;
  margin-top: -6px;
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.7);
  transition: transform 0.15s ease;
}

.custom-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.9);
}

.custom-slider::-moz-range-track {
  height: 6px;
  border-radius: 9999px;
  background: #1e293b;
}

.custom-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #22d3ee;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.7);
}
</style>