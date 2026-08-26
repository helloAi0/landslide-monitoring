import React, { useEffect } from 'react';
import mapboxgl from 'mapbox-gl';

export default function Map3DModal({ lat, lon, onClose, mapboxToken }) {
  useEffect(() => {
    if (!mapboxToken) return;

    mapboxgl.accessToken = mapboxToken;
    const map = new mapboxgl.Map({
      container: 'mapbox-3d-container',
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [lon, lat],
      zoom: 14.5,
      pitch: 70,
      bearing: -30
    });

    map.on('load', () => {
      map.addSource('mapbox-dem', {
        'type': 'raster-dem',
        'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
        'tileSize': 512,
        'maxzoom': 14
      });
      map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.8 });
    });

    return () => map.remove();
  }, [lat, lon, mapboxToken]);

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      backgroundColor: 'rgba(0,0,0,0.85)', zIndex: 9999, display: 'flex',
      flexDirection: 'column', padding: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#fff', marginBottom: '10px' }}>
        <h3>🏔️ 3D Terrain Analysis ({lat.toFixed(4)}, {lon.toFixed(4)})</h3>
        <button 
          onClick={onClose}
          style={{ background: '#ef4444', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
        >
          Close 3D View
        </button>
      </div>
      <div id="mapbox-3d-container" style={{ flex: 1, borderRadius: '8px', overflow: 'hidden' }} />
    </div>
  );
}