<script setup>
import { computed } from 'vue'
import { Gauge } from 'lucide-vue-next'

const props = defineProps({
  form: {
    type: Object,
    required: true
  },
  sliders: {
    type: Array,
    required: true
  }
})

defineEmits(['change'])

// Kalkulasi status dan warna risiko per parameter
const getFeatureRiskMeta = (key, val) => {
  let status = 'safe'

  switch (key) {
    case 'depth_of_discharge':
      if (val > 80) status = 'danger'
      else if (val > 65) status = 'warning'
      break
    case 'state_of_charge':
      if (val > 90) status = 'danger'
      else if (val > 80) status = 'warning'
      break
    case 'fast_charge_ratio':
      if (val > 0.70) status = 'danger'
      else if (val > 0.35) status = 'warning'
      break
    case 'hard_braking_score':
      if (val > 70) status = 'danger'
      else if (val > 40) status = 'warning'
      break
    case 'average_speed':
      if (val > 95) status = 'danger'
      else if (val > 70) status = 'warning'
      break
  }

  const palettes = {
    safe: {
      color: '#10b981',
      glow: 'rgba(16, 185, 129, 0.45)',
      text: 'text-emerald-400',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      border: 'border-white/5 hover:border-emerald-500/30',
      label: 'Optimal'
    },
    warning: {
      color: '#f59e0b',
      glow: 'rgba(245, 158, 11, 0.45)',
      text: 'text-amber-400',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      border: 'border-amber-500/20 hover:border-amber-500/40',
      label: 'Moderate'
    },
    danger: {
      color: '#f43f5e',
      glow: 'rgba(244, 63, 94, 0.55)',
      text: 'text-rose-400',
      badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      border: 'border-rose-500/30 hover:border-rose-500/50',
      label: 'High Stress'
    }
  }

  return palettes[status]
}
</script>

<template>
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
        :class="[
          'group p-4 rounded-2xl bg-slate-950/50 border transition-all duration-300 space-y-3 box-border',
          getFeatureRiskMeta(s.key, form[s.key]).border
        ]"
      >
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold text-slate-100 group-hover:text-white transition-colors">
              {{ s.label }}
            </span>
            <span :class="['text-[10px] font-medium px-2 py-0.5 rounded-full border transition-colors', getFeatureRiskMeta(s.key, form[s.key]).badge]">
              {{ getFeatureRiskMeta(s.key, form[s.key]).label }}
            </span>
          </div>

          <div class="flex items-baseline gap-1 font-mono shrink-0">
            <span :class="['text-base font-bold tracking-tight transition-colors duration-200', getFeatureRiskMeta(s.key, form[s.key]).text]">
              {{ s.key === 'fast_charge_ratio' ? (form[s.key] * 100).toFixed(0) : form[s.key] }}
            </span>
            <span class="text-[11px] text-slate-400">{{ s.unit || (s.key === 'fast_charge_ratio' ? '%' : '') }}</span>
          </div>
        </div>

        <!-- Range Slider Adaptif -->
        <div class="relative flex items-center">
          <input 
            type="range" 
            :min="s.min" 
            :max="s.max" 
            :step="s.step"
            v-model.number="form[s.key]" 
            @input="$emit('change')"
            :style="{
              '--slider-accent': getFeatureRiskMeta(s.key, form[s.key]).color,
              '--slider-glow': getFeatureRiskMeta(s.key, form[s.key]).glow,
              '--slider-fill': `${((form[s.key] - s.min) / (s.max - s.min)) * 100}%`
            }"
            class="adaptive-slider w-full h-2 rounded-lg appearance-none cursor-pointer focus:outline-none"
          />
        </div>

        <p class="text-xs sm:text-[12px] text-slate-300 leading-relaxed">
          {{ s.desc }}
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
.adaptive-slider {
  background: linear-gradient(
    to right,
    var(--slider-accent) 0%,
    var(--slider-accent) var(--slider-fill),
    #1e293b var(--slider-fill),
    #1e293b 100%
  );
}

.adaptive-slider::-webkit-slider-runnable-track {
  height: 6px;
  border-radius: 9999px;
}

.adaptive-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--slider-accent);
  cursor: pointer;
  margin-top: -6px;
  box-shadow: 0 0 14px var(--slider-glow);
  transition: transform 0.15s ease, background-color 0.25s ease, box-shadow 0.25s ease;
}

.adaptive-slider::-webkit-slider-thumb:hover {
  transform: scale(1.18);
  box-shadow: 0 0 18px var(--slider-glow);
}

.adaptive-slider::-moz-range-track {
  height: 6px;
  border-radius: 9999px;
  background: transparent;
}

.adaptive-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--slider-accent);
  cursor: pointer;
  border: none;
  box-shadow: 0 0 14px var(--slider-glow);
  transition: transform 0.15s ease, background-color 0.25s ease, box-shadow 0.25s ease;
}
</style>