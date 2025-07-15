# Settings Endpoints

This document provides an overview of the settings API endpoints available in the smart-nyuki application and the necessary fields for each endpoint.

## User Settings
- **Endpoint**: `/api/settings/user-settings/my_settings/`
- **Methods**: GET, POST, PATCH
- **Fields**:
  - `timezone` (string, default: 'UTC')
  - `language` (string, default: 'en')
  - `temperature_unit` (string, options: 'Celsius', 'Fahrenheit', default: 'Celsius')
  - `weight_unit` (string, options: 'Kilograms', 'Pounds', default: 'Kilograms')
  - `date_format` (string, options: 'DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD', default: 'DD/MM/YYYY')

## Alert Thresholds

### Overview
Alert thresholds support both **global** (apply to all hives) and **hive-specific** settings. The system uses a fallback mechanism where hive-specific thresholds take precedence over global ones.

### Base Endpoint
- **Base**: `/api/settings/alert-thresholds/`
- **Authentication**: Required (JWT)

### Fields
- `hive` (UUID, nullable: Yes for global thresholds)
- `temperature_min` (decimal, default: 32.0) - Minimum temperature in °C
- `temperature_max` (decimal, default: 38.0) - Maximum temperature in °C
- `humidity_min` (decimal, default: 40.0) - Minimum humidity in %
- `humidity_max` (decimal, default: 70.0) - Maximum humidity in %
- `weight_change_threshold` (decimal, default: 2.0) - Daily weight change in kg
- `sound_level_threshold` (integer, default: 85) - Sound level in dB
- `battery_warning_level` (integer, default: 20) - Battery warning in %
- `inspection_reminder_days` (integer, default: 7) - Days before inspection

### API Endpoints

#### 1. Get All Thresholds
```http
GET /api/settings/alert-thresholds/
```
**Use Case**: Display all user's thresholds in a list/table

#### 2. Global Thresholds Management
```http
GET /api/settings/alert-thresholds/global_thresholds/
POST /api/settings/alert-thresholds/set_global_thresholds/
PATCH /api/settings/alert-thresholds/set_global_thresholds/
```
**Use Case**: Global settings page/section

#### 3. Hive-Specific Thresholds
```http
GET /api/settings/alert-thresholds/hive_thresholds/?hive_id=<uuid>
POST /api/settings/alert-thresholds/
```
**Use Case**: Hive-specific settings page

#### 4. Available Hives
```http
GET /api/settings/alert-thresholds/available_hives/
```
**Use Case**: Populate hive selection dropdown

---

## Frontend Implementation Guide

### 1. Alert Thresholds Settings Page Structure

```jsx
// Suggested component structure
const AlertThresholdsSettings = () => {
  const [globalThresholds, setGlobalThresholds] = useState(null);
  const [hiveThresholds, setHiveThresholds] = useState([]);
  const [availableHives, setAvailableHives] = useState([]);
  const [selectedHive, setSelectedHive] = useState(null);
  const [activeTab, setActiveTab] = useState('global'); // 'global' or 'hive'
  
  return (
    <div className="alert-thresholds-settings">
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      {activeTab === 'global' && (
        <GlobalThresholdsForm 
          thresholds={globalThresholds}
          onSave={handleGlobalSave}
        />
      )}
      
      {activeTab === 'hive' && (
        <HiveThresholdsManager 
          hives={availableHives}
          selectedHive={selectedHive}
          onHiveSelect={setSelectedHive}
          onSave={handleHiveSave}
        />
      )}
    </div>
  );
};
```

### 2. API Service Functions

```javascript
// services/alertThresholds.js
const API_BASE = '/api/settings/alert-thresholds';

export const alertThresholdsApi = {
  // Get global thresholds
  getGlobalThresholds: async () => {
    try {
      const response = await api.get(`${API_BASE}/global_thresholds/`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // No global thresholds set yet
      }
      throw error;
    }
  },

  // Set/update global thresholds
  setGlobalThresholds: async (data) => {
    const response = await api.post(`${API_BASE}/set_global_thresholds/`, data);
    return response.data;
  },

  // Get hive-specific thresholds
  getHiveThresholds: async (hiveId) => {
    const response = await api.get(`${API_BASE}/hive_thresholds/?hive_id=${hiveId}`);
    return response.data;
  },

  // Create hive-specific thresholds
  createHiveThresholds: async (data) => {
    const response = await api.post(`${API_BASE}/`, data);
    return response.data;
  },

  // Update hive-specific thresholds
  updateHiveThresholds: async (id, data) => {
    const response = await api.patch(`${API_BASE}/${id}/`, data);
    return response.data;
  },

  // Get available hives
  getAvailableHives: async () => {
    const response = await api.get(`${API_BASE}/available_hives/`);
    return response.data;
  },

  // Get all thresholds
  getAllThresholds: async () => {
    const response = await api.get(`${API_BASE}/`);
    return response.data;
  }
};
```

