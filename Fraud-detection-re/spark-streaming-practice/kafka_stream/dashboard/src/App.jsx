import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { ShieldAlert, Activity, DollarSign, List } from 'lucide-react';

const App = () => {
  const [data, setData] = useState(null);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/stats');
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (!data || data.error) return <div className="p-10 text-center">Connecting to HDFS Pipeline...</div>;

  const stats = [
    { title: 'Total Transactions', value: data.summary.total_count, icon: <Activity className="text-blue-500" /> },
    { title: 'Fraud Detected', value: data.summary.fraud_count, icon: <ShieldAlert className="text-red-500" /> },
    { title: 'Fraud Rate', value: data.summary.fraud_rate, icon: <List className="text-purple-500" /> },
    { title: 'Fraud Volume', value: `$${data.summary.fraud_volume}`, icon: <DollarSign className="text-green-500" /> },
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Fraud Detection Command Center</h1>
        <p className="text-gray-600">Real-time HDFS Stream Monitoring</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, i) => (
          <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
            </div>
            {stat.icon}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Fraud Table */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Recent Fraudulent Alerts</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="text-gray-400 border-b">
                <th className="pb-3">User</th>
                <th className="pb-3">Amount</th>
                <th className="pb-3">Source</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_fraud.map((item, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-3 font-medium">{item.user}</td>
                  <td className="py-3 text-red-600 font-bold">${item.amount}</td>
                  <td className="py-3 text-gray-600">{item.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Simple Visualization */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col items-center justify-center">
             <h2 className="text-xl font-semibold mb-4 w-full text-left">Volume Analysis</h2>
             <div className="w-full h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                        {name: 'Legit', amount: data.summary.total_volume - data.summary.fraud_volume},
                        {name: 'Fraud', amount: data.summary.fraud_volume}
                    ]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="amount" fill="#3b82f6" />
                    </BarChart>
                </ResponsiveContainer>
             </div>
        </div>
      </div>
    </div>
  );
};

export default App;