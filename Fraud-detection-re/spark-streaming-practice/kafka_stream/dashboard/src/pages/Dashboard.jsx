import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DollarSign, Zap, Activity } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    summary: { total_volume: 0, fraud_rate: "0%", fraud_count: 0 },
    recent_fraud: []
  });

  const fetchData = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/stats');
      setStats(res.data);
    } catch (err) { console.error("Stats fetch error:", err); }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Total Vol." val={`$${stats.summary.total_volume}`} color="text-emerald-400" />
        <StatCard title="Fraud Rate" val={stats.summary.fraud_rate} color="text-blue-400" />
        <StatCard title="Live Alerts" val={stats.summary.fraud_count} color="text-red-400" />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-4 bg-slate-800/50 border-b border-slate-800 font-bold text-sm">REAL-TIME FRAUD STREAM</div>
        <table className="w-full text-left text-sm">
          <thead className="text-slate-500 uppercase text-[10px] font-bold">
            <tr>
              <th className="px-6 py-3">User</th>
              <th className="px-6 py-3">Source</th>
              <th className="px-6 py-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {stats.recent_fraud.map((f, i) => (
              <tr key={i} className="hover:bg-red-500/5">
                <td className="px-6 py-4 font-mono text-blue-400">{f.user}</td>
                <td className="px-6 py-4 text-slate-400">{f.source}</td>
                <td className="px-6 py-4 text-right font-bold text-red-500">${f.amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatCard = ({ title, val, color }) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
    <div className="text-xs font-bold text-slate-500 uppercase mb-2">{title}</div>
    <div className={`text-3xl font-black font-mono ${color}`}>{val}</div>
  </div>
);

export default Dashboard;