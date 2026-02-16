
import React, { useState, useEffect } from 'react';
import { Terminal, Database, Cpu, Zap, ChevronRight, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const LOGS_URL = 'http://localhost:8550/api/system/logs';

const KernelLogs = ({ logs }) => {
    const [filter, setFilter] = useState('ALL');

    const filteredLogs = filter === 'ALL'
        ? logs
        : logs.filter(log => log.model?.toUpperCase() === filter.toUpperCase());

    const availableAgents = ['ALL', ...new Set(logs.map(log => log.model?.toUpperCase()).filter(Boolean))];

    return (
        <div className="flex flex-column gap-6 h-full overflow-hidden">
            <div className="glass-panel p-6 flex flex-column h-full overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        <Terminal className="text-sky-400" size={24} />
                        Intelligence Kernel Logs
                    </h3>
                    <div className="px-3 py-1 bg-sky-500/10 border border-sky-400/20 rounded-full text-[10px] text-sky-400 font-bold uppercase">
                        Live Stream Active
                    </div>
                </div>

                <div className="flex gap-2 overflow-x-auto pb-4 mb-2 no-scrollbar border-b border-white/5">
                    {availableAgents.map(agent => (
                        <button
                            key={agent}
                            onClick={() => setFilter(agent)}
                            className={`px-3 py-1 rounded-full text-[9px] font-bold uppercase transition-all whitespace-nowrap ${filter === agent
                                    ? 'bg-sky-500 text-white border-sky-400'
                                    : 'bg-white/5 text-slate-500 border-white/10 hover:bg-white/10'
                                } border`}
                        >
                            {agent}
                        </button>
                    ))}
                </div>

                <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                    <div className="flex flex-column gap-4">
                        <AnimatePresence initial={false} mode="popLayout">
                            {filteredLogs.map((log, i) => (
                                <LogEntry key={log.id || i} data={log} index={i} />
                            ))}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    );
};

const LogEntry = ({ data, index }) => {
    const lastUserMsg = data.messages?.filter(m => m.role === 'user').pop()?.content || "Unknown Query";

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-4 flex flex-column gap-3 font-mono text-[11px]"
        >
            <div className="flex justify-between items-center border-b border-white/5 pb-2">
                <div className="flex items-center gap-3">
                    <span className="text-sky-400 font-bold tracking-widest">{data.model?.toUpperCase()}</span>
                    <span className="text-slate-600">ID: {data.id?.slice(0, 8)}</span>
                </div>
                <div className="flex items-center gap-3 text-slate-500">
                    <span className="flex items-center gap-1"><Zap size={10} /> {data.latency_ms}ms</span>
                    <span>{new Date(data.timestamp * 1000).toLocaleTimeString()}</span>
                </div>
            </div>

            <div className="flex flex-column gap-2">
                <div className="flex gap-2">
                    <span className="text-indigo-400 shrink-0 select-none">USER &gt;</span>
                    <p className="text-slate-300 break-words line-clamp-1">{lastUserMsg}</p>
                </div>
                <div className="flex gap-2">
                    <span className="text-emerald-400 shrink-0 select-none">KERN &gt;</span>
                    <p className="text-slate-400 break-words line-clamp-2 italic">{data.response?.slice(0, 200)}...</p>
                </div>
            </div>

            <div className="flex justify-between items-center mt-1">
                <div className="flex gap-2">
                    {data.guards?.length > 0 ? (
                        <span className="px-1.5 py-0.5 bg-red-500/10 text-red-500 border border-red-500/20 rounded text-[9px] font-bold">HALLUCINATION DETECTED</span>
                    ) : (
                        <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded text-[9px] font-bold">QUALITY VERIFIED</span>
                    )}
                    <span className="px-1.5 py-0.5 bg-white/5 text-slate-500 border border-white/10 rounded text-[9px]">SFT READY</span>
                </div>
                <button className="text-[10px] text-sky-400 flex items-center gap-1 hover:underline">
                    Expand Trace <ChevronRight size={10} />
                </button>
            </div>
        </motion.div>
    );
};

export default KernelLogs;
