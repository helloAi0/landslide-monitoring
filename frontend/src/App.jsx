import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix missing Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function App() {
  const mapRef = useRef(null);
  const routeLayerRef = useRef(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [coordinates, setCoordinates] = useState({ lat: null, lng: null });

  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('map-container').setView([30.3165, 78.0322], 9);

      // Using Esri World Imagery to match your satellite aesthetic
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
      }).addTo(map);

      routeLayerRef.current = L.layerGroup().addTo(map);

      map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        setCoordinates({ lat, lng });
        analyzeLocation(lat, lng);
        
        map.eachLayer((layer) => {
          if (layer instanceof L.Marker) map.removeLayer(layer);
        });

        L.marker([lat, lng]).addTo(map);
      });

      mapRef.current = map;
      setTimeout(() => map.invalidateSize(), 300);
    }
  }, []);

  const analyzeLocation = async (lat, lng) => {
    setLoading(true);
    routeLayerRef.current.clearLayers();
    try {
      const response = await fetch('http://localhost:8000/api/predict-location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: lat, longitude: lng, auto_fetch_live_data: true })
      });
      if (!response.ok) throw new Error("Server error");
      const result = await response.json();
      setData(result);
    } catch (err) {
      console.warn("Backend unavailable. Ensure Uvicorn is running on port 8000.");
    }
    setLoading(false);
  };

  const drawEvacuationRoute = async () => {
    if (!coordinates.lat || !mapRef.current) return;
    alert("In production, this queries the OSRM backend to map the lowest-elevation exit route from this sector.");
    // Simulated OSRM Route drawing for demo
    const safeZone = [coordinates.lat - 0.05, coordinates.lng + 0.05];
    const route = L.polyline([[coordinates.lat, coordinates.lng], safeZone], {color: '#22c55e', weight: 5, dashArray: '10, 10'}).addTo(routeLayerRef.current);
    L.circleMarker(safeZone, {color: '#22c55e', radius: 8, fillOpacity: 1}).bindPopup("Safe Zone / Evac Center").addTo(routeLayerRef.current);
    mapRef.current.fitBounds(route.getBounds(), { padding: [50, 50] });
  };

  const downloadReport = () => {
    window.print(); // Quick browser PDF generation for demo purposes
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', fontFamily: 'system-ui, sans-serif' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '15px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          <h2 style={{ margin: 0, color: '#f8fafc', fontSize: '1.4rem', letterSpacing: '1px' }}>NER LANDSLIDE COMMAND CENTER</h2>
          <span style={{ background: '#0ea5e9', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>SIH PROTOTYPE</span>
        </div>
        <div style={{ display: 'flex', gap: '15px' }}>
          <div style={{ color: '#0ea5e9', fontSize: '0.8rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(14, 165, 233, 0.1)', padding: '6px 12px', borderRadius: '20px' }}>
            🛰️ SATELLITE TELEMETRY ACTIVE
          </div>
          <div style={{ color: '#22c55e', fontSize: '0.8rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(34, 197, 94, 0.1)', padding: '6px 12px', borderRadius: '20px' }}>
            <span style={{ width: '8px', height: '8px', background: '#22c55e', borderRadius: '50%', display: 'inline-block' }}></span>
            TELEGRAM ALERTS STANDBY
          </div>
        </div>
      </div>

      {/* Main Grid Layout - Tweaked to give the Map way more space (2.5fr vs 1fr) */}
      <div style={{ display: 'grid', gridTemplateColumns: '2.5fr 1fr', gap: '24px' }}>
        
        {/* Left Column: Huge Map Container */}
        <div style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: '1px solid #1e293b', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#f8fafc', fontWeight: '500' }}>
            <span>📍 Regional Hazard Radar (Click map to analyze)</span>
            {coordinates.lat && <span>{coordinates.lat.toFixed(4)} N, {coordinates.lng.toFixed(4)} E</span>}
          </div>
          {/* Increased Map Height to 800px */}
          <div id="map-container" style={{ width: '100%', height: '800px', position: 'relative' }}>
             {/* Overlay floating action buttons */}
             <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 400, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button style={{ background: '#1e293b', color: '#fff', border: '1px solid #334155', padding: '8px 12px', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
                   🏔️ 3D Terrain View
                </button>
                <button style={{ background: '#1e293b', color: '#fff', border: '1px solid #334155', padding: '8px 12px', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
                   🔥 Susceptibility Heatmap
                </button>
             </div>
          </div>
        </div>

        {/* Right Column: Live Data & Hybrid Assessment */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Live Environmental Data Panel (Replaces Sliders) */}
          <div style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: '1px solid #1e293b', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f8fafc', marginBottom: '16px', fontWeight: '500' }}>
              📡 Live Automated Telemetry
            </div>
            
            {loading ? (
               <div style={{ color: '#0ea5e9', textAlign: 'center', padding: '20px 0' }}>Fetching Open-Meteo & SoilGrids APIs...</div>
            ) : data ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                  <span style={{ color: '#94a3b8' }}>Real-time Precipitation (24h)</span>
                  <b style={{ color: '#f8fafc' }}>{data.live_precipitation.daily_mm} mm</b>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                  <span style={{ color: '#94a3b8' }}>7-Day Hydrological Load</span>
                  <b style={{ color: '#f8fafc' }}>{data.live_precipitation.cumul_7d_mm} mm</b>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: '8px' }}>
                  <span style={{ color: '#94a3b8' }}>Soil Comp (Clay / Sand)</span>
                  <b style={{ color: '#f8fafc' }}>{data.soil_properties.clay_pct}% / {data.soil_properties.sand_pct}%</b>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>ISRIC Bulk Density</span>
                  <b style={{ color: '#f8fafc' }}>{data.soil_properties.bulk_density_g_cm3} g/cm³</b>
                </div>
              </div>
            ) : (
               <div style={{ color: '#64748b', textAlign: 'center', padding: '20px 0', fontSize: '0.85rem' }}>Awaiting coordinates...</div>
            )}
          </div>

          {/* Hybrid Risk Assessment Panel */}
          <div style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: data?.risk_level === 'High' ? '1px solid #ef4444' : '1px solid #1e293b', padding: '20px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
            {data?.risk_level === 'High' && (
                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '4px', background: '#ef4444' }}></div>
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#f8fafc', fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '8px' }}>
              🛡️ HYBRID RISK ASSESSMENT
            </div>
            
            <div style={{ margin: '16px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#0f172a', padding: '15px', borderRadius: '8px' }}>
                <div style={{ textAlign: 'left' }}>
                    <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginBottom: '4px' }}>Geotechnical Physics</div>
                    <div style={{ fontSize: '1rem', color: '#f8fafc' }}>Factor of Safety: <b style={{ color: data?.factor_of_safety < 1.0 ? '#ef4444' : '#22c55e', fontSize: '1.2rem' }}>{data ? data.factor_of_safety : '--'}</b></div>
                </div>
                <div style={{ textAlign: 'right', borderLeft: '1px solid #1e293b', paddingLeft: '15px' }}>
                    <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginBottom: '4px' }}>XGBoost ML Model</div>
                    <div style={{ fontSize: '1rem', color: '#f8fafc' }}>Failure Prob: <b style={{ color: data?.probability_score > 0.6 ? '#ef4444' : '#f8fafc', fontSize: '1.2rem' }}>{data ? (data.probability_score * 100).toFixed(1) : '0.0'}%</b></div>
                </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-around', fontSize: '0.9rem', color: '#e2e8f0', marginTop: '16px' }}>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginBottom: '4px' }}>⛰️ Terrain Elev</div>
                <b>{data ? data.elevation : '--'}m</b>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginBottom: '4px' }}>📉 Slope Grad</div>
                <b>{data ? data.slope : '--'}°</b>
              </div>
              <div>
                <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginBottom: '4px' }}>🌡️ Ambient</div>
                <b>{data ? data.temperature_c : '--'}°C</b>
              </div>
            </div>

            {data?.risk_level === 'High' && (
                <div style={{ marginTop: '20px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '12px', borderRadius: '6px', fontWeight: 'bold', fontSize: '0.85rem' }}>
                    ⚠️ CRITICAL HAZARD: AUTOMATED SMS ALERTS DISPATCHED TO NDRF
                </div>
            )}
          </div>

          {/* Emergency Action Center */}
          <div style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: '1px solid #1e293b', padding: '20px' }}>
            <div style={{ color: '#f8fafc', fontWeight: 'bold', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🚨 Emergency Action Protocols
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button 
                    onClick={drawEvacuationRoute}
                    disabled={!data}
                    style={{ background: data ? '#22c55e' : '#1e293b', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', cursor: data ? 'pointer' : 'not-allowed', fontWeight: 'bold', opacity: data ? 1 : 0.5 }}>
                    🏃‍♂️ Generate Safe Evacuation Route (OSRM)
                </button>
                <button 
                    onClick={downloadReport}
                    disabled={!data}
                    style={{ background: '#0ea5e9', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', cursor: data ? 'pointer' : 'not-allowed', fontWeight: 'bold', opacity: data ? 1 : 0.5 }}>
                    📄 Download Incident Briefing (PDF)
                </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}