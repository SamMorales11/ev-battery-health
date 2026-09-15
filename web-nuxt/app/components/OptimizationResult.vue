<script setup>
import { computed } from 'vue'
import { Sparkles, CheckCircle2, ArrowDownRight, ArrowUpRight, Radio, Hourglass } from 'lucide-vue-next'

const props = defineProps({
  optimization: {
    type: Object,
    default: null
  },
  form: {
    type: Object,
    required: true
  },
  sliders: {
    type: Array,
    required: true
  }
})

defineEmits(['apply'])

// Komputasi Tambahan Tahun Masa Pakai Baterai
const lifespanGainedYears = computed(() => {
  if (!props.optimization) return '0.0'
  const reduced = props.optimization.risk_reduced_percent ?? 0
  const gain = (reduced / 100) * 7.2
  return gain.toFixed(1)
})

// Komputasi Titik Poligon Radar Chart (Current Profile vs Recommended Profile)
const radarData = computed(() => {
  if (!props.optimization) return null
  const cx = 130
  const cy = 100
  const rMax = 62
  const total = props.sliders.length

  const optMap = {}
  props.optimization.recommendations.forEach(item => {
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

  const currentPoints = props.sliders.map((s, i) => calcPoint(props.form[s.key], s.min, s.max, i))
  const optimalPoints = props.sliders.map((s, i) => {
    const val = optMap[s.key] !== undefined ? optMap[s.key] : props.form[s.key]
    return calcPoint(val, s.min, s.max, i)
  })

  const currentPolygon = currentPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const optimalPolygon = optimalPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')

  const gridLevels = [0.35, 0.7, 1.0].map(lvl => {
    return props.sliders.map((_, i) => {
      const p = calcPoint(0, 0, 1, i, rMax * lvl)
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`
    }).join(' ')
  })

  const axes = props.sliders.map((_, i) => {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2
    return {
      x2: (cx + rMax * Math.cos(angle)).toFixed(1),
      y2: (cy + rMax * Math.sin(angle)).toFixed(1)
    }
  })

  const shortLabels = ['DoD', 'SoC', 'Fast Chg', 'Braking', 'Speed']
  const labelPositions = props.sliders.map((_, i) => {
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
</script>

<template>
  <div>
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

      <!-- Metric Difference Banner with Lifespan Extension -->
      <div class="grid grid-cols-3 gap-2.5 p-3.5 rounded-2xl bg-slate-950/60 border border-white/5 box-border">
        <div>
          <p class="text-[10px] text-slate-400 uppercase font-medium">Potensi Reduksi</p>
          <p class="text-lg sm:text-xl font-bold font-mono text-emerald-400">
            -{{ optimization.risk_reduced_percent }}%
          </p>
        </div>

        <div class="border-l border-white/5 pl-2.5">
          <p class="text-[10px] text-slate-400 uppercase font-medium">Risiko Baru</p>
          <p class="text-lg sm:text-xl font-bold font-mono text-cyan-300">
            {{ (optimization.optimized_risk * 100).toFixed(2) }}%
          </p>
        </div>

        <div class="border-l border-white/5 pl-2.5">
          <div class="flex items-center gap-1">
            <Hourglass class="w-3 h-3 text-emerald-400" />
            <p class="text-[10px] text-slate-400 uppercase font-medium">Ekstensi Usia</p>
          </div>
          <p class="text-lg sm:text-xl font-bold font-mono text-emerald-300">
            +{{ lifespanGainedYears }} <span class="text-xs font-sans text-slate-400">Thn</span>
          </p>
        </div>
      </div>

      <!-- Radar Chart: Current Habit vs Optimal Habit -->
      <div v-if="radarData" class="p-3.5 rounded-2xl bg-slate-950/70 border border-white/5 space-y-2.5 box-border">
        <div class="flex items-center justify-between text-[11px]">
          <span class="text-xs sm:text-sm font-semibold text-slate-100">Polygon Komparasi Parameter</span>
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
          <!-- Label Nama Parameter -->
          <span class="text-sm font-semibold text-slate-100 truncate pr-2">
            {{ sliders.find(s => s.key === rec.feature)?.label.split('(')[0] || rec.feature }}
          </span>
          
          <div class="flex items-center gap-2.5 font-mono shrink-0">
            <!-- Nilai Lama -->
            <span class="text-xs sm:text-sm text-slate-400 line-through">{{ rec.current_value }}</span>
            <span class="text-slate-500 text-xs">→</span>
            <!-- Nilai Rekomendasi Baru -->
            <span class="text-sm sm:text-base text-cyan-300 font-bold">{{ rec.recommended_value }}</span>
            
            <!-- Badge Aksi Turunkan / Pertahankan -->
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
        @click="$emit('apply')"
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
</template>