from datetime import datetime, timedelta
import urllib.parse

DESTINATION_CODES = {
    "New York": 20088325
}

def create_booking_url(start_date: datetime.date = datetime.today(), 
                       nights: int = 3, 
                       destination: str = "New York",
                       group_adults: int = 2,
                       children: int = 0,
                       number_of_rooms: int = 1,
                       offset: int = 0):
    BOOKING_URL = "https://www.booking.com/searchresults.html?"
    
    url_query = urllib.parse.urlencode(
        {
            "dest_id": DESTINATION_CODES[destination],
            "dest_type": "city",
            "checkin": start_date.strftime('%Y-%m-%d'),
            "checkout": (start_date + timedelta(days=nights)).strftime('%Y-%m-%d'),
            "group_adults": group_adults,
            "no_rooms": number_of_rooms,
            "group_children": children,
            "sb_travel_purpose": "leisure",
            "selected_currency": "ILS",
            "offset": offset
        }
    )
    return BOOKING_URL + url_query

if __name__ == '__main__':
    print(create_booking_url())