# Database Update Required

## New Field Added: `preferred_hospitals`

A new column has been added to the `User` table to support multiple preferred hospitals.

### Run This Command to Update Database

```powershell
python
```

Then in Python:

```python
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

This will add the new `preferred_hospitals` column without affecting existing data.

## Changes Summary

### Button Logic Based on Severity:
- **Pain 1-5**: Only "Order Medicine" button shown
- **Pain 6-8**: Only "Consult Doctor" button shown  
- **Pain 9-10**: "Emergency Alert Sent" badge shown, automatic hospital notification

### Multiple Preferred Hospitals:
- Patients can now add multiple preferred hospitals (comma-separated)
- Emergency alerts sent to ALL preferred hospitals + all nearby hospitals
- Accessible from Health Records page → "Preferred Hospitals for Emergencies" field

### Auto Emergency Trigger:
- When pain level ≥ 9, emergency alert automatically sent
- No manual button click needed
- All hospitals in system notified + preferred hospitals highlighted

## Testing Steps

1. **Update Database** (run commands above)
2. **Login as Patient**
3. **Go to Health Records** → Add preferred hospitals (e.g., "Apollo Hospital, Max Hospital")
4. **Submit Symptoms**:
   - Pain 1-5: See only "Order Medicine"
   - Pain 6-8: See only "Consult Doctor"
   - Pain 9-10: See "Emergency Alert Sent" badge
5. **Check Console**: Emergency logs show which hospitals were notified

## Production Considerations

In production, replace console logs with:
- Email notifications to hospitals
- SMS alerts to emergency contacts
- Push notifications to hospital staff
- Integration with emergency services API
