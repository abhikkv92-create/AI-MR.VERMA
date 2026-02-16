import React, { useState, useEffect, useRef } from 'react';
import {
    Plus,
    Search,
    Settings,
    Trash2,
    CheckCircle2,
    Calendar,
    AlertCircle,
    CloudRain,
    Sun,
    Wind,
    Image as ImageIcon,
    Loader2,
    Sparkles,
    ChevronRight,
    Zap,
    Layers,
    Target,
    Cpu,
    RefreshCcw,
    X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const TODO_API = 'http://localhost:8550/api/swarm/todo';

const TodoSwarm = () => {
    const [tasks, setTasks] = useState([]);
    const [input, setInput] = useState('');
    const [weather, setWeather] = useState(null);
    const [isArchitectMode, setIsArchitectMode] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [activeTab, setActiveTab] = useState('active'); // active, completed
    const scrollRef = useRef(null);

    // Fetch Weather on Mount
    useEffect(() => {
        const fetchWeather = async () => {
            try {
                const resp = await axios.get(`${TODO_API}/weather?location=London`);
                setWeather(resp.data);
            } catch (err) {
                console.error("Weather fetch failed", err);
            }
        };
        fetchWeather();
    }, []);

    const handleAction = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim()) return;

        setIsProcessing(true);
        try {
            const endpoint = isArchitectMode ? 'architect' : 'analyze';
            const payload = isArchitectMode ? { goal: input } : { text: input };

            const resp = await axios.post(`${TODO_API}/${endpoint}`, payload);

            const newTasks = resp.data.map(t => ({
                id: Math.random().toString(36).substr(2, 9),
                title: t.title,
                priority: t.priority || 'medium',
                category: t.category || (isArchitectMode ? 'Architecture' : 'General'),
                due_date: t.due_date || 'Neural Priority',
                completed: false,
                timestamp: Date.now()
            }));

            setTasks(prev => [...newTasks, ...prev]);
            setInput('');
            if (isArchitectMode) setIsArchitectMode(false);
        } catch (err) {
            console.error("Operation failed", err);
            // Fallback
            if (!isArchitectMode) {
                setTasks(prev => [{
                    id: Date.now(),
                    title: input,
                    priority: 'medium',
                    category: 'Manual',
                    completed: false
                }, ...prev]);
            }
        } finally {
            setIsProcessing(false);
        }
    };

    const handleVisionUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsProcessing(true);
        const reader = new FileReader();
        reader.onloadend = async () => {
            const base64 = reader.result.split(',')[1];
            try {
                const resp = await axios.post(`${TODO_API}/vision`, { image: base64 });
                const extractResp = await axios.post(`${TODO_API}/analyze`, { text: resp.data.transcription });
                const newTasks = extractResp.data.map(t => ({
                    id: Math.random().toString(36).substr(2, 9),
                    title: t.title,
                    priority: t.priority || 'medium',
                    category: 'Vision Scan',
                    due_date: 'Neural Priority',
                    completed: false,
                    timestamp: Date.now()
                }));
                setTasks(prev => [...newTasks, ...prev]);
            } catch (err) {
                console.error("Vision operation failed", err);
            } finally {
                setIsProcessing(false);
            }
        };
        reader.readAsDataURL(file);
    };

    const toggleTask = (id) => {
        setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
    };

    const deleteTask = (id) => {
        setTasks(tasks.filter(t => t.id !== id));
    };

    const filteredTasks = tasks.filter(t => activeTab === 'active' ? !t.completed : t.completed);

    return (
        <div className="flex flex-col h-full gap-6 animate-in fade-in duration-700">
            {/* Supreme HUD */}
            <div className="flex justify-between items-center glass-panel p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 blur-[100px] -mr-32 -mt-32 pointer-events-none" />
                <div className="flex items-center gap-6 relative z-10">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 p-px flex items-center justify-center shadow-[0_0_30px_rgba(6,182,212,0.3)]">
                        <div className="w-full h-full rounded-2xl bg-slate-950 flex items-center justify-center">
                            <Zap className="text-cyan-400 fill-cyan-400/20" size={32} />
                        </div>
                    </div>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-3xl font-bold text-white tracking-tight uppercase">Todo <span className="text-cyan-400">Matrix</span></h1>
                            <div className="px-2 py-0.5 rounded-full bg-cyan-400/10 border border-cyan-400/20 text-[10px] text-cyan-400 font-bold uppercase tracking-widest">Supreme V2.5</div>
                        </div>
                        <p className="text-sm text-slate-500 font-mono tracking-widest mt-1">ORCHESTRATING {tasks.length} NEURAL ENTITIES</p>
                    </div>
                </div>

                {weather && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex items-center gap-8 relative z-10 bg-white/5 px-6 py-3 rounded-2xl border border-white/10 backdrop-blur-md"
                    >
                        <div className="flex flex-col items-end border-r border-white/10 pr-6">
                            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-tighter mb-1 font-mono">Environment Status</span>
                            <div className="flex items-center gap-2">
                                <span className="text-2xl font-bold text-white font-mono">{weather.temp}°C</span>
                                <span className={`text-xs font-bold uppercase ${weather.condition.includes('Sun') ? 'text-amber-400' : 'text-cyan-400'}`}>{weather.condition}</span>
                            </div>
                        </div>
                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-3xl ${weather.condition.includes('Sun') ? 'bg-amber-500/10 text-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.2)]' : 'bg-cyan-500/10 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.2)]'}`}>
                            {weather.condition.includes('Sun') ? <Sun size={32} /> : <CloudRain size={32} />}
                        </div>
                    </motion.div>
                )}
            </div>

            <div className="grid grid-cols-12 gap-8 flex-1 min-h-0">
                {/* Main Interface */}
                <div className="col-span-9 flex flex-col gap-6 h-full">
                    {/* Dispatch Logic Block */}
                    <div className={`relative transition-all duration-500 ${isArchitectMode ? 'scale-[1.02]' : 'scale-100'}`}>
                        <AnimatePresence>
                            {isArchitectMode && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 10 }}
                                    className="absolute -top-10 left-0 text-[10px] font-bold uppercase tracking-widest text-purple-400 flex items-center gap-2"
                                >
                                    <Layers size={12} /> ARCHITECT MODE: DESIGNING GLOBAL PLAN
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <form onSubmit={handleAction} className="relative group">
                            <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${isArchitectMode ? 'from-purple-500/20 to-indigo-500/20' : 'from-cyan-500/10 to-transparent'} blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none`} />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={isArchitectMode ? "Describe your supreme goal... (e.g., Build a Mars colonization plan)" : "Synchronize new task with the swarm..."}
                                className={`w-full bg-slate-900/40 border ${isArchitectMode ? 'border-purple-500/30' : 'border-white/5'} rounded-2xl py-6 px-8 text-white placeholder-slate-600 focus:outline-none focus:ring-2 ${isArchitectMode ? 'focus:ring-purple-500/30 focus:border-purple-500/50' : 'focus:ring-cyan-500/20 focus:border-cyan-500/40'} transition-all text-xl backdrop-blur-xl shadow-2xl relative z-10`}
                            />

                            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-3 z-10">
                                <button
                                    type="button"
                                    onClick={() => setIsArchitectMode(!isArchitectMode)}
                                    className={`p-3 rounded-xl transition-all ${isArchitectMode ? 'bg-purple-500 text-white shadow-lg' : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'}`}
                                    title="Toggle Architect Mode"
                                >
                                    <Layers size={20} />
                                </button>
                                <div className="w-px h-8 bg-white/5 mx-1" />
                                <button
                                    type="submit"
                                    disabled={isProcessing}
                                    className={`w-14 h-14 rounded-xl flex items-center justify-center transition-all shadow-2xl active:scale-95 disabled:opacity-50 ${isArchitectMode ? 'bg-purple-600 hover:bg-purple-500 text-white shadow-purple-500/20' : 'bg-cyan-500 hover:bg-cyan-400 text-slate-900 shadow-cyan-500/20'}`}
                                >
                                    {isProcessing ? <Loader2 className="animate-spin" size={24} /> : (isArchitectMode ? <Sparkles size={24} /> : <Plus size={28} />)}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Matrix Repository */}
                    <div className="flex-1 glass-panel flex flex-col overflow-hidden">
                        <div className="px-8 py-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                            <div className="flex gap-8">
                                <button
                                    onClick={() => setActiveTab('active')}
                                    className={`text-xs font-bold uppercase tracking-widest pb-2 transition-all border-b-2 ${activeTab === 'active' ? 'text-cyan-400 border-cyan-400 shadow-[0_8px_15px_-5px_rgba(6,182,212,0.4)]' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
                                >
                                    Active <span className="ml-1 opacity-50">{tasks.filter(t => !t.completed).length}</span>
                                </button>
                                <button
                                    onClick={() => setActiveTab('completed')}
                                    className={`text-xs font-bold uppercase tracking-widest pb-2 transition-all border-b-2 ${activeTab === 'completed' ? 'text-cyan-400 border-cyan-400 shadow-[0_8px_15px_-5px_rgba(6,182,212,0.4)]' : 'text-slate-500 border-transparent hover:text-slate-300'}`}
                                >
                                    Completed <span className="ml-1 opacity-50">{tasks.filter(t => t.completed).length}</span>
                                </button>
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest bg-white/5 px-3 py-1.5 rounded-lg">Sort: Neural Hash</div>
                                <label className={`cursor-pointer w-10 h-10 rounded-xl flex items-center justify-center transition-all ${isProcessing ? 'bg-pink-500/20 animate-pulse' : 'bg-white/5 hover:bg-white/10 hover:border hover:border-white/10'}`}>
                                    <input type="file" accept="image/*" className="hidden" onChange={handleVisionUpload} />
                                    <ImageIcon size={18} className={isProcessing ? "text-pink-400" : "text-slate-400"} />
                                </label>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto custom-scrollbar p-8 space-y-4" ref={scrollRef}>
                            <AnimatePresence mode="popLayout">
                                {filteredTasks.length === 0 && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="h-full flex flex-col items-center justify-center text-slate-700 space-y-6"
                                    >
                                        <div className="w-24 h-24 rounded-full border border-slate-800 flex items-center justify-center relative">
                                            <div className="absolute inset-0 rounded-full border border-cyan-400/20 animate-ping opacity-20" />
                                            <Target size={48} className="opacity-20" />
                                        </div>
                                        <div className="text-center">
                                            <p className="font-mono text-sm tracking-[0.3em] uppercase mb-2">Matrix Standby</p>
                                            <p className="text-xs text-slate-600">No active neural nodes detected in this sector.</p>
                                        </div>
                                    </motion.div>
                                )}
                                {filteredTasks.map((task, idx) => (
                                    <motion.div
                                        key={task.id}
                                        layout
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, scale: 0.95 }}
                                        transition={{ delay: idx * 0.05 }}
                                        className={`group glass-card p-5 flex items-center gap-6 border border-white/5 hover:border-cyan-500/30 relative overflow-hidden ${task.completed ? 'opacity-40 grayscale-[0.5]' : ''}`}
                                    >
                                        <div className={`absolute top-0 left-0 w-1 h-full ${task.priority === 'high' ? 'bg-red-500' :
                                                task.priority === 'medium' ? 'bg-amber-500' : 'bg-emerald-500'
                                            } opacity-50 group-hover:opacity-100 transition-opacity`} />

                                        <button
                                            onClick={() => toggleTask(task.id)}
                                            className={`w-7 h-7 rounded-xl border flex items-center justify-center transition-all ${task.completed ? 'bg-cyan-500 border-cyan-500 text-slate-950' : 'border-slate-700 hover:border-cyan-500/50 bg-white/5'}`}
                                        >
                                            {task.completed && <CheckCircle2 size={16} strokeWidth={3} />}
                                        </button>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-3 mb-1">
                                                <span className="text-[10px] font-mono text-slate-600">#{task.id}</span>
                                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded">{task.category}</span>
                                            </div>
                                            <h4 className={`text-lg font-medium tracking-tight text-white transition-all ${task.completed ? 'line-through text-slate-500 font-normal' : ''}`}>
                                                {task.title}
                                            </h4>
                                        </div>

                                        <div className="flex flex-col items-end gap-2 pr-2">
                                            <div className="flex gap-2 items-center">
                                                <span className={`text-[9px] font-bold px-2 py-1 rounded-lg uppercase tracking-wider ${task.priority === 'high' ? 'bg-red-500/10 text-red-500 border border-red-500/20' :
                                                        task.priority === 'medium' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
                                                            'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                                                    }`}>
                                                    {task.priority}
                                                </span>
                                                <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1.5 bg-white/5 px-2 py-1 rounded-lg border border-white/5">
                                                    <Calendar size={12} className="text-cyan-400" /> {task.due_date}
                                                </span>
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => deleteTask(task.id)}
                                            className="p-3 text-slate-600 hover:text-red-400 hover:bg-red-400/10 border border-transparent hover:border-red-400/20 rounded-xl transition-all"
                                        >
                                            <Trash2 size={20} />
                                        </button>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>

                {/* Intelligence Sidebar */}
                <div className="col-span-3 flex flex-col gap-8">
                    <div className="glass-panel p-8 bg-gradient-to-b from-cyan-500/[0.08] to-transparent border-cyan-500/20">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 rounded-xl bg-cyan-400/20 flex items-center justify-center">
                                <Wind className="text-cyan-400" size={20} />
                            </div>
                            <h3 className="text-xs font-bold uppercase tracking-widest text-white">Neural Insights</h3>
                        </div>
                        <p className="text-sm text-slate-300 leading-relaxed font-mono italic mb-6">
                            "{weather?.recommendation || "Synchronizing with environmental variables. Neural clusters standby..."}"
                        </p>
                        <div className="flex items-center gap-2 text-[10px] text-cyan-400/60 font-mono uppercase tracking-[0.2em]">
                            <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                            Source: Secondary Engine
                        </div>
                    </div>

                    <div className="glass-panel p-8 flex-1 flex flex-col relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-px h-full bg-gradient-to-b from-white/10 to-transparent" />
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400">
                                <Cpu size={20} />
                            </div>
                            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Telemetry Feed</h3>
                        </div>

                        <div className="space-y-6 flex-1 overflow-y-auto custom-scrollbar pr-2">
                            <TelemetryItem label="Matrix Uplink" value="ESTABLISHED" color="text-emerald-400" />
                            <TelemetryItem label="Node Stability" value="99.98%" color="text-cyan-400" />
                            <TelemetryItem label="Thermal State" value="OPTIMIZED" color="text-emerald-400" />
                            <TelemetryItem label="Neural Load" value="12.4% / 100" color="text-amber-400" />
                            <TelemetryItem label="Sync Cycles" value="8,124" color="text-purple-400" />
                        </div>

                        <div className="mt-8 pt-8 border-t border-white/5">
                            <button
                                onClick={() => setTasks([])}
                                className="w-full flex items-center justify-between text-[10px] uppercase font-bold text-slate-500 hover:text-red-400 font-mono tracking-widest group transition-all"
                            >
                                <span>Reset Matrix Sector</span>
                                <RefreshCcw size={14} className="group-hover:rotate-180 transition-all duration-500" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const TelemetryItem = ({ label, value, color }) => (
    <div className="flex flex-col gap-2">
        <div className="flex justify-between items-end">
            <span className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">{label}</span>
            <span className={`text-[10px] font-bold font-mono tracking-tight ${color}`}>{value}</span>
        </div>
        <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 1, ease: "easeOut" }}
                className={`h-full opacity-30 ${color.replace('text', 'bg')}`}
            />
        </div>
    </div>
);

export default TodoSwarm;
