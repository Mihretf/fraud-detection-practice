import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import L from 'leaflet';

// Fix for Leaflet default icons
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const MapView = () => {
  const [alerts, setAlerts] = useState([]);

  const fetchLocations = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/stats');
      // Filter out any entries that don't have lat/lon just in case
      const validAlerts = (res.data.recent_fraud || []).filter(a => a.lat && a.lon);
      setAlerts(validAlerts); 
    } catch (err) { 
      console.error("Map fetch error:", err); 
    }
  };

  useEffect(() => {
    fetchLocations();
    // Refresh every 3 seconds to match the dashboard
    const interval = setInterval(fetchLocations, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-full w-full p-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden h-[85vh] shadow-2xl">
        {/* Changed center to [42.7, -74.0] because your data is focused around New York/Albany area */}
        <MapContainer center={[42.7, -74.0]} zoom={8} className="h-full w-full">
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; CARTO'
          />
          
          {alerts.map((alert, idx) => (
            <React.Fragment key={idx}>
              {/* FIXED: Using alert.lon instead of alert.lng */}
              <Marker position={[alert.lat, alert.lon]}>
                <Popup>
                  <div className="text-slate-900">
                    <p className="font-bold text-red-600 uppercase text-xs">Fraud Alert</p>
                    <p className="font-bold">{alert.user}</p>
                    <p className="text-sm">Amount: ${alert.amount.toFixed(2)}</p>
                    <p className="text-xs text-slate-500">Source: {alert.source}</p>
                  </div>
                </Popup>
              </Marker>
              
              <Circle 
                center={[alert.lat, alert.lon]} 
                radius={2000} // Reduced radius for better visibility at zoom level 8
                pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.3 }} 
              />
            </React.Fragment>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapView;