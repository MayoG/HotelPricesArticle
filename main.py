import datetime
from functools import partial
from utils.logging_utils import setup_logger
from utils.utils import get_async_session, create_csv
from utils.booking_utils import extract_booking_data, extract_data_from_booking_page

# NIGHTS_RANGE = (3,6) # 3 to 5
# WEEKS_SKIP_DAYS = [(2, 1), (2, 2), (4, 3)] # First 2 weeks every day, The next two weeks every 2 days, the next 4 weeks every 3 days
# MAX_PAGE = 5

# Test constants
NIGHTS_RANGE = (3,5) 
WEEKS_SKIP_DAYS = [(1,4)]
MAX_PAGE = 2

def test():
    from utils.utils import create_csv
    from requests_html import HTMLSession
    session = HTMLSession()
    booking_page = session.get('https://www.booking.com/searchresults.html?label=gen173nr-1FCAQoggI4_gNIM1gEaGqIAQGYATG4ARfIAQzYAQHoAQH4AQOIAgGoAgO4AvLS5qUGwAIB0gIkMTczNGFhYjQtMTRhOC00MjgzLWEyZmYtMjIzOTY2MGY0MGUy2AIF4AIB&aid=304142&ss=New+York&ssne=New+York&ssne_untouched=New+York&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=20088325&dest_type=city&checkin=2023-07-22&checkout=2023-07-25&group_adults=2&no_rooms=1&group_children=0&offset=50')
    results = extract_data_from_booking_page(booking_page, 1, datetime.datetime.today(), 3, x)
    create_csv(results, file_path=f'data/playtest')

def main():
    async_session = get_async_session()
    final_results = []

    for nights in range(*NIGHTS_RANGE):
        data_extraction_functions = []
        current_day = datetime.datetime.today()

        for weeks, skip_days in WEEKS_SKIP_DAYS:
            for _ in range(0, weeks*7, skip_days):
                data_extraction_functions.append(
                    partial(extract_booking_data, current_day, nights, MAX_PAGE)
                )

                current_day += datetime.timedelta(days=skip_days)

        results = async_session.run(*data_extraction_functions) # 31 at the same time
        results = sum(results, [])
        final_results.extend(results)
        create_csv(results, file_path=f'data/{datetime.datetime.today().strftime("%Y-%m-%d")}_{nights}')

    create_csv(final_results, file_path=f'data/{datetime.datetime.today().strftime("%Y-%m-%d")}')

if __name__ == '__main__':
    setup_logger()
    main()