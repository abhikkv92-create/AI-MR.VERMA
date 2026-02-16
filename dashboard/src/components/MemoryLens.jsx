
import React, { useState } from 'react';
import { Search, Loader2, Database, Clock, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const SEARCH_URL = 'http://localhost:8550/api/memory/search';

const MemoryLens = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedResult, setSelectedResult] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const res = await axios.get(`${SEARCH_URL}?q=${encodeURIComponent(query)}`);
            setResults(res.data);
        } catch (err) {
            console.error("Search failed:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-column gap-6 h-full">
            <div className="glass-panel p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Database className="text-sky-400" size={24} />
                    Semantic Memory Lens
                </h3>
                <p className="text-sm text-slate-400 mb-6">
                    Query the MR.VERMA 2.0 long-term memory using natural language.
                    Powered by NVIDIA Embeddings and Milvus Vector Store.
                </p>

                <form onSubmit={handleSearch} className="relative">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search across 1.5M lines of project knowledge..."
                        className="w-full bg-slate-900/50 border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-sky-500/50 transition-all font-medium"
                    />
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                    <button
                        type="submit"
                        disabled={loading}
                        className="absolute right-3 top-1/2 -translate-y-1/2 bg-sky-500 hover:bg-sky-400 text-white px-4 py-2 rounded-lg font-bold text-sm transition-all flex items-center gap-2"
                    >
                        {loading ? <Loader2 className="animate-spin" size={16} /> : "Query Swarm"}
                    </button>
                </form>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                <AnimatePresence mode='wait'>
                    {results.length > 0 ? (
                        <motion.div
                            key="results"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-column gap-4"
                        >
                            {results.map((res, i) => (
                                <MemoryCard
                                    key={i}
                                    data={res}
                                    index={i}
                                    onClick={() => setSelectedResult(res)}
                                />
                            ))}
                        </motion.div>
                    ) : !loading && (
                        <motion.div
                            key="empty"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-column items-center justify-center py-20 text-slate-500"
                        >
                            <Database size={48} className="mb-4 opacity-20" />
                            <p>Enter a query to recall project history...</p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <AnimatePresence>
                {selectedResult && (
                    <DeepViewModal
                        data={selectedResult}
                        onClose={() => setSelectedResult(null)}
                    />
                )}
            </AnimatePresence>
        </div>
    );
};

const MemoryCard = ({ data, index, onClick }) => (
    <motion.div
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: index * 0.05 }}
        onClick={onClick}
        className="glass-card p-5 group cursor-pointer hover:border-sky-500/30 transition-all"
    >
        <div className="flex justify-between items-start mb-3">
            <div className="flex items-center gap-2">
                <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest ${data.role === 'user' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {data.role}
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-500 font-mono">
                    <Clock size={10} />
                    {new Date(data.timestamp * 1000).toLocaleDateString()}
                </div>
            </div>
            <div className="text-[10px] text-sky-500 font-mono font-bold">
                REL-{(1 - data.distance).toFixed(4)}
            </div>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed line-clamp-3">
            {data.content}
        </p>
        <div className="flex justify-end mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button className="text-sky-400 text-xs font-bold flex items-center">
                Deep Recall Context <ChevronRight size={14} />
            </button>
        </div>
    </motion.div>
);

const DeepViewModal = ({ data, onClose }) => (
    <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-8 bg-slate-950/80 backdrop-blur-md"
        onClick={onClose}
    >
        <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="glass-panel w-full max-w-4xl max-h-[80vh] flex flex-column overflow-hidden border-sky-500/20"
            onClick={e => e.stopPropagation()}
        >
            <div className="p-6 border-b border-white/10 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Database className="text-sky-400" size={24} />
                    <h3 className="text-xl font-bold">Memory Trace Reconstruction</h3>
                </div>
                <button
                    onClick={onClose}
                    className="w-10 h-10 rounded-full hover:bg-white/5 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
                >
                    ✕
                </button>
            </div>
            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                <div className="flex flex-column gap-6">
                    <div className="flex gap-6 border-b border-white/5 pb-6">
                        <div className="flex flex-column gap-1">
                            <span className="text-[10px] text-slate-500 font-bold uppercase">Role</span>
                            <span className={`text-sm font-bold ${data.role === 'user' ? 'text-indigo-400' : 'text-emerald-400'}`}>{data.role?.toUpperCase()}</span>
                        </div>
                        <div className="flex flex-column gap-1">
                            <span className="text-[10px] text-slate-500 font-bold uppercase">Timestamp</span>
                            <span className="text-sm font-mono text-slate-300">{new Date(data.timestamp * 1000).toLocaleString()}</span>
                        </div>
                        <div className="flex flex-column gap-1">
                            <span className="text-[10px] text-slate-500 font-bold uppercase">Vector Distance</span>
                            <span className="text-sm font-mono text-sky-400">{data.distance?.toFixed(6)}</span>
                        </div>
                    </div>
                    <div>
                        <span className="text-[10px] text-slate-500 font-bold uppercase mb-4 block">Reconstructed Content</span>
                        <div className="bg-slate-900/50 p-6 rounded-xl border border-white/5 font-mono text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">
                            {data.content}
                        </div>
                    </div>
                </div>
            </div>
            <div className="p-6 border-t border-white/10 flex justify-between items-center bg-sky-500/5">
                <span className="text-xs text-slate-500 italic">Semantic memory fragments are retrieved using long-term synaptic anchoring.</span>
                <button
                    onClick={onClose}
                    className="px-6 py-2 bg-sky-500 hover:bg-sky-400 text-white rounded-lg font-bold text-sm transition-all"
                >
                    Close Trace
                </button>
            </div>
        </motion.div>
    </motion.div>
);

export default MemoryLens;
