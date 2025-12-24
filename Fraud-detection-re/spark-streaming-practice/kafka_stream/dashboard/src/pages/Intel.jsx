import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart3, TrendingUp } from 'lucide-react';

const Intel = () => {
  const [profiles, setProfiles] = useState([]);

  useEffect(() => {
    const load = () => axios.get('http://localhost:8000/api/batch-report')
      .then(res => setProfiles(res.data.alerts)); // Note: backend sends 'alerts'
    load();
    const itv = setInterval(load, 5000);
    return () => clearInterval(itv);
  }, []);

  return (
    <div className="p-8 space-y-6">
      <h2 className="text-2xl font-bold">Statistical Intelligence (Batch Layer)</h2>
      <div className="grid gap-4">
        {profiles.map((p, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex justify-between items-center">
            <div>
              <div className="text-blue-400 font-bold text-lg">{p.user}</div>
              <div className="flex gap-6 mt-2 text-xs font-mono text-slate-400">
                <span>Mean (μ): ${p.avg_amount?.toFixed(2)}</span>
                <span>StdDev (σ): ${p.std_dev?.toFixed(2)}</span>
              </div>
            </div>
            <div className="text-right bg-slate-950 px-4 py-2 rounded-lg border border-slate-800">
               <div className="text-[10px] text-slate-600 font-bold uppercase">Samples</div>
               <div className="text-xl font-bold text-white">{p.transaction_count}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Intel;