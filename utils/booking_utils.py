import urllib.parse
from datetime import datetime, timedelta
from utils.logging_utils import get_logger
from utils.utils import get_async_session, Dummy

DESTINATION_CODES = {
    "New York": 20088325
}

class BookingDataExtraction(object):
    def __init__(self, hotel_card, logger, card_number) -> None:
        self.hotel_card = hotel_card
        self.logger = logger
        self.card_number = card_number

    def hotel_name(self) -> dict:
        return {"name": self.hotel_card.find('[data-testid="title"]', first=True).text}
    
    def hotel_reviews(self) -> dict:
        numerical_review_score, verbal_review_score, reviewers_amount = self.hotel_card.find(
        '[data-testid="review-score"]', first=True).text.split('\n')
        reviewers_amount = int(reviewers_amount.split()[0].replace(',', '')) # Initial value was '123 reviews'

        return {
            "numerical_review_score": numerical_review_score,
            "verbal_review_score": verbal_review_score, 
            "reviewers_amount": reviewers_amount
            }
    
    def hotel_page_link(self) -> dict:
        return {
            "page_link": list(self.hotel_card.find('[data-testid="title-link"]', first=True).absolute_links)[0]
            }
    
    def hotel_price(self) -> dict:
        currency_symbol, price = self.hotel_card.find('[data-testid="price-and-discounted-price"]', first=True).text.split()
        price = int(price.replace(',', '')) # Remove comas from prices like 5,854
        
        return {
            "price": price,
            "currency_symbol": currency_symbol
        }
    
    def hotel_saving_percentage(self) -> dict:
        saving_percentage = self.hotel_card.find('[data-testid="absolute-savings-percentage"]', first=True)
        if saving_percentage:
            saving_percentage = saving_percentage.text.split('%')[0]

        return {
            "saving_percentage": saving_percentage
            } 
    
    def hotel_km_from_center(self) -> dict:        
        return {
            "km_from_center": float(self.hotel_card.find('[data-testid="distance"]', first=True).text.split()[0])        
            }

    def hotel_stars(self) -> dict: # stars or squares
        return {
            "stars": int(self.hotel_card.find('div[aria-label$="out of 5"]', first=True).attrs['aria-label'].split()[0])
            }

    def hotel_preferred(self) -> dict: # Include the Like Icon next to the stars
        return {
            "preferred": self.hotel_card.find('[data-testid="preferred-badge"]', first=True) != None
        }

    def extract_data(self):
        data = {}
        extraction_methods = [func for func in dir(BookingDataExtraction) if callable(getattr(BookingDataExtraction, func)) and not func.startswith("__") and not func == 'extract_data']
        for extraction_method in extraction_methods:
            try:
                data.update(getattr(self, extraction_method)())
            except Exception as err:
                self.logger.info(f'Failed to extract {extraction_method} from card No {self.card_number} with error: {err}')

        return data

async_session = get_async_session()

root_logger = get_logger()

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

def extract_data_from_booking_hotel_card(hotel_card, logger, card_number):
    extraction_data = BookingDataExtraction(hotel_card=hotel_card, logger=logger, card_number=card_number)
    return extraction_data.extract_data()

def extract_data_from_booking_page(booking_page, page_number: int, check_in_date: datetime.date, nights: int, logger = Dummy()):
    page_hotels_data = []
    logger.info(f"Starting to extract data")

    hotels_cards = booking_page.html.find('[data-testid="property-card"]')

    for hotel_order, hotel_card in enumerate(hotels_cards):
        try:
            hotel_data = extract_data_from_booking_hotel_card(hotel_card, logger=logger, card_number=hotel_order)
            hotel_data['order'] = (page_number - 1) * 25 + hotel_order
            hotel_data['check_in_day'] = check_in_date.day
            hotel_data['check_in_month'] = check_in_date.month
            hotel_data['check_in_year'] = check_in_date.year
            hotel_data['nights'] = nights
            page_hotels_data.append(hotel_data)
        except Exception as err:
            logger.exception(f'Failed to extract data from card No {hotel_order} with error: {err}')

    return page_hotels_data

async def extract_booking_data(start_date: datetime.date, nights: int, max_page=None):
    logger = root_logger.getChild(f"{start_date.strftime('%Y-%m-%d')}_{nights}_nights")
    booking_data = []

    first_booking_page_url = create_booking_url(start_date=start_date, nights=nights)
    logger.info(f"Requesting url: {first_booking_page_url}")
    first_booking_page = await async_session.get(first_booking_page_url)

    number_of_pages = int(first_booking_page.html.find('[data-testid="pagination"]', first=True).find('li button')[-1].text)
    logger.info(f"There are {number_of_pages} pages")

    booking_data.extend(extract_data_from_booking_page(first_booking_page, 1, start_date, nights, logger.getChild(f"page_{1}")))

    for page_number in range(2, max_page + 1 if max_page and max_page < number_of_pages + 1 else number_of_pages + 1):
        booking_page_url = create_booking_url(start_date=start_date, nights=nights, offset=(page_number - 1) * 25)
        
        logger.info(f"Requesting url: {booking_page_url}")
        booking_page = await async_session.get(booking_page_url)
        
        booking_data.extend(extract_data_from_booking_page(booking_page, page_number, start_date, nights, logger.getChild(f"page_{page_number}")))

    return booking_data