### 3. Global Thresholds Form Component

```jsx
const GlobalThresholdsForm = ({ thresholds, onSave }) => {
  const [formData, setFormData] = useState({
    temperature_min: 32.0,
    temperature_max: 38.0,
    humidity_min: 40.0,
    humidity_max: 70.0,
    weight_change_threshold: 2.0,
    sound_level_threshold: 85,
    battery_warning_level: 20,
    inspection_reminder_days: 7,
    ...thresholds
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await alertThresholdsApi.setGlobalThresholds(formData);
      onSave();
      toast.success('Global thresholds updated successfully');
    } catch (error) {
      toast.error('Failed to update global thresholds');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="thresholds-form">
      <div className="form-section">
        <h3>Temperature Settings (°C)</h3>
        <div className="form-row">
          <div className="form-group">
            <label>Minimum Temperature</label>
            <input 
              type="number" 
              step="0.1"
              value={formData.temperature_min}
              onChange={(e) => setFormData({...formData, temperature_min: parseFloat(e.target.value)})}
            />
          </div>
          <div className="form-group">
            <label>Maximum Temperature</label>
            <input 
              type="number" 
              step="0.1"
              value={formData.temperature_max}
              onChange={(e) => setFormData({...formData, temperature_max: parseFloat(e.target.value)})}
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Humidity Settings (%)</h3>
        <div className="form-row">
          <div className="form-group">
            <label>Minimum Humidity</label>
            <input 
              type="number" 
              step="0.1"
              min="0" 
              max="100"
              value={formData.humidity_min}
              onChange={(e) => setFormData({...formData, humidity_min: parseFloat(e.target.value)})}
            />
          </div>
          <div className="form-group">
            <label>Maximum Humidity</label>
            <input 
              type="number" 
              step="0.1"
              min="0" 
              max="100"
              value={formData.humidity_max}
              onChange={(e) => setFormData({...formData, humidity_max: parseFloat(e.target.value)})}
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Other Settings</h3>
        <div className="form-row">
          <div className="form-group">
            <label>Weight Change Threshold (kg)</label>
            <input 
              type="number" 
              step="0.1"
              value={formData.weight_change_threshold}
              onChange={(e) => setFormData({...formData, weight_change_threshold: parseFloat(e.target.value)})}
            />
          </div>
          <div className="form-group">
            <label>Sound Level Threshold (dB)</label>
            <input 
              type="number" 
              min="0" 
              max="150"
              value={formData.sound_level_threshold}
              onChange={(e) => setFormData({...formData, sound_level_threshold: parseInt(e.target.value)})}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Battery Warning Level (%)</label>
            <input 
              type="number" 
              min="0" 
              max="100"
              value={formData.battery_warning_level}
              onChange={(e) => setFormData({...formData, battery_warning_level: parseInt(e.target.value)})}
            />
          </div>
          <div className="form-group">
            <label>Inspection Reminder (days)</label>
            <input 
              type="number" 
              min="1" 
              max="365"
              value={formData.inspection_reminder_days}
              onChange={(e) => setFormData({...formData, inspection_reminder_days: parseInt(e.target.value)})}
            />
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          Save Global Thresholds
        </button>
      </div>
    </form>
  );
};
```

### 4. Hive-Specific Thresholds Manager

