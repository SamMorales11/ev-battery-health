<script setup>
import { Zap, Sparkles } from 'lucide-vue-next'

defineProps({
  activePreset: {
    type: String,
    required: true
  },
  isOptimizing: {
    type: Boolean,
    default: false
  }
})

defineEmits(['selectPreset', 'optimize'])
</script>

<template>
  <header class="w-full flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl bg-slate-900/40 border border-white/10 backdrop-blur-xl shadow-2xl shadow-black/50 box-border">
    
    <!-- Brand / Identity -->
    <div class="flex items-center gap-3.5 min-w-0">
      <div class="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-400/20 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)] shrink-0">
        <Zap class="w-5 h-5" />
      </div>
      <div class="min-w-0">
        <div class="flex flex-wrap items-center gap-2.5">
          <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-white truncate">VoltIQ Telemetry</h1>
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
          @click="$emit('selectPreset', 'eco')" 
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
          @click="$emit('selectPreset', 'commuter')" 
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
          @click="$emit('selectPreset', 'aggressive')" 
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
        @click="$emit('optimize')"
        :disabled="isOptimizing"
        class="group relative inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl text-cyan-300 bg-cyan-950/40 hover:bg-cyan-900/40 border border-cyan-500/30 hover:border-cyan-400/60 shadow-[0_0_20px_rgba(6,182,212,0.15)] hover:shadow-[0_0_25px_rgba(6,182,212,0.3)] transition-all duration-300 disabled:opacity-40 cursor-pointer shrink-0 whitespace-nowrap active:scale-[0.98]"
      >
        <Sparkles class="w-3.5 h-3.5 text-cyan-400 transition-transform duration-300 group-hover:rotate-12" />
        <span>{{ isOptimizing ? 'Mengoptimalkan...' : 'Auto-Optimize' }}</span>
      </button>

    </div>
  </header>
</template>