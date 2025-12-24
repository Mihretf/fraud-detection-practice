import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Fixing the default icon issue in Leaflet + React
import L from 'leaflet';
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

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/stats');
        setAlerts(res.data.recent_fraud); 
      } catch (err) { console.error(err); }
    };
    fetchLocations();
  }, []);

  return (
    <div className="h-full w-full p-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden h-[80vh] shadow-2xl">
        <MapContainer center={[20, 0]} zoom={2} className="h-full w-full">
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; OpenStreetMap contributors &copy; CARTO'
          />
          
          {alerts.map((alert, idx) => (
            <React.Fragment key={idx}>
              {/* The Marker shows the exact spot */}
              <Marker position={[alert.lat || 0, alert.lng || 0]}>
                <Popup>
                  <div className="text-slate-900">
                    <p className="font-bold text-red-600">FRAUD ALERT</p>
                    <p>User: {alert.user}</p>
                    <p>Amt: ${alert.amount}</p>
                  </div>
                </Popup>
              </Marker>
              
              {/* A Red circle to show a "Danger Zone" */}
              <Circle 
                center={[alert.lat || 0, alert.lng || 0]} 
                radius={50000} 
                pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.2 }} 
              />
            </React.Fragment>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapView;