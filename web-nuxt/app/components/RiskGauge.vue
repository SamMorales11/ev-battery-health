<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Activity } from 'lucide-vue-next'

const props = defineProps({
  riskData: {
    type: Object,
    required: true
  },
  riskTheme: {
    type: Object,
    required: true
  }
})

// Nilai yang dianimasikan secara halus
const displayRisk = ref(props.riskData?.risk_percentage ?? 0)
let animationFrameId = null

const animateValue = (start, end, duration = 350) => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }

  const startTime = performance.now()

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)

    // Kurva transisi Ease-out Cubic agar deselerasi angka terasa natural
    const easeProgress = 1 - Math.pow(1 - progress, 3)
    displayRisk.value = start + (end - start) * easeProgress

    if (progress < 1) {
      animationFrameId = requestAnimationFrame(step)
    } else {
      displayRisk.value = end
    }
  }

  animationFrameId = requestAnimationFrame(step)
}

// Pantau perubahan persentase risiko dari API
watch(
  () => props.riskData?.risk_percentage,
  (newVal, oldVal) => {
    const start = oldVal !== undefined ? oldVal : displayRisk.value
    const target = newVal !== undefined ? newVal : 0
    animateValue(start, target)
  }
)

onMounted(() => {
  displayRisk.value = props.riskData?.risk_percentage ?? 0
})

onBeforeUnmount(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
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

    <!-- Big Metric Value with Animated Counting -->
    <div class="flex items-baseline gap-2.5 my-2">
      <span :class="['text-4xl sm:text-5xl font-extrabold font-mono tracking-normal leading-normal py-1 inline-block bg-gradient-to-br bg-clip-text text-transparent tabular-nums', riskTheme.gradientText]">
        {{ Number(displayRisk).toFixed(2) }}%
      </span>
      <span class="text-xs font-medium text-slate-400 uppercase tracking-widest">Calculated Risk</span>
    </div>

    <!-- Progress Bar (Bergerak Selaras dengan Angka) -->
    <div class="relative w-full h-3 rounded-full bg-slate-950/80 p-0.5 border border-white/5 overflow-hidden mb-4 box-border">
      <div 
        :class="['h-full rounded-full bg-gradient-to-r transition-all duration-300 ease-out', riskTheme.bar]"
        :style="{ width: `${Math.min(Math.max(displayRisk, 0), 100)}%` }"
      />
    </div>

    <p class="text-xs text-slate-400 leading-relaxed border-t border-white/5 pt-3">
      {{ riskTheme.statusDesc }}
    </p>
  </div>
</template>