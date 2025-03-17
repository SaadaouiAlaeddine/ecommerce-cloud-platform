import requests
import logging

STOCK_MS_URL = 'http://localhost:6128'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_all_products_by_category():
    response = requests.get(f'{STOCK_MS_URL}/stock/all-products-by-category')
    if response.status_code != 200:
        logger.error(f"Error while getting all products by category: {response}")
        raise Exception("Error while getting all products")
    return response.json()