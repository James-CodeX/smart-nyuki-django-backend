# Stage 5: Production (Production & Monitoring)

## Models

### Harvests
- **Purpose**: Track harvested products from hives
- **Fields**:
  - `id` (UUID, Primary Key): Auto-generated
  - `hive` (ForeignKey to Hives): Associated hive
  - `harvest_date` (Date): Date the harvest took place
  - `honey_kg` (Decimal): Amount of honey harvested in kg
  - `wax_kg` (Decimal, Optional): Amount of wax harvested in kg
  - `pollen_kg` (Decimal, Optional): Amount of pollen harvested in kg
  - `processing_method` (String, Optional): Method used for processing
  - `harvested_by` (ForeignKey to Users): User who conducted the harvest
  - `quality_notes` (Text, Optional): Notes about harvest quality
  - `created_at` (DateTime): Record creation timestamp

### Alerts
- **Purpose**: Manage alerts and notifications for hives
- **Fields**:
  - `id` (UUID, Primary Key): Auto-generated
  - `hive` (ForeignKey to Hives): Associated hive
  - `alert_type` (Choice): Type of alert (Temperature, Humidity, etc.)
  - `message` (Text): Message describing the alert
  - `severity` (Choice): Severity level (Low, Medium, High, Critical)
  - `trigger_values` (JSON, Optional): Values that triggered alert
  - `is_resolved` (Boolean): Whether the alert has been resolved
  - `resolved_at` (DateTime, Optional): Date and time when resolved
  - `resolved_by` (ForeignKey to Users, Optional): User who resolved the alert
  - `resolution_notes` (Text, Optional): Notes about resolution
  - `created_at` (DateTime): Record creation timestamp

## Endpoints

### Harvests
- **List/Create Harvests**: `GET/POST /api/production/harvests/`
- **Harvest Statistics**: `GET /api/production/stats/`
  - **Purpose**: Provide statistics on user harvests
  - **Authentication**: Required
  - **Response Fields**:
    - `total_statistics`: Total amounts and counts
    - `current_year_statistics`: Statistics for the current year
    - `top_producing_hives`: List of top hives by honey produced
  - **Purpose**: List user's hive harvests or create a new harvest
  - **Authentication**: Required (Bearer token)
  - **GET Query Parameters**:
    - `search` - Search in hive name, processing_method, quality_notes
    - `ordering` - Order by: harvest_date, created_at, honey_kg (add `-` for descending)
  - **POST Required Fields**:
    - `hive`: Hive UUID
    - `harvest_date`: Harvest date (YYYY-MM-DD)
    - `honey_kg`: Honey quantity (kg)

### Alerts
- **List/Create Alerts**: `GET/POST /api/production/alerts/`
- **Alert Statistics**: `GET /api/production/alert-stats/`
  - **Purpose**: Provide statistics on alerts
  - **Authentication**: Required
  - **Response Fields**:
    - `overview`: Overall alert counts
    - `by_severity`: Alerts grouped by severity
    - `by_type`: Alerts grouped by type
  - **Purpose**: List hive alerts or create a new alert
  - **Authentication**: Required (Bearer token)
  - **GET Query Parameters**:
    - `search` - Search in message or resolution_notes
    - `ordering` - Order by: created_at, severity (add `-` for descending)
  - **POST Required Fields**:
    - `hive`: Hive UUID
    - `alert_type`: Type of alert
    - `message`: Alert message
    - `severity`: Severity level

- **Resolve Alert**: `POST /api/production/alerts/{alert_id}/resolve/`
  - **Purpose**: Mark an alert as resolved
  - **Authentication**: Required (Bearer token)
  - **POST Optional Fields**:
    - `resolution_notes`: Notes about how the alert was resolved

- **Resolve All Alerts**: `POST /api/production/alerts/resolve_all/`
  - **Purpose**: Mark all active alerts as resolved for the authenticated user
  - **Authentication**: Required (Bearer token)
  - **POST Optional Fields**:
    - `resolution_notes`: Notes about how all alerts were resolved (default: "Bulk resolved by user")
  - **Response Fields**:
    - `message`: Success message with count of resolved alerts
    - `alerts_resolved`: Number of alerts that were resolved
    - `resolution_notes`: The resolution notes used
    - `timestamp`: When the operation was performed
  - **Example Response**:
    ```json
    {
      "message": "Successfully resolved 5 alerts",
      "alerts_resolved": 5,
      "resolution_notes": "Bulk resolved by user",
      "timestamp": "2025-07-15T12:55:52Z"
    }
    ```
  - **Example Request**:
    ```json
    {
      "resolution_notes": "Checked all hives - issues resolved"
    }
    ```

Please make sure to set up authentication headers and proper permissions before accessing these endpoints.

## Frontend Guide: Handling Hive and Apiary Information

