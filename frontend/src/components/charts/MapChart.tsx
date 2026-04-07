import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface MapChartProps {
  data: any[];
  config: {
    x_column: string; // Location column
    y_column: string; // Value column
    title?: string;
    colors?: string[];
  };
}

// Component to fit bounds
const FitBounds: React.FC<{ bounds: any }> = ({ bounds }) => {
  const map = useMap();
  
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      map.fitBounds(bounds);
    }
  }, [bounds, map]);
  
  return null;
};

export const MapChart: React.FC<MapChartProps> = ({ data, config }) => {
  const [geoData, setGeoData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Geocode locations (simplified - in production, use a geocoding API)
  useEffect(() => {
    const geocodeData = async () => {
      setLoading(true);
      
      // Simple geocoding for common locations
      const locationCoords: Record<string, [number, number]> = {
        'north': [45.0, -95.0],
        'south': [30.0, -95.0],
        'east': [37.5, -75.0],
        'west': [37.5, -115.0],
        'central': [37.5, -95.0],
        'usa': [37.0902, -95.7129],
        'uk': [51.5074, -0.1278],
        'germany': [51.1657, 10.4515],
        'france': [46.2276, 2.2137],
        'spain': [40.4637, -3.7492],
        'italy': [41.8719, 12.5674],
        'canada': [56.1304, -106.3468],
        'mexico': [23.6345, -102.5528],
        'brazil': [-14.2350, -51.9253],
        'china': [35.8617, 104.1954],
        'japan': [36.2048, 138.2529],
        'india': [20.5937, 78.9629],
        'australia': [-25.2744, 133.7751],
      };

      const geocoded = data.map((item, _index) => {
        const location = String(item[config.x_column]).toLowerCase();
        const value = parseFloat(item[config.y_column]) || 0;
        
        // Try to find coordinates
        let coords: [number, number] = [0, 0];
        for (const [key, coord] of Object.entries(locationCoords)) {
          if (location.includes(key)) {
            coords = coord;
            break;
          }
        }
        
        // If no match, generate random coords (for demo)
        if (coords[0] === 0 && coords[1] === 0) {
          coords = [
            20 + Math.random() * 40,
            -120 + Math.random() * 80
          ];
        }

        return {
          name: item[config.x_column],
          value: value,
          lat: coords[0],
          lng: coords[1]
        };
      });

      setGeoData(geocoded);
      setLoading(false);
    };

    if (data && data.length > 0) {
      geocodeData();
    }
  }, [data, config]);

  const getRadius = (value: number, maxValue: number) => {
    const minRadius = 5;
    const maxRadius = 30;
    return minRadius + (value / maxValue) * (maxRadius - minRadius);
  };

  const getColor = (value: number, maxValue: number) => {
    const ratio = value / maxValue;
    if (ratio > 0.7) return '#EF4444'; // Red for high
    if (ratio > 0.4) return '#F59E0B'; // Orange for medium
    return '#22C55E'; // Green for low
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading map...
      </div>
    );
  }

  if (!geoData || geoData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No geographic data available
      </div>
    );
  }

  const maxValue = Math.max(...geoData.map(d => d.value));
  const bounds = geoData.map(d => [d.lat, d.lng] as [number, number]);

  return (
    <div className="w-full h-full">
      {config.title && (
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{config.title}</h3>
      )}
      <div className="w-full h-[500px] rounded-lg overflow-hidden border border-gray-200">
        <MapContainer
          center={[37.0902, -95.7129]}
          zoom={4}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FitBounds bounds={bounds} />
          {geoData.map((point, index) => (
            <CircleMarker
              key={index}
              center={[point.lat, point.lng]}
              radius={getRadius(point.value, maxValue)}
              fillColor={getColor(point.value, maxValue)}
              color="#fff"
              weight={2}
              opacity={0.8}
              fillOpacity={0.6}
            >
              <Popup>
                <div className="text-sm">
                  <div className="font-semibold">{point.name}</div>
                  <div className="text-gray-600">
                    {config.y_column}: {point.value.toFixed(2)}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">Low</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
          <span className="text-gray-600">Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded-full"></div>
          <span className="text-gray-600">High</span>
        </div>
      </div>
    </div>
  );
};
