
import React, { useState, useEffect } from 'react';
import { Shield, Lock, Eye, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const EVENTS_URL = 'http://localhost:8550/api/security/events';

const SecurityOps = ({ security }) => {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const res = await axios.get(EVENTS_URL);
                setEvents(res.data);
            } catch (err) {
                console.error("Security fetch failed:", err);
            }
        };
        fetchEvents();
        const interval = setInterval(fetchEvents, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-column gap-6 h-full">
            <div className="grid grid-cols-3 gap-6">
                <SecurityStat icon={<Lock className="text-emerald-400" />} label="Encryption" value="AES-256-GCM" />
                <SecurityStat icon={<Shield className="text-sky-400" />} label="Integrity Status" value={security.status} />
                <SecurityStat icon={<Eye className={security.status !== 'SECURE' ? 'text-red-500 font-black' : 'text-amber-400'} />} label="Threat Level" value={security.status === 'SECURE' ? 'ZERO' : 'ELEVATED'} />
            </div>

            <div className="grid grid-cols-2 gap-6 flex-1 overflow-hidden">
                <div className="glass-panel p-6 flex flex-column overflow-hidden">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <Database className="text-sky-400" size={24} />
                        Core Integrity Threat Map
                    </h3>

                    <div className="grid grid-cols-2 gap-4 flex-1">
                        <ThreatZone name="Kernel Core" status={security.last_incident?.file.includes('core') ? 'MUTATED' : 'SECURE'} />
                        <ThreatZone name="Agent Cluster" status={security.last_incident?.file.includes('agents') ? 'MUTATED' : 'SECURE'} />
                        <ThreatZone name="Operational Scripts" status={security.last_incident?.file.includes('scripts') ? 'MUTATED' : 'SECURE'} />
                        <ThreatZone name="Env Context" status={security.last_incident?.file.includes('.env') ? 'MUTATED' : 'SECURE'} />
                    </div>

                    {security.last_incident && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl"
                        >
                            <p className="text-[10px] text-red-500 font-black uppercase mb-1">INCIDENT DETECTED</p>
                            <p className="text-xs font-mono text-slate-300 break-all">{security.last_incident.file}</p>
                        </motion.div>
                    )}
                </div>

                <div className="glass-panel p-6 flex flex-column overflow-hidden">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <Shield className="text-sky-400" size={24} />
                        Military-Grade Security Audit Log
                    </h3>

                    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                        <div className="flex flex-column gap-3">
                            <AnimatePresence>
                                {events.map((event, i) => (
                                    <SecurityEvent key={event.id} data={event} index={i} />
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const SecurityStat = ({ icon, label, value }) => (
    <div className="glass-panel p-4 flex items-center gap-4 border-sky-500/10 hover:border-sky-500/30 transition-all">
        <div className="w-10 h-10 bg-white/5 rounded-lg flex items-center justify-center">
            {icon}
        </div>
        <div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{label}</p>
            <p className="text-sm font-semibold">{value}</p>
        </div>
    </div>
);

const ThreatZone = ({ name, status }) => (
    <div className={`p-4 rounded-xl border flex flex-column justify-between gap-4 transition-all ${status === 'SECURE' ? 'border-white/5 bg-slate-900/40' : 'border-red-500/50 bg-red-500/10 shadow-[0_0_20px_rgba(239,68,68,0.1)]'}`}>
        <div className="flex justify-between items-start">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{name}</span>
            <div className={`w-1.5 h-1.5 rounded-full ${status === 'SECURE' ? 'bg-emerald-500' : 'bg-red-500 animate-pulse'}`} />
        </div>
        <div className="flex items-end justify-between">
            <span className={`text-[9px] font-black ${status === 'SECURE' ? 'text-emerald-500/50' : 'text-red-500'}`}>
                {status}
            </span>
            <Lock size={12} className={status === 'SECURE' ? 'text-slate-700' : 'text-red-500'} />
        </div>
    </div>
);

const SecurityEvent = ({ data, index }) => {
    const icons = {
        info: <Info size={16} className="text-sky-400" />,
        success: <CheckCircle size={16} className="text-emerald-400" />,
        warning: <AlertTriangle size={16} className="text-amber-400" />
    };

    const colors = {
        info: 'border-sky-500/10 bg-sky-500/5',
        success: 'border-emerald-500/10 bg-emerald-500/5',
        warning: 'border-amber-500/10 bg-amber-500/5'
    };

    return (
        <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`p-4 rounded-xl border flex items-start gap-4 ${colors[data.severity] || colors.info}`}
        >
            <div className="mt-0.5">{icons[data.severity] || icons.info}</div>
            <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{data.type}</span>
                    <span className="text-[10px] font-mono text-slate-600">{new Date(data.timestamp * 1000).toLocaleTimeString()}</span>
                </div>
                <p className="text-sm text-slate-300 font-medium">{data.message}</p>
            </div>
        </motion.div>
    );
};

export default SecurityOps;
