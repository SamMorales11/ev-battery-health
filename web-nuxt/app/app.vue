<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ShieldCheck, AlertTriangle, Flame } from 'lucide-vue-next'

useHead({
  title: 'VoltIQ - EV Battery Health Simulator',
  link: [
    {
      rel: 'icon',
      type: 'image/svg+xml',
      href: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2322d3ee"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'
    }
  ],
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
      
      <!-- 1. Header Bar Component -->
      <DashboardHeader 
        :active-preset="activePreset"
        :is-optimizing="isOptimizing"
        @select-preset="applyPreset"
        @optimize="runOptimization"
      />

      <!-- 2. Main Dashboard Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start flex-1 box-border w-full">
        
        <!-- Panel Kiri: 5 Sliders Component -->
        <div class="lg:col-span-7 space-y-6 box-border">
          <HabitControls 
            :form="form" 
            :sliders="sliders" 
            @change="onSliderChange"
          />
        </div>

        <!-- Panel Kanan: Gauge Risiko & Output Optimasi/Radar Component -->
        <div class="lg:col-span-5 space-y-6 box-border">
          <RiskGauge 
            :risk-data="riskData" 
            :risk-theme="riskTheme" 
          />

          <OptimizationResult 
            :optimization="optimization"
            :form="form"
            :sliders="sliders"
            @apply="applyRecommendation"
          />
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