import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ShieldAlert, LayoutDashboard, Map as MapIcon, Users } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Intel from './pages/Intel';
import MapView from './pages/MapView';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-950 text-slate-100">
        {/* SIDEBAR */}
        <nav className="w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col gap-6">
          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert className="text-red-500" size={28} />
            <span className="text-xl font-black tracking-tighter">FRAUD RADAR</span>
          </div>
          
          <div className="flex flex-col gap-2">
            <NavLink to="/" icon={<LayoutDashboard size={20}/>} label="Dashboard" />
            <NavLink to="/map" icon={<MapIcon size={20}/>} label="Live Map" />
            <NavLink to="/intel" icon={<Users size={20}/>} label="User Intelligence" />
          </div>
        </nav>

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/map" element={<MapView />} />
            <Route path="/intel" element={<Intel />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

const NavLink = ({ to, icon, label }) => (
  <Link to={to} className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-all">
    {icon} <span className="font-medium text-sm">{label}</span>
  </Link>
);

export default App;