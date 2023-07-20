import datetime
from functools import partial
from utils.utils import get_async_session
from utils.logging_utils import setup_logger
from utils.booking_utils import extract_booking_data


if __name__ == '__main__':
    logger = setup_logger()
    async_session = get_async_session()
    async_session.run(partial(extract_booking_data, datetime.datetime.today(), 3))
