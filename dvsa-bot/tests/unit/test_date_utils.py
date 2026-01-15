import pytest
from datetime import date
from src.utils.date_utils import DateFilter

class TestDateFilter:
    def test_is_weekday(self):
        monday = date(2024, 1, 1)
        saturday = date(2024, 1, 6)
        
        assert DateFilter.is_weekday(monday) == True
        assert DateFilter.is_weekday(saturday) == False
    
    def test_is_within_range(self):
        check_date = date(2024, 6, 15)
        after = date(2024, 6, 1)
        before = date(2024, 6, 30)
        
        assert DateFilter.is_within_range(check_date, after, before) == True
        
        outside_date = date(2024, 7, 1)
        assert DateFilter.is_within_range(outside_date, after, before) == False
