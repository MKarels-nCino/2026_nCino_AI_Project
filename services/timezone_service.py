"""Timezone service - Handles timezone-aware calculations"""
from datetime import datetime, timedelta
import pytz
from models.location import Location


class TimezoneService:
    """Service for timezone-aware date/time calculations"""
    
    def __init__(self):
        pass
    
    def get_location_timezone(self, location_id):
        """Get timezone for a location"""
        location = Location.find_by_id(location_id)
        if location:
            return pytz.timezone(location.timezone)
        return pytz.UTC
    
    def now_in_location(self, location_id):
        """Get current time in location's timezone"""
        tz = self.get_location_timezone(location_id)
        return datetime.now(tz)
    
    def to_location_timezone(self, dt, location_id):
        """Convert datetime to location's timezone"""
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        tz = self.get_location_timezone(location_id)
        return dt.astimezone(tz)
    
    def calculate_return_window(self, checkout_time, location_id):
        """
        Calculate return window based on location timezone
        Returns: (expected_return_time, is_weekend)
        - 1 day if Mon-Thu
        - Weekend (until Monday) if Fri-Sun
        """
        tz = self.get_location_timezone(location_id)
        checkout_local = self.to_location_timezone(checkout_time, location_id)
        
        weekday = checkout_local.weekday()  # 0=Monday, 6=Sunday
        
        if weekday < 4:  # Monday (0) through Thursday (3)
            # 1 day return window
            expected_return = checkout_local + timedelta(days=1)
            is_weekend = False
        else:  # Friday (4), Saturday (5), or Sunday (6)
            # Weekend return - return by Monday
            days_until_monday = (7 - weekday) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            expected_return = checkout_local + timedelta(days=days_until_monday)
            # Set to Monday at same time
            expected_return = expected_return.replace(hour=checkout_local.hour,
                                                      minute=checkout_local.minute,
                                                      second=0, microsecond=0)
            is_weekend = True
        
        # Convert back to UTC for storage
        if expected_return.tzinfo is None:
            expected_return = tz.localize(expected_return)
        expected_return_utc = expected_return.astimezone(pytz.UTC)
        
        return expected_return_utc, is_weekend
    
    def is_weekend_in_location(self, dt, location_id):
        """Check if datetime is weekend in location's timezone"""
        tz = self.get_location_timezone(location_id)
        local_dt = self.to_location_timezone(dt, location_id)
        weekday = local_dt.weekday()
        return weekday >= 4  # Friday, Saturday, or Sunday
    
    def format_datetime(self, dt, location_id, format_str='%Y-%m-%d %H:%M %Z'):
        """Format datetime in location's timezone"""
        if dt is None:
            return None
        tz = self.get_location_timezone(location_id)
        local_dt = self.to_location_timezone(dt, location_id)
        return local_dt.strftime(format_str)
    
    def is_unlock_time_passed(self, unlock_time, location_id):
        """Check if unlock time has passed in location's timezone"""
        now = self.now_in_location(location_id)
        unlock_local = self.to_location_timezone(unlock_time, location_id)
        return now >= unlock_local
