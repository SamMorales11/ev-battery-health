<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Activity, CalendarClock, Route } from 'lucide-vue-next'

const props = defineProps({
  form: {
    type: Object,
    default: () => ({
      depth_of_discharge: 70,
      state_of_charge: 90,
      fast_charge_ratio: 0.55,
      hard_braking_score: 65,
      average_speed: 85
    })
  },
  riskData: {
    type: Object,
    required: true
  },
  riskTheme: {
    type: Object,
    required: true
  }
})

// 1. Animasi Halus Persentase Risiko (ML Model)
const displayRisk = ref(props.riskData?.risk_percentage ?? 0)
let riskAnimFrame = null

const animateRisk = (start, end, duration = 300) => {
  if (riskAnimFrame) cancelAnimationFrame(riskAnimFrame)
  const startTime = performance.now()

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const ease = 1 - Math.pow(1 - progress, 3)
    displayRisk.value = start + (end - start) * ease

    if (progress < 1) {
      riskAnimFrame = requestAnimationFrame(step)
    } else {
      displayRisk.value = end
    }
  }

  riskAnimFrame = requestAnimationFrame(step)
}

watch(
  () => props.riskData?.risk_percentage,
  (newVal, oldVal) => {
    animateRisk(oldVal !== undefined ? oldVal : displayRisk.value, newVal ?? 0)
  }
)

// 2. Kalkulasi Dinamis Usia Baterai Berdasarkan Perilaku Langsung + Risiko Model
const calculatedTargetYears = computed(() => {
  // Baseline baterai NMC 811 dalam kondisi preservasi ideal (~9.6 Tahun)
  let years = 9.6

  // Penalti stres voltase & siklus kedalaman (DoD & SoC)
  const dodPenalty = ((props.form.depth_of_discharge - 30) / 65) * 1.8
  const socPenalty = ((props.form.state_of_charge - 50) / 50) * 1.3

  // Penalti arus cepat (DC Fast Charge), deselerasi agresif, dan kecepatan jelajah
  const fastChargePenalty = props.form.fast_charge_ratio * 2.3
  const brakePenalty = (props.form.hard_braking_score / 100) * 0.9
  const speedPenalty = ((props.form.average_speed - 20) / 100) * 0.8

  // Penalti probabilitas kegagalan dari model ML
  const mlRisk = Number(displayRisk.value) || 0
  const mlPenalty = (mlRisk / 100) * 1.5

  years -= (dodPenalty + socPenalty + fastChargePenalty + brakePenalty + speedPenalty + mlPenalty)

  // Rentang realistis degradasi sel: batas bawah 2.1 tahun s/d batas atas 9.4 tahun
  return Math.max(2.1, Math.min(9.4, years))
})

// 3. Animasi Halus Angka Tahun & Jarak Tempuh
const displayYears = ref(calculatedTargetYears.value)
let yearsAnimFrame = null

const animateYears = (start, end, duration = 300) => {
  if (yearsAnimFrame) cancelAnimationFrame(yearsAnimFrame)
  const startTime = performance.now()

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const ease = 1 - Math.pow(1 - progress, 3)
    displayYears.value = start + (end - start) * ease

    if (progress < 1) {
      yearsAnimFrame = requestAnimationFrame(step)
    } else {
      displayYears.value = end
    }
  }

  yearsAnimFrame = requestAnimationFrame(step)
}

watch(
  () => calculatedTargetYears.value,
  (newVal, oldVal) => {
    animateYears(oldVal ?? displayYears.value, newVal)
  }
)

const displayMileageKm = computed(() => {
  const km = Math.round((displayYears.value * 27000) / 1000) * 1000
  return km.toLocaleString('id-ID')
})

onMounted(() => {
  displayRisk.value = props.riskData?.risk_percentage ?? 0
  displayYears.value = calculatedTargetYears.value
})

onBeforeUnmount(() => {
  if (riskAnimFrame) cancelAnimationFrame(riskAnimFrame)
  if (yearsAnimFrame) cancelAnimationFrame(yearsAnimFrame)
})
</script>

<template>
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

    <!-- Big Metric Value with Animated Counting -->
    <div class="flex items-baseline gap-2.5 my-2">
      <span :class="['text-4xl sm:text-5xl font-extrabold font-mono tracking-normal leading-normal py-1 inline-block bg-gradient-to-br bg-clip-text text-transparent tabular-nums', riskTheme.gradientText]">
        {{ Number(displayRisk).toFixed(2) }}%
      </span>
      <span class="text-xs font-medium text-slate-400 uppercase tracking-widest">Calculated Risk</span>
    </div>

    <!-- Progress Bar -->
    <div class="relative w-full h-3 rounded-full bg-slate-950/80 p-0.5 border border-white/5 overflow-hidden mb-4 box-border">
      <div 
        :class="['h-full rounded-full bg-gradient-to-r transition-all duration-300 ease-out', riskTheme.bar]"
        :style="{ width: `${Math.min(Math.max(displayRisk, 0), 100)}%` }"
      />
    </div>

    <!-- Real-world Lifespan & Mileage Projections (Dinamis & Reaktif) -->
    <div class="grid grid-cols-2 gap-3 p-3.5 rounded-2xl bg-slate-950/60 border border-white/5 my-4 box-border">
      <div>
        <div class="flex items-center gap-1.5 text-slate-400 text-[11px] mb-1">
          <CalendarClock class="w-3.5 h-3.5 text-cyan-400" />
          <span class="font-medium uppercase tracking-wider">Proyeksi Usia</span>
        </div>
        <div class="flex items-baseline gap-1 font-mono">
          <span class="text-2xl font-bold text-white tabular-nums">~{{ Number(displayYears).toFixed(1) }}</span>
          <span class="text-xs text-slate-400 font-sans">Tahun</span>
        </div>
        <p class="text-[10px] text-slate-400 mt-1">Estimasi ambang 70% SOH</p>
      </div>

      <div class="border-l border-white/5 pl-3.5">
        <div class="flex items-center gap-1.5 text-slate-400 text-[11px] mb-1">
          <Route class="w-3.5 h-3.5 text-emerald-400" />
          <span class="font-medium uppercase tracking-wider">Masa Jarak</span>
        </div>
        <div class="flex items-baseline gap-1 font-mono">
          <span class="text-2xl font-bold text-cyan-300 tabular-nums">~{{ displayMileageKm }}</span>
          <span class="text-xs text-slate-400 font-sans">km</span>
        </div>
        <p class="text-[10px] text-slate-400 mt-1">Siklus operasional normal</p>
      </div>
    </div>

    <p class="text-xs text-slate-400 leading-relaxed border-t border-white/5 pt-3">
      {{ riskTheme.statusDesc }}
    </p>
  </div>
</template>