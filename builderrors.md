# Build Errors Guide: Frontend Data Structure Issues

## Overview

This guide addresses TypeScript build errors in the frontend related to mismatched data structures between the expected frontend types and the actual API response formats. The errors occur because the frontend expects flat field names while the API returns nested objects.

## Root Cause Analysis

After analyzing the Django backend models and serializers, here are the actual data structures returned by the API:

### 1. AlertsPage.tsx Issues

**Problem**: Frontend expects flat field names, but API returns nested objects

**Current API Response Structure (from AlertsSerializer)**:
```json
{
  "id": "uuid",
  "hive": "uuid",
  "hive_name": "string",
  "apiary_name": "string",
  "alert_type": "string",
  "message": "string",
  "severity": "string",
  "is_resolved": false,
  "created_at": "datetime"
}
```

**Frontend Build Error Solutions**:

❌ **Incorrect (causing errors)**:
```typescript
alert.hive_name  // ✅ This is correct - field exists in serializer
alert.apiary_name // ✅ This is correct - field exists in serializer
```

✅ **Correct Usage**:
```typescript
// These fields are already available in the basic AlertsSerializer
alert.hive_name    // Direct field from serializer
alert.apiary_name  // Direct field from serializer
```

**For detailed view (AlertsDetailSerializer)**:
```typescript
// When using retrieve action, you get nested objects
alert.hive.name           // From nested hive object
alert.hive.apiary.name    // From nested apiary object
```

### 2. HarvestsPage.tsx Issues

**Problem**: Similar nested vs flat field access issues

**Current API Response Structure (from HarvestsSerializer)**:
```json
{
  "id": "uuid",
  "hive": "uuid",
  "hive_name": "string",
  "harvest_date": "date",
  "honey_kg": "decimal",
  "harvested_by": "uuid",
  "harvested_by_name": "string",
  "created_at": "datetime"
}
```

**Frontend Build Error Solutions**:

❌ **Incorrect (causing errors)**:
```typescript
harvest.hive_name?         // ✅ This is correct - field exists
harvest.apiary_name        // ❌ This field doesn't exist in HarvestsSerializer
harvest.harvested_by_name  // ✅ This is correct - field exists
```

✅ **Correct Usage**:
```typescript
// For list view (HarvestsSerializer)
harvest.hive_name          // Direct field from serializer
harvest.harvested_by_name  // Direct field from serializer

// For apiary name - NOT available in basic serializer
// You need to use the detail serializer or modify the serializer

// For detailed view (HarvestsDetailSerializer)
harvest.hive.name              // From nested hive object
harvest.hive.apiary.name       // From nested apiary object
harvest.harvested_by.full_name // From nested user object
```

### 3. assign-device-modal.tsx Issues

**Problem**: Hive object structure access

**Current API Response Structure (from HivesSerializer)**:
```json
{
  "id": "uuid",
  "apiary": "uuid",
  "apiary_name": "string",
  "name": "string",
  "type": "string",
  "has_smart_device": false,
  "is_active": true
}
```

**Frontend Build Error Solutions**:

❌ **Incorrect (causing errors)**:
```typescript
hive.apiary_name  // ✅ This is correct - field exists in serializer
```

✅ **Correct Usage**:
```typescript
// For basic hive data (HivesSerializer)
hive.apiary_name    // Direct field from serializer

// For detailed view (HivesDetailSerializer)
hive.apiary?.name   // From nested apiary object (optional chaining needed)
```

## Solutions by Component

### 1. AlertsPage.tsx - SOLUTION

**Current working approach**:
```typescript
// Use the existing flat fields from AlertsSerializer
alert.hive_name     // ✅ Available
alert.apiary_name   // ✅ Available
```

**No changes needed** - the original frontend code should work as the serializer provides these fields.

### 2. HarvestsPage.tsx - SOLUTION

**Issue**: `apiary_name` field missing from HarvestsSerializer