```jsx
const HiveThresholdsManager = ({ hives, selectedHive, onHiveSelect, onSave }) => {
  const [hiveThresholds, setHiveThresholds] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadHiveThresholds = async (hiveId) => {
    if (!hiveId) return;
    setLoading(true);
    try {
      const data = await alertThresholdsApi.getHiveThresholds(hiveId);
      setHiveThresholds(data);
    } catch (error) {
      console.error('Failed to load hive thresholds:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedHive) {
      loadHiveThresholds(selectedHive.id);
    }
  }, [selectedHive]);

  const handleSave = async (formData) => {
    try {
      if (hiveThresholds?.id) {
        // Update existing
        await alertThresholdsApi.updateHiveThresholds(hiveThresholds.id, formData);
      } else {
        // Create new
        await alertThresholdsApi.createHiveThresholds({
          ...formData,
          hive: selectedHive.id
        });
      }
      onSave();
      toast.success('Hive thresholds updated successfully');
    } catch (error) {
      toast.error('Failed to update hive thresholds');
    }
  };

  return (
    <div className="hive-thresholds-manager">
      <div className="hive-selector">
        <h3>Select Hive</h3>
        <select 
          value={selectedHive?.id || ''}
          onChange={(e) => {
            const hive = hives.find(h => h.id === e.target.value);
            onHiveSelect(hive);
          }}
        >
          <option value="">Select a hive...</option>
          {hives.map(hive => (
            <option key={hive.id} value={hive.id}>
              {hive.name} - {hive.apiary_name}
            </option>
          ))}
        </select>
      </div>

      {selectedHive && (
        <div className="hive-thresholds-form">
          <h3>Thresholds for {selectedHive.name}</h3>
          {hiveThresholds?.is_global && (
            <div className="info-banner">
              <p>This hive is currently using global thresholds. You can override them below.</p>
            </div>
          )}
          
          {loading ? (
            <div className="loading">Loading thresholds...</div>
          ) : (
            <ThresholdsForm 
              thresholds={hiveThresholds}
              onSave={handleSave}
              isHiveSpecific={true}
            />
          )}
        </div>
      )}
    </div>
  );
};
```

### 5. Usage in Main Settings Page

```jsx
// In your main settings page
const SettingsPage = () => {
  return (
    <div className="settings-page">
      <nav className="settings-nav">
        <Link to="/settings/user">User Settings</Link>
        <Link to="/settings/alert-thresholds">Alert Thresholds</Link>
        <Link to="/settings/notifications">Notifications</Link>
        <Link to="/settings/privacy">Privacy</Link>
      </nav>
      
      <Routes>
        <Route path="/alert-thresholds" element={<AlertThresholdsSettings />} />
        {/* Other routes */}
      </Routes>
    </div>
  );
};
```

### 6. Key Frontend Considerations

1. **Form Validation**: Ensure min < max for temperature and humidity
2. **Loading States**: Show loading indicators when fetching data
3. **Error Handling**: Handle API errors gracefully
4. **Default Values**: Use the defaults from the backend model
5. **Responsive Design**: Make forms work well on mobile devices
6. **Data Persistence**: Save form data locally to prevent loss
7. **Confirmation**: Ask for confirmation before saving changes
8. **Visual Feedback**: Show success/error messages after API calls

### 7. Integration with Alerts System

When implementing the alerts page, you can use these thresholds to:
- Compare sensor data against appropriate thresholds (hive-specific or global)
- Display threshold violations as alerts
- Allow users to adjust thresholds directly from alert details

## Notification Settings
- **Endpoint**: `/api/settings/notification-settings/my_settings/`
- **Methods**: GET, POST, PATCH
- **Fields**:
  - `push_notifications` (boolean, default: TRUE)
  - `email_notifications` (boolean, default: TRUE)
  - `sms_notifications` (boolean, default: FALSE)
  - `alert_sound` (boolean, default: TRUE)
  - `quiet_hours_start` (time, default: '22:00')
  - `quiet_hours_end` (time, default: '06:00')
  - `critical_alerts_override_quiet` (boolean, default: TRUE)
  - `daily_summary_enabled` (boolean, default: TRUE)
  - `daily_summary_time` (time, default: '08:00')

## Data Sync Settings
- **Endpoint**: `/api/settings/data-sync-settings/my_settings/`
- **Methods**: GET, POST, PATCH
- **Fields**:
  - `auto_sync_enabled` (boolean, default: TRUE)
  - `sync_frequency` (string, options: 'Real-time', 'Hourly', 'Daily', default: 'Hourly')
  - `wifi_only_sync` (boolean, default: FALSE)
  - `backup_enabled` (boolean, default: TRUE)
  - `backup_frequency` (string, options: 'Daily', 'Weekly', 'Monthly', default: 'Weekly')
  - `data_retention_days` (integer, default: 365)

## Privacy Settings
- **Endpoint**: `/api/settings/privacy-settings/my_settings/`
- **Methods**: GET, POST, PATCH
- **Fields**:
  - `location_sharing` (boolean, default: FALSE)
  - `analytics_enabled` (boolean, default: TRUE)
  - `crash_reporting` (boolean, default: TRUE)
  - `data_sharing_research` (boolean, default: FALSE)
  - `profile_visibility` (string, options: 'Private', 'Public', 'Community', default: 'Private')
