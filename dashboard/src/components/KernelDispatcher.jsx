
import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Send, ChevronRight, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const DISPATCH_URL = 'http://localhost:8550/api/swarm/dispatch';

const KernelDispatcher = () => {
    const [input, setInput] = useState('');
    const [history, setHistory] = useState([
        { type: 'system', text: 'MR.VERMA Kernel Command Bridge v2.0 READY.' },
        { type: 'system', text: 'Swarm affinity: INTEL i9-13900H (14 Cores / 20 Threads)' }
    ]);
    const [executing, setExecuting] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history]);

    const handleCommand = async (e) => {
        e.preventDefault();
        const cmd = input.trim();
        if (!cmd || executing) return;

        setHistory(prev => [...prev, { type: 'user', text: cmd }]);
        setInput('');
        setExecuting(true);

        try {
            const res = await axios.post(DISPATCH_URL, { command: cmd });
            setHistory(prev => [...prev, {
                type: 'kernel',
                text: res.data.response || 'Command acknowledged. No output returned.',
                status: res.data.status
            }]);
        } catch (err) {
            setHistory(prev => [...prev, {
                type: 'error',
                text: err.response?.data?.error || 'Execution failed: Bridge timeout.'
            }]);
        } finally {
            setExecuting(false);
        }
    };

    return (
        <div className="glass-panel p-6 flex flex-column gap-4 h-full overflow-hidden border-sky-500/10">
            <div className="flex justify-between items-center pb-4 border-b border-white/5">
                <h3 className="text-lg font-bold flex items-center gap-2">
                    <Terminal className="text-sky-400" size={20} />
                    Swarm Dispatcher
                </h3>
                <div className="flex gap-2">
                    <span className="text-[10px] text-slate-500 font-mono">CHANNEL: C2-GLOBAL</span>
                    <div className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
                </div>
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto pr-2 custom-scrollbar font-mono text-[11px] flex flex-column gap-2"
            >
                <AnimatePresence initial={false}>
                    {history.map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -5 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`flex gap-3 p-2 rounded ${item.type === 'user' ? 'bg-white/5' : ''}`}
                        >
                            <span className={`shrink-0 font-bold ${item.type === 'system' ? 'text-slate-500' :
                                item.type === 'user' ? 'text-indigo-400' :
                                    item.type === 'error' ? 'text-red-400' : 'text-emerald-400'
                                }`}>
                                {item.type === 'user' ? 'USER &gt;' : 'KERN &gt;'}
                            </span>
                            <p className={`${item.type === 'error' ? 'italic' : ''} break-words`}>
                                {item.text}
                            </p>
                        </motion.div>
                    ))}
                </AnimatePresence>
                {executing && (
                    <div className="flex gap-3 p-2 animate-pulse">
                        <span className="text-sky-400 font-bold">KERN {' > '}</span>
                        <div className="flex gap-1 items-center">
                            <div className="w-1 h-1 bg-sky-400 rounded-full" />
                            <div className="w-1 h-1 bg-sky-400 rounded-full" />
                            <div className="w-1 h-1 bg-sky-400 rounded-full" />
                        </div>
                    </div>
                )}
            </div>

            <form onSubmit={handleCommand} className="relative mt-2">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-sky-500/50">
                    <ChevronRight size={16} />
                </div>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Dispatch command to swarm (e.g. /scan, /heal, /analyze)..."
                    className="w-full bg-slate-900/60 border border-white/10 rounded-xl py-3 pl-10 pr-12 text-[12px] font-mono focus:outline-none focus:border-sky-500/50 transition-all placeholder:text-slate-600"
                    disabled={executing}
                />
                <button
                    type="submit"
                    disabled={executing || !input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-400/20 flex items-center justify-center text-sky-400 hover:bg-sky-500/20 transition-all disabled:opacity-30"
                >
                    <Send size={14} />
                </button>
            </form>
        </div>
    );
};

export default KernelDispatcher;
