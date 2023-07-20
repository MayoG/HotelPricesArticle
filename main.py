import datetime
from utils.booking_utils import create_booking_url
from utils.logging_utils import setup_logger
from utils.utils import save_to_json, save_to_csv, load_from_json
from requests_html import AsyncHTMLSession
from functools import partial
import pandas as pd

def extract_data_from_hotel_card(hotel_card):
    hotel_name = hotel_card.find('[data-testid="title"]', first=True).text
    numerical_review_score, verbal_review_score, reviewers_amount = hotel_card.find(
      '[data-testid="review-score"]', first=True).text.split('\n')
    reviewers_amount = int(reviewers_amount.split()[0].replace(',', '')) # Initial value was '123 reviews'
    hotel_page_link = list(hotel_card.find('[data-testid="title-link"]', first=True).absolute_links)[0]
    currency_symbol, price = hotel_card.find('[data-testid="price-and-discounted-price"]', first=True).text.split()
    price = int(price.replace(',', '')) # Remove comas from prices like 5,854
    saving_percentage = hotel_card.find('[data-testid="absolute-savings-percentage"]', first=True)
    if saving_percentage:
      saving_percentage = saving_percentage.text.split('%')[0]

    km_from_center = float(hotel_card.find('[data-testid="distance"]', first=True).text.split()[0])

    return {
       "hotel_name": hotel_name,
       "numerical_review_score": numerical_review_score,
       "verbal_review_score": verbal_review_score, 
       "reviewers_amount": reviewers_amount,
       "hotel_page_link": hotel_page_link,
       "price": price,
       "currency_symbol": currency_symbol,
       "saving_percentage": saving_percentage,
       "km_from_center": km_from_center
    }

def extract_data_from_booking_page(booking_page, page_number: int):
    page_hotels_data = []
    hotels_cards = booking_page.html.find('[data-testid="property-card"]')

    for hotel_order, hotel_card in enumerate(hotels_cards):
        hotel_data = extract_data_from_hotel_card(hotel_card)
        hotel_data['order'] = (page_number - 1) * 25 + hotel_order
        page_hotels_data.append(hotel_data)

    return page_hotels_data

async def extract_booking_data(start_date: datetime.date, nights: int):
    booking_data = []

    first_booking_page_url = create_booking_url(start_date=start_date, nights=nights)
    logger.info(f"Requesting url: {first_booking_page_url}")
    first_booking_page = await async_session.get(first_booking_page_url)

    number_of_pages = int(first_booking_page.html.find('[data-testid="pagination"]', first=True).find('li button')[-1].text)
    logger.info(f"There are {number_of_pages} pages")

    logger.info(f"Extracting data from page number {1}")
    booking_data.extend(extract_data_from_booking_page(first_booking_page, 1))

    # for page_number in range(2, number_of_pages + 1):
    for page_number in range(2, 3):
        booking_page_url = create_booking_url(start_date=start_date, nights=nights, offset=(page_number - 1) * 25)
        
        logger.info(f"Requesting url: {booking_page_url}")
        booking_page = await async_session.get(booking_page_url)
        
        logger.info(f"Extracting data from page number {page_number}")
        booking_data.extend(extract_data_from_booking_page(booking_page, page_number))


    save_to_json(booking_data)


if __name__ == '__main__':
    logger = setup_logger()
    async_session = AsyncHTMLSession()
    
    async_session.run(partial(extract_booking_data, datetime.datetime.today(), 3))