### API Response Fields
The API endpoints now include additional fields to prevent "Unknown Hive" and "Unknown Apiary" issues:

#### Alerts Response Fields:
- `hive_name`: Name of the associated hive
- `apiary_name`: Name of the apiary containing the hive
- `alert_type_display`: Human-readable alert type
- `severity_display`: Human-readable severity level
- `resolved_by_name`: Full name of user who resolved the alert

#### Harvests Response Fields:
- `hive_name`: Name of the associated hive
- `harvested_by_name`: Full name of user who conducted the harvest
- `total_weight_kg`: Calculated total weight of all products

### Example API Response

#### Alert Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "hive": "550e8400-e29b-41d4-a716-446655440001",
  "hive_name": "Hive 1",
  "apiary_name": "Main Apiary",
  "alert_type": "TEMPERATURE",
  "alert_type_display": "Temperature",
  "message": "Temperature too low",
  "severity": "LOW",
  "severity_display": "Low",
  "is_resolved": false,
  "created_at": "2025-07-03T10:38:00Z"
}
```

#### Harvest Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "hive": "550e8400-e29b-41d4-a716-446655440001",
  "hive_name": "Hive 1",
  "harvest_date": "2025-07-03",
  "honey_kg": "15.50",
  "wax_kg": "2.30",
  "pollen_kg": "1.20",
  "total_weight_kg": "19.00",
  "harvested_by_name": "John Doe",
  "created_at": "2025-07-03T10:30:00Z"
}
```

### Frontend Implementation Guide

#### 1. Display Alert Information
```jsx
const AlertItem = ({ alert }) => (
  <div className="alert-item">
    <div className="alert-header">
      <h4>{alert.hive_name || "Unknown Hive"}</h4>
      <span className="apiary-name">{alert.apiary_name || "Unknown Apiary"}</span>
      <span className={`severity-badge severity-${alert.severity.toLowerCase()}`}>
        {alert.severity_display}
      </span>
    </div>
    <div className="alert-details">
      <p><strong>Type:</strong> {alert.alert_type_display}</p>
      <p><strong>Message:</strong> {alert.message}</p>
      <p><strong>Created:</strong> {new Date(alert.created_at).toLocaleString()}</p>
      {alert.is_resolved && (
        <p><strong>Resolved by:</strong> {alert.resolved_by_name}</p>
      )}
    </div>
  </div>
);
```

#### 2. Display Harvest Information
```jsx
const HarvestItem = ({ harvest }) => (
  <div className="harvest-item">
    <div className="harvest-header">
      <h4>{harvest.hive_name || "Unknown Hive"}</h4>
      <span className="harvest-date">{harvest.harvest_date}</span>
    </div>
    <div className="harvest-details">
      <p><strong>Honey:</strong> {harvest.honey_kg} kg</p>
      {harvest.wax_kg && <p><strong>Wax:</strong> {harvest.wax_kg} kg</p>}
      {harvest.pollen_kg && <p><strong>Pollen:</strong> {harvest.pollen_kg} kg</p>}
      <p><strong>Total Weight:</strong> {harvest.total_weight_kg} kg</p>
      <p><strong>Harvested by:</strong> {harvest.harvested_by_name}</p>
    </div>
  </div>
);
```

#### 3. Error Handling
```jsx
// Handle cases where hive/apiary information might be missing
const getDisplayName = (name, fallback = "Unknown") => {
  return name && name.trim() !== "" ? name : fallback;
};

// Usage
<h4>{getDisplayName(alert.hive_name, "Unknown Hive")}</h4>
<span>{getDisplayName(alert.apiary_name, "Unknown Apiary")}</span>
```

#### 4. Fetching Data with Proper Error Handling
```jsx
const fetchAlerts = async () => {
  try {
    const response = await fetch('/api/production/alerts/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.results || data; // Handle paginated vs non-paginated responses
  } catch (error) {
    console.error('Error fetching alerts:', error);
    // Handle error appropriately in your app
    return [];
  }
};
```

### Best Practices

1. **Always provide fallback values** for hive and apiary names to prevent "Unknown" displays
2. **Use the `*_display` fields** for user-facing text instead of raw enum values
3. **Handle null/undefined values** gracefully in your components
4. **Cache hive and apiary data** if you're making frequent requests
5. **Implement proper error boundaries** to handle API failures gracefully

### Troubleshooting

If you're still seeing "Unknown Hive" or "Unknown Apiary":

1. **Check API Response:** Verify that `hive_name` and `apiary_name` are included in the API response
2. **Verify Authentication:** Ensure the user has proper permissions to access hive data
3. **Check Data Relationships:** Verify that alerts/harvests are properly linked to hives and hives are linked to apiaries
4. **Review Frontend Logic:** Ensure your frontend code is accessing the correct field names from the API response
