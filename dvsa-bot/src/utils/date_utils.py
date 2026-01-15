from datetime import datetime, date, time
from typing import List

class DateFilter:
    @staticmethod
    def is_weekday(check_date: date):
        return check_date.weekday() < 5
    
    @staticmethod
    def is_within_range(check_date: date, after: date, before: date):
        return after < check_date < before
    
    @staticmethod
    def is_earlier_than(check_date: date, reference: date):
        return check_date < reference
    
    @staticmethod
    def is_not_disabled(check_date: date, disabled_dates: List[date]):
        return check_date not in disabled_dates
    
    @staticmethod
    def parse_dvsa_date(date_string: str):
        return datetime.strptime(date_string, "%A %d %B %Y %I:%M%p")
    
    @staticmethod
    def is_time_between(begin_time: time, end_time: time, check_time: time = None):
        check_time = check_time or datetime.now().time()
        if begin_time < end_time:
            return begin_time <= check_time <= end_time
        else:
            return check_time >= begin_time or check_time <= end_time
