/**
 * GeoControls Component
 * Controls for geo-radius search filtering
 */

interface GeoControlsProps {
  enabled: boolean;
  onEnabledChange: (enabled: boolean) => void;
  lat: number;
  lng: number;
  radius: number;
  onLatChange: (lat: number) => void;
  onLngChange: (lng: number) => void;
  onRadiusChange: (radius: number) => void;
}

const CITY_PRESETS = [
  { name: 'Seattle, WA', lat: 47.6062, lng: -122.3321 },
  { name: 'Denver, CO', lat: 39.7392, lng: -104.9903 },
  { name: 'Portland, OR', lat: 45.5152, lng: -122.6784 },
  { name: 'Austin, TX', lat: 30.2672, lng: -97.7431 },
  { name: 'Boston, MA', lat: 42.3601, lng: -71.0589 },
  { name: 'San Francisco, CA', lat: 37.7749, lng: -122.4194 },
];

export default function GeoControls({
  enabled,
  onEnabledChange,
  lat,
  lng,
  radius,
  onLatChange,
  onLngChange,
  onRadiusChange,
}: GeoControlsProps) {

  const handleUseMyLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          onLatChange(position.coords.latitude);
          onLngChange(position.coords.longitude);
          alert(`Location set to: ${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`);
        },
        (error) => {
          alert('Unable to get your location: ' + error.message);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser');
    }
  };

  const handleCityPreset = (preset: typeof CITY_PRESETS[0]) => {
    onLatChange(preset.lat);
    onLngChange(preset.lng);
  };

  return (
    <div style={{
      marginTop: '20px',
      padding: '15px',
      background: '#f9f9f9',
      borderRadius: '8px',
      border: '1px solid #e0e0e0',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, fontSize: '1rem' }}>
          📍 Geo-Radius Search
        </h3>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onEnabledChange(e.target.checked)}
          />
          <span style={{ fontWeight: 600 }}>Enable</span>
        </label>
      </div>

      {enabled && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          {/* City Presets */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
              City Presets:
            </label>
            <select
              onChange={(e) => {
                const preset = CITY_PRESETS[parseInt(e.target.value)];
                if (preset) handleCityPreset(preset);
              }}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                fontSize: '0.9rem',
              }}
            >
              <option value="">Select a city...</option>
              {CITY_PRESETS.map((preset, index) => (
                <option key={preset.name} value={index}>
                  {preset.name}
                </option>
              ))}
            </select>
          </div>

          {/* Latitude */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
              Latitude:
            </label>
            <input
              type="number"
              step="0.0001"
              value={lat}
              onChange={(e) => onLatChange(parseFloat(e.target.value) || 0)}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                fontSize: '0.9rem',
              }}
            />
          </div>

          {/* Longitude */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
              Longitude:
            </label>
            <input
              type="number"
              step="0.0001"
              value={lng}
              onChange={(e) => onLngChange(parseFloat(e.target.value) || 0)}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                fontSize: '0.9rem',
              }}
            />
          </div>

          {/* Radius */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: 600 }}>
              Radius: <span style={{ color: '#667eea' }}>{radius} km</span>
            </label>
            <input
              type="range"
              min="5"
              max="200"
              step="5"
              value={radius}
              onChange={(e) => onRadiusChange(parseInt(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>

          {/* Use My Location Button */}
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              onClick={handleUseMyLocation}
              style={{
                width: '100%',
                padding: '8px 16px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.9rem',
              }}
            >
              📍 Use My Location
            </button>
          </div>
        </div>
      )}

      {enabled && (
        <div style={{
          marginTop: '12px',
          padding: '10px',
          background: '#e8f0fe',
          borderRadius: '4px',
          fontSize: '0.85rem',
          color: '#1967d2',
        }}>
          ℹ️ Searching within {radius} km of ({lat.toFixed(4)}, {lng.toFixed(4)})
          <br />
          <small>Note: Coordinate format is [latitude, longitude]</small>
        </div>
      )}
    </div>
  );
}
