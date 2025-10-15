# PocketBase Database Setup Guide

## Manual Collection Setup Required

Since the PocketBase instance at `https://steady-park.pockethost.io/` requires admin authentication to create collections, you'll need to set up the collections manually through the PocketBase admin interface.

## Collections to Create

### 1. **sos_alerts** Collection
**Purpose:** Store SOS alerts when drowsiness is detected

**Fields:**
- `taxiid` (Text) - Taxi identifier
- `driverid` (Text) - Driver identifier  
- `details` (Text) - Alert description
- `status` (Select) - Options: "NEW", "ACTIONED"
- `createdtime` (DateTime) - When alert was created
- `actionedtime` (DateTime) - When alert was handled
- `latitude` (Number) - GPS latitude
- `longitude` (Number) - GPS longitude  
- `address` (Text) - Location address

### 2. **users** Collection
**Purpose:** Store driver and admin information

**Fields:**
- `firstname` (Text) - First name
- `lastname` (Text) - Last name
- `type` (Select) - Options: "Driver", "Admin"
- `status` (Select) - Options: "Active", "Inactive"
- `code` (Text) - Employee/Driver code
- `email` (Email) - Email address
- `password` (Text) - Password (will be hashed)

### 3. **taxis** Collection  
**Purpose:** Store taxi/vehicle information

**Fields:**
- `number` (Text) - Taxi number/plate
- `model` (Text) - Vehicle model
- `year` (Text) - Vehicle year
- `status` (Select) - Options: "Active", "Inactive", "Maintenance"

### 4. **sessions** Collection
**Purpose:** Store active driving sessions

**Fields:**
- `taxiid` (Text) - Reference to taxi
- `userid` (Text) - Reference to user/driver
- `starttime` (DateTime) - Session start time
- `endtime` (DateTime) - Session end time  
- `status` (Select) - Options: "Active", "Completed", "Emergency"

## Steps to Set Up:

1. **Access Admin Interface:**
   - Go to: https://steady-park.pockethost.io/_/
   - Log in with admin credentials

2. **Create Collections:**
   - Create each collection above with the specified fields
   - Set appropriate field types and options
   - Configure any validation rules needed

3. **Test Connection:**
   - Run the test script after setup: `python test_db_connection.py`

## Alternative: Use File-Based Storage

If admin access is not available, the application can be modified to use local JSON file storage as a fallback.

## Current Status
- ✅ PocketBase connection working
- ❌ Collections need manual creation via admin interface
- ✅ Application ready to use collections once created