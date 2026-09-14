<script setup>
import { Gauge } from 'lucide-vue-next'

defineProps({
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
            @input="$emit('change')"
            class="custom-slider w-full h-2 rounded-lg appearance-none cursor-pointer focus:outline-none"
          />
        </div>

        <p class="text-xs sm:text-[12px] text-slate-300 leading-relaxed">
          {{ s.desc }}
        </p>
      </div>
    </div>

  </div>
</template>