import React, { useState } from 'react';

const HomeAutomation = ({ homeStatus, toggleLight, toggleDevice, setTemperature, toggleDoorLock, toggleGarageDoor, loading }) => {
  const [activeHomeTab, setActiveHomeTab] = useState('thermostats');
  const [searchQuery, setSearchQuery] = useState('');

  const getDeviceIcon = (type, state) => {
    const icons = {
      light: state ? '💡' : '🔘',
      switch: state ? '🟢' : '⚫',
      fan: state ? '🌀' : '⭕',
      thermostat: '🌡️',
      security: '🔐',
    };
    return icons[type] || '📱';
  };

  // Filter function - always returns array of [key, value] pairs
  const filterDevices = (devices) => {
    const entries = Object.entries(devices || {});
    if (!searchQuery) return entries;
    return entries.filter(([key, device]) => {
      const name = device.name || key;
      return name.toLowerCase().includes(searchQuery.toLowerCase());
    });
  };

  // Render Thermostats Tab
  const renderThermostats = () => {
    const thermostats = homeStatus?.thermostats || [];

    if (thermostats.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">🌡️</div>
          <p>No thermostats found</p>
        </div>
      );
    }

    return (
      <div className="device-grid">
        {thermostats.map((thermostat) => (
          <div key={thermostat.entity_id} className="device-card" style={{ cursor: 'default' }}>
            <div className="device-card-header">
              <span className="device-name">{getDeviceIcon('thermostat')} {thermostat.name}</span>
              <span className="device-status" style={{
                textTransform: 'capitalize',
                background: 'rgba(102, 126, 234, 0.1)',
                padding: '0.25rem 0.6rem',
                borderRadius: '12px',
                fontSize: '0.8rem'
              }}>
                {thermostat.mode}
              </span>
            </div>
            <div style={{
              marginBottom: '1rem',
              padding: '0.75rem',
              background: 'rgba(102, 126, 234, 0.05)',
              borderRadius: '8px'
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '0.5rem',
                fontSize: '0.95rem'
              }}>
                <span style={{ color: '#666' }}>Current:</span>
                <strong style={{ fontSize: '1.1rem', color: '#333' }}>
                  {thermostat.current_temp || 0}°F
                </strong>
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '0.95rem'
              }}>
                <span style={{ color: '#666' }}>Target:</span>
                <strong style={{ fontSize: '1.1rem', color: '#667eea' }}>
                  {thermostat.target_temp || 0}°F
                </strong>
              </div>
              {thermostat.humidity > 0 && (
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginTop: '0.5rem',
                  paddingTop: '0.5rem',
                  borderTop: '1px solid rgba(102, 126, 234, 0.2)',
                  fontSize: '0.9rem'
                }}>
                  <span style={{ color: '#666' }}>Humidity:</span>
                  <strong style={{ color: '#333' }}>{thermostat.humidity}%</strong>
                </div>
              )}
            </div>
            <div className="device-controls" style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.5rem'
            }}>
              {[64, 66, 68, 70, 72, 74, 76].map((temp) => (
                <button
                  key={temp}
                  onClick={() => setTemperature(temp, thermostat.entity_id)}
                  disabled={loading}
                  style={{
                    padding: '0.5rem 0.75rem',
                    border: '2px solid',
                    borderColor: thermostat.target_temp === temp ? '#667eea' : '#e0e0e0',
                    borderRadius: '8px',
                    background: thermostat.target_temp === temp ? '#667eea' : 'white',
                    color: thermostat.target_temp === temp ? 'white' : '#333',
                    fontWeight: thermostat.target_temp === temp ? 'bold' : '500',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (thermostat.target_temp !== temp) {
                      e.target.style.borderColor = '#667eea';
                      e.target.style.background = 'rgba(102, 126, 234, 0.1)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (thermostat.target_temp !== temp) {
                      e.target.style.borderColor = '#e0e0e0';
                      e.target.style.background = 'white';
                    }
                  }}
                >
                  {temp}°
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render Lights Tab
  const renderLights = () => {
    const lights = homeStatus?.lights || {};
    const filteredLights = filterDevices(lights);

    if (filteredLights.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">💡</div>
          <p>{searchQuery ? 'No lights match your search' : 'No lights found'}</p>
        </div>
      );
    }

    return (
      <>
        <div className="search-filter-bar">
          <input
            type="text"
            className="search-input"
            placeholder="Search lights..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="section-header">
          All Lights <span className="device-count">{filteredLights.length}</span>
        </div>
        <div className="device-grid compact-grid">
          {filteredLights.map(([key, light]) => (
            <div
              key={key}
              className={`device-card ${light?.on ? 'active' : ''}`}
              onClick={() => toggleLight(key)}
              style={{ minHeight: '100px' }}
            >
              <div className="device-card-header">
                <span className="device-name">
                  {getDeviceIcon('light', light?.on)} {light?.name || key}
                </span>
              </div>
              <div className="device-status" style={{ marginTop: '0.5rem' }}>
                {light?.on ? '✓ On' : '○ Off'}
                {light?.on && light.brightness > 0 && (
                  <div style={{ fontSize: '0.8rem', marginTop: '0.25rem', opacity: 0.8 }}>
                    Brightness: {Math.round((light.brightness / 255) * 100)}%
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </>
    );
  };

  // Render Switches Tab
  const renderSwitches = () => {
    const switches = homeStatus?.switches || {};
    const filteredSwitches = filterDevices(switches);

    if (filteredSwitches.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">🔌</div>
          <p>{searchQuery ? 'No switches match your search' : 'No switches found'}</p>
        </div>
      );
    }

    return (
      <>
        <div className="search-filter-bar">
          <input
            type="text"
            className="search-input"
            placeholder="Search switches..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="section-header">
          All Switches <span className="device-count">{filteredSwitches.length}</span>
        </div>
        <div className="device-grid compact-grid">
          {filteredSwitches.map(([key, switchDevice]) => (
            <div
              key={key}
              className={`device-card ${switchDevice?.on ? 'active' : ''}`}
              onClick={() => toggleDevice(key)}
              style={{ minHeight: '100px' }}
            >
              <div className="device-card-header">
                <span className="device-name">
                  {getDeviceIcon('switch', switchDevice?.on)} {switchDevice?.name || key}
                </span>
              </div>
              <div className="device-status" style={{ marginTop: '0.5rem' }}>
                {switchDevice?.on ? '✓ On' : '○ Off'}
              </div>
            </div>
          ))}
        </div>
      </>
    );
  };

  // Render Fans Tab
  const renderFans = () => {
    const fans = homeStatus?.fans || {};
    const filteredFans = filterDevices(fans);

    if (filteredFans.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">🌀</div>
          <p>{searchQuery ? 'No fans match your search' : 'No fans found'}</p>
        </div>
      );
    }

    return (
      <>
        <div className="search-filter-bar">
          <input
            type="text"
            className="search-input"
            placeholder="Search fans..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="section-header">
          All Fans <span className="device-count">{filteredFans.length}</span>
        </div>
        <div className="device-grid compact-grid">
          {filteredFans.map(([key, fan]) => (
            <div
              key={key}
              className={`device-card ${fan?.on ? 'active' : ''}`}
              onClick={() => toggleDevice(key)}
              style={{ minHeight: '100px' }}
            >
              <div className="device-card-header">
                <span className="device-name">
                  {getDeviceIcon('fan', fan?.on)} {fan?.name || key}
                </span>
              </div>
              <div className="device-status" style={{ marginTop: '0.5rem' }}>
                {fan?.on ? '✓ On' : '○ Off'}
                {fan?.on && fan.speed > 0 && (
                  <div style={{ fontSize: '0.8rem', marginTop: '0.25rem', opacity: 0.8 }}>
                    Speed: {fan.speed}%
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </>
    );
  };

  // Render Security Tab
  const renderSecurity = () => {
    const security = homeStatus?.security || {};

    return (
      <div className="device-grid">
        <div className="device-card">
          <div className="device-card-header">
            <span className="device-name">
              {security.door_locked ? '🔒' : '🔓'} Front Door
            </span>
            <span className="device-status">
              {security.door_locked ? 'Locked' : 'Unlocked'}
            </span>
          </div>
          <button
            className="device-control-btn"
            onClick={toggleDoorLock}
            disabled={loading}
            style={{
              width: '100%',
              marginTop: '0.5rem',
              background: security.door_locked ? '#28a745' : '#ffc107',
              color: 'white',
              fontWeight: 'bold'
            }}
          >
            {security.door_locked ? 'Unlock' : 'Lock'} Door
          </button>
        </div>

        <div className="device-card">
          <div className="device-card-header">
            <span className="device-name">
              {security.garage_open ? '🚗' : '🚪'} Garage
            </span>
            <span className="device-status">
              {security.garage_open ? 'Open' : 'Closed'}
            </span>
          </div>
          <button
            className="device-control-btn"
            onClick={toggleGarageDoor}
            disabled={loading}
            style={{
              width: '100%',
              marginTop: '0.5rem',
              background: security.garage_open ? '#ffc107' : '#28a745',
              color: 'white',
              fontWeight: 'bold'
            }}
          >
            {security.garage_open ? 'Close' : 'Open'} Garage
          </button>
        </div>

        <div className="device-card" style={{
          background: security.motion_detected ? '#fff3cd' : '#d4edda',
          cursor: 'default'
        }}>
          <div className="device-card-header">
            <span className="device-name">
              {security.motion_detected ? '⚠️' : '✅'} Motion Sensor
            </span>
            <span className="device-status" style={{
              color: security.motion_detected ? '#ff6b00' : '#28a745',
              fontWeight: 'bold'
            }}>
              {security.motion_detected ? 'Motion Detected' : 'Clear'}
            </span>
          </div>
        </div>
      </div>
    );
  };

  // Render Active Tab Content
  const renderTabContent = () => {
    switch (activeHomeTab) {
      case 'thermostats':
        return renderThermostats();
      case 'lights':
        return renderLights();
      case 'switches':
        return renderSwitches();
      case 'fans':
        return renderFans();
      case 'security':
        return renderSecurity();
      default:
        return null;
    }
  };

  return (
    <section className="section">
      <h2>🏠 Home Automation</h2>

      <div className="home-automation-container">
        <div className="home-tabs">
          <button
            className={`home-tab ${activeHomeTab === 'thermostats' ? 'active' : ''}`}
            onClick={() => { setActiveHomeTab('thermostats'); setSearchQuery(''); }}
          >
            🌡️ Thermostats ({homeStatus?.thermostats?.length || 0})
          </button>
          <button
            className={`home-tab ${activeHomeTab === 'lights' ? 'active' : ''}`}
            onClick={() => { setActiveHomeTab('lights'); setSearchQuery(''); }}
          >
            💡 Lights ({Object.keys(homeStatus?.lights || {}).length})
          </button>
          <button
            className={`home-tab ${activeHomeTab === 'switches' ? 'active' : ''}`}
            onClick={() => { setActiveHomeTab('switches'); setSearchQuery(''); }}
          >
            🔌 Switches ({Object.keys(homeStatus?.switches || {}).length})
          </button>
          <button
            className={`home-tab ${activeHomeTab === 'fans' ? 'active' : ''}`}
            onClick={() => { setActiveHomeTab('fans'); setSearchQuery(''); }}
          >
            🌀 Fans ({Object.keys(homeStatus?.fans || {}).length})
          </button>
          <button
            className={`home-tab ${activeHomeTab === 'security' ? 'active' : ''}`}
            onClick={() => { setActiveHomeTab('security'); setSearchQuery(''); }}
          >
            🔐 Security
          </button>
        </div>

        <div className="home-tab-content">
          {renderTabContent()}
        </div>
      </div>
    </section>
  );
};

export default HomeAutomation;
