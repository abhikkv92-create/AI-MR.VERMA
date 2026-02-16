
import React, { useState, useEffect } from 'react';
import { Cpu, Zap, Activity, Database, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const TELEMETRY_URL = 'http://localhost:8550/api/hardware/telemetry';

const HardwareHUD = ({ telemetry, thermal }) => {
    // i9-13900H: 6 P-Cores (12 Threads) + 8 E-Cores (8 Threads) = 20 Logical Processors
    const cpuCores = telemetry.cpu_cores || [];
    const pCoreThreads = cpuCores.slice(0, 12);
    const eCoreThreads = cpuCores.slice(12, 20);

    return (
        <div className="flex flex-column gap-6 h-full overflow-hidden">
            <div className="grid grid-cols-2 gap-6">
                <div className="glass-panel p-6 flex items-center justify-between border-sky-500/10">
                    <div className="flex gap-4 items-center">
                        <div className="flex flex-column gap-1">
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em]">System Thermal</span>
                            <div className="flex items-center gap-2">
                                <Zap className={thermal?.is_throttled ? "text-amber-500 animate-pulse" : "text-sky-400"} size={16} />
                                <span className={`text-xl font-bold font-mono ${thermal?.is_throttled ? 'text-amber-400' : 'text-slate-100'}`}>
                                    {thermal?.sim_temp_c || 0}°C
                                </span>
                            </div>
                        </div>
                        {thermal?.is_throttled && (
                            <motion.div
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                className="bg-amber-500/20 border border-amber-500/40 rounded px-2 py-1 flex items-center gap-1"
                            >
                                <span className="text-[9px] text-amber-500 font-black animate-pulse">THROTTLED</span>
                            </motion.div>
                        )}
                    </div>
                </div>
                <div className="glass-panel p-6 flex flex-column gap-1 border-sky-500/10">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em]">Core Balance</span>
                    <div className="flex items-center gap-4">
                        <div className="flex flex-column gap-1 flex-1">
                            <div className="flex justify-between text-[9px] font-mono text-slate-400">
                                <span>P-CORE</span>
                                <span>{thermal?.p_core_load || 0}%</span>
                            </div>
                            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                <motion.div animate={{ width: `${thermal?.p_core_load || 0}%` }} className="h-full bg-sky-500/60" />
                            </div>
                        </div>
                        <div className="flex flex-column gap-1 flex-1">
                            <div className="flex justify-between text-[9px] font-mono text-slate-400">
                                <span>E-CORE</span>
                                <span>{thermal?.e_core_load || 0}%</span>
                            </div>
                            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                <motion.div animate={{ width: `${thermal?.e_core_load || 0}%` }} className="h-full bg-indigo-500/60" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
                <div className="glass-panel p-6 flex flex-column gap-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Cpu className="text-sky-400" size={20} />
                            P-Cores (Performance)
                        </h3>
                        <span className="text-xs font-mono text-slate-500 uppercase">Threads 0-11</span>
                    </div>
                    <div className="grid grid-cols-6 gap-3">
                        {pCoreThreads.map((load, i) => (
                            <CoreMonitor key={`p-${i}`} load={load} index={i} type="p" />
                        ))}
                    </div>
                </div>

                <div className="glass-panel p-6 flex flex-column gap-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Zap className="text-indigo-400" size={20} />
                            E-Cores (Efficiency)
                        </h3>
                        <span className="text-xs font-mono text-slate-500 uppercase">Threads 12-19</span>
                    </div>
                    <div className="grid grid-cols-4 gap-3">
                        {eCoreThreads.map((load, i) => (
                            <CoreMonitor key={`e-${i}`} load={load} index={i} type="e" />
                        ))}
                    </div>
                </div>
            </div>

            <div className="glass-panel p-6 flex-1 flex flex-column gap-6 overflow-hidden">
                <div className="flex justify-between items-center">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        <Activity className="text-sky-400" size={24} />
                        System Load Signature
                    </h3>
                    <div className="flex gap-4">
                        <StatPill label="Avg Load" value={`${telemetry.cpu_total}%`} />
                        <StatPill label="Memory" value={`${telemetry.ram_percent}%`} />
                    </div>
                </div>

                <div className="flex-1 flex items-end gap-1 px-4 py-8 bg-slate-900/40 rounded-xl border border-white/5 relative">
                    <div className="absolute top-2 left-4 text-[9px] text-slate-600 font-bold uppercase tracking-widest">
                        P-Core Pulse (Threads 0-11)
                    </div>
                    <div className="absolute top-2 right-4 text-[9px] text-slate-600 font-bold uppercase tracking-widest text-right">
                        E-Core Pulse (Threads 12-19)
                    </div>
                    <div className="absolute inset-x-0 top-0 h-full flex flex-column justify-between pointer-events-none p-4">
                        {[100, 75, 50, 25, 0].map(v => (
                            <div key={v} className="flex items-center gap-2 border-t border-white/5 w-full">
                                <span className="text-[10px] text-slate-600 font-mono w-4">{v}</span>
                            </div>
                        ))}
                    </div>
                    {telemetry.cpu_cores.map((load, i) => (
                        <motion.div
                            key={i}
                            initial={{ height: 0 }}
                            animate={{ height: `${load}%` }}
                            className={`flex-1 rounded-t-sm ${i < 12 ? 'bg-sky-500/40' : 'bg-indigo-500/40'} border-t-2 ${i < 12 ? 'border-sky-400' : 'border-indigo-400'} min-w-[4px]`}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

const CoreMonitor = ({ load, index, type }) => (
    <div className="flex flex-column gap-2">
        <div className="h-20 bg-slate-900/50 rounded-lg flex items-end overflow-hidden border border-white/5 p-1">
            <motion.div
                initial={{ height: 0 }}
                animate={{ height: `${load}%` }}
                className={`w-full rounded-sm ${type === 'p' ? 'bg-sky-500/60' : 'bg-indigo-500/60'} shadow-[0_0_10px_rgba(56,189,248,0.2)]`}
            />
        </div>
        <span className="text-[9px] text-center text-slate-500 font-mono">{index}</span>
    </div>
);

const StatPill = ({ label, value }) => (
    <div className="flex flex-column items-end">
        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{label}</span>
        <span className="text-sm font-bold font-mono text-sky-400">{value}</span>
    </div>
);

export default HardwareHUD;
