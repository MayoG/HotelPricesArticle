import datetime
from functools import partial
from utils.utils import get_async_session, create_csv
from utils.logging_utils import setup_logger
from utils.booking_utils import extract_booking_data

# NIGHTS_RANGE = (3,6) # 3 to 5
# WEEKS_SKIP_DAYS = [(2, 1), (2, 2), (4, 3)] # First 2 weeks every day, The next two weeks every 2 days, the next 4 weeks every 3 days
# MAX_PAGE = 5

# Test consts
NIGHTS_RANGE = (3,5) 
WEEKS_SKIP_DAYS = [(1,4)]
MAX_PAGE = 2

if __name__ == '__main__':
    setup_logger()
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