<script setup>
import { Activity } from 'lucide-vue-next'

defineProps({
  riskData: {
    type: Object,
    required: true
  },
  riskTheme: {
    type: Object,
    required: true
  }
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
</template>