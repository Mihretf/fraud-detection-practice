import React, { useState, useEffect } from 'react';
import { History, AlertTriangle, Download } from 'lucide-react';

const Audit = () => {
  const [auditData, setAuditData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/batch-audit')
      .then(res => res.json())
      .then(data => {
        setAuditData(data.audit || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Audit Fetch Error:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
            <History className="text-blue-500" /> FRAUD AUDIT LOG
          </h1>
          <p className="text-slate-400 mt-1">Historical batch analysis of flagged transactions from HDFS.</p>
        </div>
        <button className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-md flex items-center gap-2 text-sm transition-colors">
          <Download size={16} /> Export CSV
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr>
              <th className="p-4 text-xs font-bold uppercase tracking-wider text-slate-400">Transaction ID</th>
              <th className="p-4 text-xs font-bold uppercase tracking-wider text-slate-400">User</th>
              <th className="p-4 text-xs font-bold uppercase tracking-wider text-slate-400">Amount</th>
              <th className="p-4 text-xs font-bold uppercase tracking-wider text-slate-400">Reason</th>
              <th className="p-4 text-xs font-bold uppercase tracking-wider text-slate-400">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {auditData.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="p-4 font-mono text-sm text-slate-300">{row.transaction_id || `TXN-${idx+1000}`}</td>
                <td className="p-4 font-semibold">{row.user}</td>
                <td className="p-4 text-red-400">${row.amount?.toFixed(2)}</td>
                <td className="p-4">
                   <span className="text-xs bg-red-500/10 text-red-500 px-2 py-1 rounded border border-red-500/20">
                     Statistically Anomalous
                   </span>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2 text-orange-400">
                    <AlertTriangle size={14} />
                    <span className="text-sm font-medium">Flagged</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {auditData.length === 0 && !loading && (
          <div className="p-20 text-center text-slate-500">
            No historical fraud detected in the current HDFS batch.
          </div>
        )}
      </div>
    </div>
  );
};

export default Audit;