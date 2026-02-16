import React, { useState, useEffect } from 'react';
import {
  Activity,
  Cpu,
  Database,
  ShieldCheck,
  Server,
  Terminal,
  Search,
  Zap,
  LayoutDashboard,
  ShieldAlert,
  Eye,
  Aperture,
  Network,
  CheckCircle2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import MemoryLens from './components/MemoryLens';
import SecurityOps from './components/SecurityOps';
import HardwareHUD from './components/HardwareHUD';
import KernelLogs from './components/KernelLogs';
import KernelDispatcher from './components/KernelDispatcher';
import TodoSwarm from './components/TodoSwarm';

const STREAM_URL = 'http://localhost:8550/api/stream';
const DISPATCH_URL = 'http://localhost:8550/api/swarm/dispatch';

const App = () => {
  const [activeView, setActiveView] = useState('swarm');
  const [visionActive, setVisionActive] = useState(false); // New Vision State
  const [telemetry, setTelemetry] = useState({
    cpu_total: 0,
    ram_percent: 0,
    ram_used_gb: 0,
    ram_total_gb: 0
  });
  const [swarm, setSwarm] = useState({
    active_agents: 27,
    task_queue: 0,
    status: 'OPERATIONAL'
  });
  const [logs, setLogs] = useState([]);
  const [thermal, setThermal] = useState({
    sim_temp_c: 35,
    is_throttled: false,
    p_core_load: 0,
    e_core_load: 0
  });
  const [security, setSecurity] = useState({
    status: 'SECURE',
    last_incident: null
  });

  useEffect(() => {
    const eventSource = new EventSource(STREAM_URL);

    eventSource.addEventListener('telemetry', (e) => {
      const data = JSON.parse(e.data);
      setTelemetry(data);
    });

    eventSource.addEventListener('kernel_log', (e) => {
      const data = JSON.parse(e.data);
      setLogs(prev => [data, ...prev].slice(0, 50));

      // Simulate Vision Activation detection from logs (since we don't have a direct stream yet)
      if (data.message && data.message.includes("Visual Content Detected")) {
        setVisionActive(true);
        setTimeout(() => setVisionActive(false), 5000);
      }
    });

    eventSource.addEventListener('thermal_status', (e) => {
      setThermal(JSON.parse(e.data));
    });

    eventSource.addEventListener('security_status', (e) => {
      setSecurity(JSON.parse(e.data));
    });

    eventSource.onerror = (err) => {
      console.error("SSE Connection Error:", err);
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  return (
    <div className="dashboard-container">
      {/* Neon Sidebar */}
      <aside className="sidebar">
        <div className="mb-8 p-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-400/30 flex items-center justify-center neon-border">
            <Zap className="text-cyan-400" size={20} />
          </div>
        </div>

        <nav className="flex flex-col gap-6 w-full px-2">
          <NavIcon icon={<LayoutDashboard size={20} />} active={activeView === 'swarm'} onClick={() => setActiveView('swarm')} tooltip="Swarm" />
          <NavIcon icon={<Database size={20} />} active={activeView === 'memory'} onClick={() => setActiveView('memory')} tooltip="Memory" />
          <NavIcon icon={<Activity size={20} />} active={activeView === 'hardware'} onClick={() => setActiveView('hardware')} tooltip="Hardware" />
          <NavIcon icon={<ShieldCheck size={20} />} active={activeView === 'security'} onClick={() => setActiveView('security')} tooltip="Security" />
          <NavIcon icon={<Terminal size={20} />} active={activeView === 'kernel'} onClick={() => setActiveView('kernel')} tooltip="Logs" />
          <div className="w-full h-px bg-white/5 my-2" />
          <NavIcon icon={<CheckCircle2 size={20} />} active={activeView === 'todo'} onClick={() => setActiveView('todo')} tooltip="Todo Matrix" />
        </nav>

        <div className="mt-auto mb-6 flex flex-col gap-4 items-center">
          {/* Vision Status Indicator */}
          <motion.div
            animate={{ opacity: visionActive ? 1 : 0.3, scale: visionActive ? 1.1 : 1 }}
            className={`w-8 h-8 rounded-full flex items-center justify-center ${visionActive ? 'bg-pink-500/20 border border-pink-500 shadow-[0_0_15px_rgba(244,114,182,0.5)]' : 'bg-slate-800/50'}`}
          >
            <Eye size={16} className={visionActive ? 'text-pink-400' : 'text-slate-600'} />
          </motion.div>

          <div className="w-1 h-12 bg-slate-800 rounded-full overflow-hidden relative">
            <motion.div
              className="absolute bottom-0 w-full bg-cyan-400"
              animate={{ height: `${telemetry.cpu_total}%` }}
              transition={{ type: "spring", stiffness: 100 }}
            />
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content scanline">

        {/* Header HUD */}
        <header className="flex justify-between items-end border-b border-white/5 pb-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-1">
              MR.<span className="text-cyan-400">VERMA</span>
            </h1>
            <div className="flex items-center gap-3 text-sm text-slate-400 font-mono">
              <span className="flex items-center gap-1.5">
                <div className={`w-2 h-2 rounded-full ${swarm.status === 'OPERATIONAL' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`}></div>
                SYSTEM ONLINE
              </span>
              <span className="opacity-30">|</span>
              <span>KERNEL v2.5.0</span>
            </div>
          </div>

          <div className="flex gap-4">
            <div className={`glass-card px-4 py-2 flex items-center gap-3 ${security.status !== 'SECURE' ? 'border-red-500/50 bg-red-900/10' : ''}`}>
              <ShieldCheck size={16} className={security.status === 'SECURE' ? 'text-emerald-400' : 'text-red-500'} />
              <div className="flex flex-col">
                <span className="text-[10px] uppercase tracking-wider text-slate-500">Security</span>
                <span className={`text-sm font-bold font-mono ${security.status === 'SECURE' ? 'text-emerald-400' : 'text-red-400'}`}>{security.status}</span>
              </div>
            </div>

            <div className="glass-card px-4 py-2 flex items-center gap-3">
              <Cpu size={16} className="text-cyan-400" />
              <div className="flex flex-col">
                <span className="text-[10px] uppercase tracking-wider text-slate-500">Processing</span>
                <span className="text-sm font-bold font-mono text-cyan-400">{telemetry.cpu_total}%</span>
              </div>
            </div>
          </div>
        </header>

        {/* View Content */}
        <div className="flex-1 relative">
          <AnimatePresence mode="wait">
            {activeView === 'swarm' && (
              <motion.div
                key="swarm"
                initial={{ opacity: 0, filter: 'blur(10px)' }}
                animate={{ opacity: 1, filter: 'blur(0px)' }}
                exit={{ opacity: 0, filter: 'blur(10px)' }}
                transition={{ duration: 0.3 }}
                className="grid-dashboard h-full"
              >
                {/* Stats Row */}
                <div className="col-span-12 grid grid-cols-4 gap-6 mb-2">
                  <StatBlock label="Active Agents" value={swarm.active_agents} icon={<Network className="text-purple-400" />} />
                  <StatBlock label="Task Queue" value={swarm.task_queue} icon={<LayoutDashboard className="text-amber-400" />} />
                  <StatBlock label="Memory Usage" value={`${telemetry.ram_used_gb} GB`} sub={`/ ${telemetry.ram_total_gb} GB`} icon={<Database className="text-emerald-400" />} />
                  <StatBlock label="Vision Engine" value={visionActive ? "ANALYZING" : "STANDBY"} icon={<Eye className={visionActive ? "text-pink-500 animate-pulse" : "text-slate-500"} />} />
                </div>

                {/* Swarm Grid */}
                <div className="col-span-8 glass-panel p-6 flex flex-col h-[600px]">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-6 flex items-center gap-2">
                    <Aperture size={16} /> Neural Swarm Matrix
                  </h3>
                  <div className="grid grid-cols-5 gap-3 overflow-y-auto pr-2 custom-scrollbar content-start">
                    {[...Array(27)].map((_, i) => (
                      <AgentNode key={i} id={i + 1} />
                    ))}
                  </div>
                </div>

                {/* Dispatcher / Command */}
                <div className="col-span-4 flex flex-col gap-6">
                  <div className="glass-panel p-6 flex-1">
                    <KernelDispatcher />
                  </div>
                </div>
              </motion.div>
            )}

            {activeView === 'memory' && (
              <motion.div key="memory" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <MemoryLens />
              </motion.div>
            )}
            {activeView === 'hardware' && (
              <motion.div key="hardware" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <HardwareHUD telemetry={telemetry} thermal={thermal} />
              </motion.div>
            )}
            {activeView === 'security' && (
              <motion.div key="security" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <SecurityOps security={security} />
              </motion.div>
            )}
            {activeView === 'kernel' && (
              <motion.div key="kernel" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <KernelLogs logs={logs} />
              </motion.div>
            )}
            {activeView === 'todo' && (
              <motion.div key="todo" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.98 }} transition={{ duration: 0.2 }} className="h-full">
                <TodoSwarm />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

// --- Sub-Components ---

const NavIcon = ({ icon, active, onClick, tooltip }) => (
  <div className="relative group flex justify-center">
    <button
      onClick={onClick}
      className={`p-3 rounded-xl transition-all duration-300 ${active
        ? 'bg-cyan-500/10 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]'
        : 'text-slate-500 hover:text-slate-200 hover:bg-white/5'
        }`}
    >
      {icon}
    </button>
    {/* Tooltip */}
    <div className="absolute left-full ml-4 top-1/2 -translate-y-1/2 px-2 py-1 bg-slate-900 border border-white/10 rounded text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
      {tooltip}
    </div>
    {/* Active Indicator */}
    {active && (
      <motion.div layoutId="nav-pill" className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-cyan-400 rounded-r-full" />
    )}
  </div>
);

const StatBlock = ({ label, value, sub, icon }) => (
  <div className="glass-card p-4 flex items-center gap-4 relative overflow-hidden group">
    <div className="w-12 h-12 rounded-lg bg-slate-900/50 flex items-center justify-center border border-white/5 group-hover:border-white/10 transition-colors">
      {icon}
    </div>
    <div>
      <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-0.5">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className="text-xl font-bold font-mono text-white">{value}</span>
        {sub && <span className="text-xs text-slate-500 font-mono">{sub}</span>}
      </div>
    </div>
  </div>
);

const AgentNode = ({ id }) => {
  const status = Math.random() > 0.2 ? 'online' : 'busy';
  const isOnline = status === 'online';

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`relative aspect-square rounded-xl border flex flex-col items-center justify-center gap-2 transition-all duration-300 cursor-pointer ${isOnline
        ? 'bg-cyan-900/10 border-cyan-500/20 hover:border-cyan-400/50 hover:bg-cyan-900/20'
        : 'bg-slate-800/20 border-white/5 hover:border-white/10'
        }`}
    >
      <div className={`w-2 h-2 rounded-full absolute top-2 right-2 ${isOnline ? 'bg-cyan-400 shadow-[0_0_8px_cyan]' : 'bg-amber-500'}`} />
      <span className="text-xs font-mono font-bold text-slate-400">A-{id}</span>
      <div className="w-full px-2 flex gap-0.5 justify-center h-0.5">
        <div className={`w-1 h-full rounded-full ${isOnline ? 'bg-cyan-500/50' : 'bg-slate-600'}`} />
        <div className={`w-1 h-full rounded-full ${isOnline ? 'bg-cyan-500/30' : 'bg-slate-700'}`} />
      </div>
    </motion.div>
  );
};

export default App;
