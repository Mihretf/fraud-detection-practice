import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldAlert, Activity, DollarSign, Zap, Clock } from 'lucide-react';

const App = () => {
  // Initialize with default structure so the UI doesn't crash or hang on "null"
  const [stats, setStats] = useState({
    summary: { total_volume: 0, fraud_rate: "0%", fraud_count: 0 },
    recent_fraud: []
  });
  const [batchData, setBatchData] = useState([]);

  const fetchData = async () => {
    try {
      // Fetching from your FastAPI endpoints
      const sRes = await axios.get('http://localhost:8000/api/stats');
      const bRes = await axios.get('http://localhost:8000/api/batch-report');
      
      if (sRes.data) setStats(sRes.data);
      if (bRes.data.alerts) setBatchData(bRes.data.alerts);
      
    } catch (err) { 
      console.error("Pipeline Sync Error (Check if FastAPI is running):", err); 
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // 3-second heartbeat
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-black tracking-tighter text-white flex items-center gap-2">
            <ShieldAlert className="text-red-500" /> FRAUD RADAR <span className="text-blue-500">v2.0</span>
          </h1>
          <p className="text-slate-500 text-xs font-mono uppercase tracking-widest">
            Hybrid Lambda Architecture (Stream + Batch)
          </p>
        </div>
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-2 text-xs font-mono bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> 
              HDFS STATUS: CONNECTED
           </div>
        </div>
      </header>

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Volume', val: `$${stats.summary.total_volume.toLocaleString()}`, icon: <DollarSign size={16}/>, color: 'text-emerald-400' },
          { label: 'Fraud Rate', val: stats.summary.fraud_rate, icon: <Zap size={16}/>, color: 'text-blue-400' },
          { label: 'Live Alerts', val: stats.summary.fraud_count, icon: <ShieldAlert size={16}/>, color: 'text-red-400' },
          { label: 'System Load', val: 'Optimal', icon: <Activity size={16}/>, color: 'text-purple-400' },
        ].map((item, i) => (
          <div key={i} className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl shadow-lg">
            <div className={`flex items-center gap-2 text-xs font-bold mb-1 ${item.color}`}>
              {item.icon} {item.label}
            </div>
            <div className="text-xl font-bold font-mono">{item.val}</div>
          </div>
        ))}
      </div>

      {/* Main Content: 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LEFT COLUMN: REAL-TIME STREAM (7/12 width) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            <div className="bg-slate-800/50 p-4 border-b border-slate-800 flex justify-between items-center">
              <h2 className="text-sm font-bold flex items-center gap-2">
                <Clock size={16} className="text-blue-400"/> REAL-TIME TRANSACTION STREAM
              </h2>
              <span className="text-[10px] font-mono text-slate-500">LIVE SYNC ENABLED</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-950 text-slate-500 text-[10px] uppercase font-bold">
                  <tr>
                    <th className="px-6 py-3 tracking-widest">Source Entity</th>
                    <th className="px-6 py-3 tracking-widest">Event Type</th>
                    <th className="px-6 py-3 text-right tracking-widest">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {stats.recent_fraud.length > 0 ? stats.recent_fraud.map((f, i) => (
                    <tr key={i} className="hover:bg-red-500/5 transition-colors group">
                      <td className="px-6 py-4 font-mono text-xs text-blue-400">{f.user}</td>
                      <td className="px-6 py-4">
                        <span className="bg-red-500/10 text-red-500 text-[10px] font-bold px-2 py-0.5 rounded border border-red-500/20">
                          FRAUD_DETECTED
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right font-bold text-white group-hover:text-red-400 transition-colors">
                        ${f.amount}
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="3" className="px-6 py-20 text-center text-slate-600 italic">
                        <Activity className="mx-auto mb-2 opacity-20" size={32} />
                        Waiting for stream events...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: BATCH ANALYSIS (5/12 width) */}
        <div className="lg:col-span-5">
          <div className="bg-slate-900 border-2 border-yellow-500/20 rounded-2xl p-6 h-full shadow-2xl shadow-yellow-500/5">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-yellow-500 font-black text-lg flex items-center gap-2 uppercase tracking-tighter">
                  <ShieldAlert size={20} /> Batch Intelligence
                </h2>
                <p className="text-slate-500 text-[10px] font-mono mt-1">HDFS AGGREGATION ENGINE</p>
              </div>
              <div className="bg-yellow-500/10 text-yellow-500 text-[9px] font-bold px-2 py-1 rounded border border-yellow-500/20">
                DAILY REPORT
              </div>
            </div>

            <p className="text-slate-400 text-xs mb-6 leading-relaxed">
              Identifying high-velocity actors spending over threshold limits within the last 24-hour processing window.
            </p>

            <div className="space-y-3">
              {batchData.length > 0 ? batchData.map((u, i) => (
                <div key={i} className="flex justify-between items-center bg-slate-950 p-4 rounded-xl border border-slate-800 group hover:border-yellow-500/50 transition-all cursor-default">
                  <div>
                    <div className="text-[10px] text-slate-500 font-mono mb-1">FLAGGED USER</div>
                    <div className="font-bold text-white tracking-tight text-sm">{u.user}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[9px] text-yellow-500 font-bold uppercase tracking-widest mb-1">Daily Accumulation</div>
                    <div className="text-lg font-black text-white font-mono">
                      ${u.total_daily_spend.toLocaleString()}
                    </div>
                  </div>
                </div>
              )) : (
                <div className="border-2 border-dashed border-slate-800 rounded-2xl p-12 text-center">
                  <Activity className="mx-auto text-slate-800 mb-3 animate-pulse" size={40} />
                  <p className="text-slate-500 text-xs font-medium">Awaiting Batch Job Completion...</p>
                  <p className="text-slate-700 text-[10px] mt-2 font-mono uppercase leading-tight">
                    spark-submit daily_velocity.py
                  </p>
                </div>
              )}
            </div>
            
            {batchData.length > 0 && (
              <div className="mt-6 pt-6 border-t border-slate-800">
                 <div className="text-[10px] text-slate-500 font-mono italic">
                   * Batch report refreshed based on HDFS Parquet updates.
                 </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default App;