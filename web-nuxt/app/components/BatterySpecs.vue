<script setup>
import { computed } from 'vue'
import { Cpu, Layers, ThermometerSnowflake, Activity, Zap, ShieldCheck, AlertTriangle } from 'lucide-vue-next'

const props = defineProps({
  form: {
    type: Object,
    required: true
  },
  riskData: {
    type: Object,
    required: true
  }
})

// 1. Kalkulasi Estimasi Suhu Pack Baterai Berdasarkan Beban Nyata
const packTemperature = computed(() => {
  const baseTemp = 24.5
  const fastChargeHeat = props.form.fast_charge_ratio * 14.0 // Fast charge memicu panas tinggi
  const speedHeat = (props.form.average_speed / 120) * 6.5
  const brakeHeat = (props.form.hard_braking_score / 100) * 4.0

  const total = baseTemp + fastChargeHeat + speedHeat + brakeHeat
  return total.toFixed(1)
})

// 2. Estimasi Laju Konsumsi Daya Kendaraan (kWh/100km)
const powerConsumption = computed(() => {
  const baseConsumption = 12.8
  const speedPenalty = Math.pow(props.form.average_speed / 70, 1.6) * 4.2
  const brakingLoss = (props.form.hard_braking_score / 100) * 3.5

  return (baseConsumption + speedPenalty + brakingLoss).toFixed(1)
})

// 3. Status Thermal Baterai
const thermalStatus = computed(() => {
  const temp = parseFloat(packTemperature.value)
  if (temp >= 40) {
    return {
      label: 'Thermal Throttling Active',
      accent: 'text-rose-400',
      badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30'
    }
  }
  if (temp >= 33) {
    return {
      label: 'Elevated Operating Temp',
      accent: 'text-amber-400',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    }
  }
  return {
    label: 'Optimal Operating Window',
    accent: 'text-emerald-400',
    badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
  }
})

// 4. Status Proteksi BMS
const bmsStatus = computed(() => {
  const risk = props.riskData?.risk_percentage ?? 0
  if (risk >= 65) {
    return {
      text: 'Critical Stress Warning',
      badge: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      icon: AlertTriangle
    }
  }
  if (risk >= 35) {
    return {
      text: 'Mitigation Standby',
      badge: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      icon: AlertTriangle
    }
  }
  return {
    text: 'BMS Nominal',
    badge: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    icon: ShieldCheck
  }
})
</script>

<template>
  <div class="p-5 sm:p-6 rounded-3xl bg-slate-900/40 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4 box-border">
    
    <!-- Header Card -->
    <div class="flex items-center justify-between pb-3 border-b border-white/5">
      <div class="flex items-center gap-2">
        <Activity class="w-4 h-4 text-cyan-400 animate-pulse" />
        <h3 class="text-xs font-semibold tracking-wider uppercase text-slate-300">
          Hardware & Telemetry Architecture
        </h3>
      </div>
      <span :class="['inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono border transition-colors duration-300', bmsStatus.badge]">
        <component :is="bmsStatus.icon" class="w-3 h-3" />
        {{ bmsStatus.text }}
      </span>
    </div>

    <!-- Mini Bento Grid Specs -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      
      <!-- Pack Architecture (Fixed Base) -->
      <div class="p-3.5 rounded-2xl bg-slate-950/50 border border-white/5 hover:border-white/10 transition-colors space-y-1.5 box-border">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-medium text-slate-400 uppercase tracking-wide">
            Pack Architecture
          </span>
          <Layers class="w-4 h-4 text-cyan-400" />
        </div>
        <p class="text-sm font-bold text-white font-mono tracking-tight">
          800V High-Voltage
        </p>
        <p class="text-[11px] text-slate-400 truncate">
          77.4 kWh • NMC 811 Lithium-Ion
        </p>
      </div>

      <!-- Thermal Temperature (Dynamic) -->
      <div class="p-3.5 rounded-2xl bg-slate-950/50 border border-white/5 hover:border-white/10 transition-colors space-y-1.5 box-border">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-medium text-slate-400 uppercase tracking-wide">
            Thermal Operating Temp
          </span>
          <ThermometerSnowflake :class="['w-4 h-4 transition-colors duration-300', thermalStatus.accent]" />
        </div>
        <p :class="['text-sm font-bold font-mono tracking-tight transition-colors duration-300', thermalStatus.accent]">
          {{ packTemperature }}°C
        </p>
        <p class="text-[11px] text-slate-400 truncate">
          {{ thermalStatus.label }}
        </p>
      </div>

      <!-- Cell Configuration -->
      <div class="p-3.5 rounded-2xl bg-slate-950/50 border border-white/5 hover:border-white/10 transition-colors space-y-1.5 box-border">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-medium text-slate-400 uppercase tracking-wide">
            Cell Balancing
          </span>
          <Cpu class="w-4 h-4 text-indigo-400" />
        </div>
        <p class="text-sm font-bold text-white font-mono tracking-tight">
          192 Series (96s2p)
        </p>
        <p class="text-[11px] text-slate-400 truncate">
          Active Passive Shunt Active
        </p>
      </div>

      <!-- Energy Draw Rate (Dynamic) -->
      <div class="p-3.5 rounded-2xl bg-slate-950/50 border border-white/5 hover:border-white/10 transition-colors space-y-1.5 box-border">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-medium text-slate-400 uppercase tracking-wide">
            Est. Energy Draw
          </span>
          <Zap class="w-4 h-4 text-amber-400" />
        </div>
        <p class="text-sm font-bold text-white font-mono tracking-tight">
          {{ powerConsumption }} <span class="text-xs text-slate-400 font-sans">kWh/100km</span>
        </p>
        <p class="text-[11px] text-slate-400 truncate">
          Real-time dynamic discharge rate
        </p>
      </div>

    </div>

    <!-- Footer Status Tag -->
    <div class="pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
      <span>Firmware: VoltBMS-v2.4-Core</span>
      <span class="font-mono text-cyan-400">Inference Loop: Active</span>
    </div>

  </div>
</template>