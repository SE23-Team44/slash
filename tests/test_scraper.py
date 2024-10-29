"""
Copyright (C) 2023 SE23-Team44
 
Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""


from src.modules import scraper
from src.modules.scraper import driver
from src.modules.app import app
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
current_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
  # Import the app object from your Flask application

def test_filter():
    data = [ {"price": "$10", "rating": "4.5"}, {"price": "$20", "rating": "4.0"}, {"price": "$30", "rating": "3.5"}, {"price": "$40", "rating": "5"} ]
    result = scraper.filter(data, 25, None, None)
    assert len(result) == 2
    result = scraper.filter(data, None, 35, None)
    assert len(result) == 3
    result = scraper.filter(data, None, None, 4.1)
    assert len(result) == 2


@patch('src.modules.scraper.searchWalmart', return_value=[{'name': 'Product 1', 'price': 10, 'title': 'Title 1', 'rating': 4.5}])
@patch('src.modules.scraper.searchEbay', return_value=[{'name': 'Product 2', 'price': 20, 'title': 'Title 2', 'rating': 4.0}])
@patch('src.modules.scraper.searchBestbuy', return_value=[{'name': 'Product 3', 'price': 30, 'title': 'Title 3', 'rating': 3.5}])
def test_driver(mock_bestbuy, mock_ebay, mock_walmart):
    scraper.driver("socks", "inr", website='all')
    scraper.driver("socks", None, csv=True, cd=".", website='all')
    scraper.driver("socks", None, ui=True, csv=True, cd=".", website='all')
    scraper.driver("socks", "USD", ui=True, sort="rades", website='all')
    scraper.driver("socks", None, ui=True, sort="raasc", website='all')
    scraper.driver("socks", None, ui=True, sort="pasc", website='all')
    scraper.driver("socks", None, ui=True, sort="asc", website='all')

"""def test_driver():
    scraper.driver("socks", "inr")
    scraper.driver("socks", None, csv=True, cd=".")
    scraper.driver("socks", None, ui=True, csv=True, cd = ".")
    scraper.driver("socks", "USD", ui=True, sort="rades")
    scraper.driver("socks", None, ui=True, sort="raasc")
    scraper.driver("socks", None, ui=True, sort="pasc")
    scraper.driver("socks", None, ui=True, sort="asc")"""

def test_amazon_scraper():
    products = scraper.searchAmazon('table',False,None)

    if products:
        price = scraper.amazon_scraper(products[0]['link'])
        assert price is None or type(price) == str

def test_walmart_scraper():
    products = scraper.searchWalmart('table',False,None)
    
    if products:
        price = scraper.walmart_scraper(products[0]['link'])
        assert price is None or type(price) == str

def test_ebay_scraper():
    products = scraper.searchEbay('table',False,None)

    if products:
        price = scraper.ebay_scraper(products[0]['link'])
        assert price is None or type(price) == str

def test_bestbuy_scraper():
    products = scraper.searchBestbuy('table',False,None)

    if products:
        price = scraper.bestbuy_scraper(products[0]['link'])
        assert price is None or type(price) == str

def test_google_scraper():
    products = scraper.searchGoogleShopping('table',False,None)

    if products:
        price = scraper.google_scraper(products[0]['link'])
        assert price is None or type(price) == str


# Mock data
mock_products_walmart = [{'name': 'Product 1', 'price': 10}]
mock_products_ebay = [{'name': 'Product 2', 'price': 20}]
mock_products_bestbuy = [{'name': 'Product 3', 'price': 30}]

@patch('src.modules.scraper.searchWalmart', return_value=[{'name': 'Product 1', 'price': 10, 'title': 'Title 1', 'rating': 4.5}])
@patch('src.modules.scraper.searchEbay', return_value=[{'name': 'Product 2', 'price': 20, 'title': 'Title 2', 'rating': 4.0}])
@patch('src.modules.scraper.searchBestbuy', return_value=[{'name': 'Product 3', 'price': 30, 'title': 'Title 3', 'rating': 3.5}])
def test_driver_all(mock_bestbuy, mock_ebay, mock_walmart):
    result = scraper.driver('test_product', 'USD', website='all')
    assert len(result) == 3  # Should return products from all sources

@patch('src.modules.scraper.searchWalmart', return_value=[{'name': 'Product 1', 'price': 10, 'title': 'Title 1', 'rating': 4.5}])
@patch('src.modules.scraper.searchEbay', return_value=[{'name': 'Product 2', 'price': 20, 'title': 'Title 2', 'rating': 4.0}])
@patch('src.modules.scraper.searchBestbuy', return_value=[{'name': 'Product 3', 'price': 30, 'title': 'Title 3', 'rating': 3.5}])
def test_driver_walmart(mock_bestbuy, mock_ebay, mock_walmart):
    result = scraper.driver('test_product', 'USD', website='walmart')
    assert len(result) == 1  # Should return products only from Walmart
    assert result[0]['name'] == 'Product 1'

@patch('src.modules.scraper.searchWalmart', return_value=[{'name': 'Product 1', 'price': 10, 'title': 'Title 1', 'rating': 4.5}])
@patch('src.modules.scraper.searchEbay', return_value=[{'name': 'Product 2', 'price': 20, 'title': 'Title 2', 'rating': 4.0}])
@patch('src.modules.scraper.searchBestbuy', return_value=[{'name': 'Product 3', 'price': 30, 'title': 'Title 3', 'rating': 3.5}])
def test_driver_ebay(mock_bestbuy, mock_ebay, mock_walmart):
    result = scraper.driver('test_product', 'USD', website='ebay')
    assert len(result) == 1  # Should return products only from eBay
    assert result[0]['name'] == 'Product 2'

@patch('src.modules.scraper.searchWalmart', return_value=[{'name': 'Product 1', 'price': 10, 'title': 'Title 1', 'rating': 4.5}])
@patch('src.modules.scraper.searchEbay', return_value=[{'name': 'Product 2', 'price': 20, 'title': 'Title 2', 'rating': 4.0}])
@patch('src.modules.scraper.searchBestbuy', return_value=[{'name': 'Product 3', 'price': 30, 'title': 'Title 3', 'rating': 3.5}])
def test_driver_bestbuy(mock_bestbuy, mock_ebay, mock_walmart):
    result = scraper.driver('test_product', 'USD', website='bestbuy')
    assert len(result) == 1  # Should return products only from Bestbuy
    assert result[0]['name'] == 'Product 3'

@patch('src.modules.scraper.searchWalmart', return_value=[{'name': 'Product 1', 'price': 10, 'title': 'Title 1', 'rating': 4.5}])
@patch('src.modules.scraper.searchEbay', return_value=[{'name': 'Product 2', 'price': 20, 'title': 'Title 2', 'rating': 4.0}])
@patch('src.modules.scraper.searchBestbuy', return_value=[{'name': 'Product 3', 'price': 30, 'title': 'Title 3', 'rating': 3.5}])
def test_driver_invalid(mock_bestbuy, mock_ebay, mock_walmart):
    result = scraper.driver('test_product', 'USD', website='invalid')
    assert len(result) == 0  # Should return no products for invalid website