**Option A: Add apiary_name to HarvestsSerializer (Recommended)**
```python
# In production/serializers.py - HarvestsSerializer
class HarvestsSerializer(serializers.ModelSerializer):
    hive_name = serializers.CharField(source='hive.name', read_only=True)
    apiary_name = serializers.CharField(source='hive.apiary.name', read_only=True)  # Add this line
    harvested_by_name = serializers.CharField(source='harvested_by.full_name', read_only=True)
    total_weight_kg = serializers.ReadOnlyField()
    
    class Meta:
        model = Harvests
        fields = [
            'id', 'hive', 'hive_name', 'apiary_name', 'harvest_date', 'honey_kg',  # Add apiary_name here
            'wax_kg', 'pollen_kg', 'processing_method', 'harvested_by',
            'harvested_by_name', 'quality_notes', 'created_at', 'total_weight_kg'
        ]
```

**Option B: Use detail serializer for harvest list**
```python
# In production/views.py - HarvestsViewSet
def get_serializer_class(self):
    if self.action in ['list', 'retrieve']:  # Use detail serializer for both list and retrieve
        return HarvestsDetailSerializer
    return HarvestsSerializer
```

**Option C: Frontend workaround (if you can't modify backend)**
```typescript
// Use detail endpoint for harvest data
const harvestsResponse = await fetch('/api/harvests/');
// Then for each harvest, fetch detailed data if needed
```

### 3. assign-device-modal.tsx - SOLUTION

**Current working approach**:
```typescript
// Use the existing flat field from HivesSerializer
hive.apiary_name  // ✅ Available in basic serializer
```

**No changes needed** - the original frontend code should work.

## Recommended Backend Changes

### 1. Update HarvestsSerializer (production/serializers.py)

```python
class HarvestsSerializer(serializers.ModelSerializer):
    """Serializer for Harvests model"""
    hive_name = serializers.CharField(source='hive.name', read_only=True)
    apiary_name = serializers.CharField(source='hive.apiary.name', read_only=True)  # Add this
    harvested_by_name = serializers.CharField(source='harvested_by.full_name', read_only=True)
    total_weight_kg = serializers.ReadOnlyField()
    
    class Meta:
        model = Harvests
        fields = [
            'id', 'hive', 'hive_name', 'apiary_name', 'harvest_date', 'honey_kg',
            'wax_kg', 'pollen_kg', 'processing_method', 'harvested_by',
            'harvested_by_name', 'quality_notes', 'created_at', 'total_weight_kg'
        ]
        read_only_fields = ['id', 'harvested_by', 'created_at', 'hive_name', 'apiary_name', 'harvested_by_name', 'total_weight_kg']
```

## Frontend TypeScript Interface Updates

### 1. Alert Interface
```typescript
interface Alert {
  id: string;
  hive: string;
  hive_name: string;
  apiary_name: string;
  alert_type: string;
  message: string;
  severity: string;
  is_resolved: boolean;
  created_at: string;
}
```

### 2. Harvest Interface
```typescript
interface Harvest {
  id: string;
  hive: string;
  hive_name: string;
  apiary_name: string;  // Make sure this is included
  harvest_date: string;
  honey_kg: number;
  harvested_by: string;
  harvested_by_name: string;
  created_at: string;
}
```

### 3. Hive Interface
```typescript
interface Hive {
  id: string;
  apiary: string;
  apiary_name: string;
  name: string;
  type: string;
  has_smart_device: boolean;
  is_active: boolean;
}
```

## Testing the Fix

1. **For Alerts**: No changes needed - should work as is
2. **For Harvests**: Add `apiary_name` field to serializer and test
3. **For Hive Assignment**: No changes needed - should work as is

## API Endpoint Reference

- **Alerts List**: `GET /api/alerts/` - uses `AlertsSerializer`
- **Alerts Detail**: `GET /api/alerts/{id}/` - uses `AlertsDetailSerializer`
- **Harvests List**: `GET /api/harvests/` - uses `HarvestsSerializer`
- **Harvests Detail**: `GET /api/harvests/{id}/` - uses `HarvestsDetailSerializer`
- **Hives List**: `GET /api/hives/` - uses `HivesSerializer`
- **Hives Detail**: `GET /api/hives/{id}/` - uses `HivesDetailSerializer`

## Summary

The main issue is the missing `apiary_name` field in the `HarvestsSerializer`. Once this is added to the backend serializer, all frontend build errors should be resolved. The other components (AlertsPage and assign-device-modal) should already work with the existing serializer structure.
