"""
Copyright (C) 2021 SE Slash - All Rights Reserved
You may use, distribute and modify this code under the
terms of the MIT license.
You should have received a copy of the MIT license with
this file. If not, please write to: secheaper@gmail.com
"""

"""
The scraper module holds functions that actually scrape the e-commerce websites
"""

import logging
from flask import request
import requests
from .formatter import formatSearchQuery,formatResult,getCurrency,sortList
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
import os
from datetime import datetime
from ebaysdk.finding import Connection
import requests

def httpsGet(URL):
    """
    The httpsGet function makes HTTP called to the requested URL with custom headers
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',  # noqa: E501
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache'
    }
    s = requests.Session()
    page = s.get(URL, headers=headers, allow_redirects=False)
    soup1 = BeautifulSoup(page.content, "html.parser")
    return BeautifulSoup(soup1.prettify(), "html.parser")

def searchAmazon(query, df_flag, currency):
    """
    The searchAmazon function scrapes amazon.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on Amazon.com that match the product entered by the user.
    """
    query = formatSearchQuery(query)
    URL = f"https://www.amazon.com/s?k={query}"
    page = httpsGet(URL)
    
    # Log the response content for debugging
    logging.debug(f"Response content: {page.prettify()}")
    
    results = page.findAll("div", {"data-component-type": "s-search-result"})
    logging.debug(f"Found {len(results)} search results")

    products = []
    for res in results:
        try:
            titles = res.select("span.a-text-normal")[0].text.strip() if res.select("span.a-text-normal") else None
            prices = res.select("span.a-price-whole")[0].text.strip() if res.select("span.a-price-whole") else None
            links = res.select("a.a-link-normal")[0]['href'] if res.select("a.a-link-normal") else None
            img_links = res.select("img.s-image")[0]['src'] if res.select("img.s-image") else None
            ratings = res.select("span.a-icon-alt")[0].text.strip() if res.select("span.a-icon-alt") else None
            num_ratings = res.select("span.a-size-base")[0].text.strip() if res.select("span.a-size-base") else None
            trending = res.select("span.a-badge-text")[0].text.strip() if res.select("span.a-badge-text") else None

            product = formatResult(
                "amazon",
                titles,
                prices,
                links,
                ratings,
                num_ratings,
                trending,
                df_flag,
                currency,
                img_links
            )
            products.append(product)
        except Exception as e:
            logging.error(f"Error processing product: {e}")
            continue

    logging.debug(f"Returning {len(products)} products")
    return products

def searchWalmart(query, df_flag, currency):
    """
    The searchWalmart function scrapes walmart.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on walmart.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    URL = f"https://www.walmart.com/search?q={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"data-item-id": True})
    products = []
    pattern = re.compile(r"out of 5 Stars")
    for res in results:
        titles, prices, links = (
            res.select("span.lh-title"),
            res.select("div.lh-copy"),
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "w_iUH7"}, string=pattern)
        num_ratings = res.findAll("span", {"class": "sans-serif gray f7"})
        trending = res.select("span.w_Cs")
        img_links = res.select("div.relative.overflow-hidden img")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "walmart",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_links
        )
        products.append(product)
    return products

def amazon_scraper(link):
    try:
        page = httpsGet(link)

        whole_price = page.select('span.a-price-whole')[0].text.strip()
        numeric_value = re.search(r'\b\d+\b',whole_price)
        if numeric_value:
            numeric_value = numeric_value.group()
            res = page.select('span.a-price-symbol')[0].text.strip() + numeric_value + '.' + page.select('span.a-price-fraction')[0].text.strip()
            return res
        else:
            return None
    
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None
    
def google_scraper(link):
    try:
        page = httpsGet(link)

        res = page.select('span.g9WBQb')[0].text
        return res
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None
    
def walmart_scraper(link):
    try:
        page = httpsGet(link)
        res = page.select('span.inline-flex.flex-column span')[0].text
        pattern = r'(\$\s?\d+\.\d{2})'
        match = re.search(pattern, res)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None

def ebay_scraper(link):
    try:
        page = httpsGet(link)

        res = page.select('div.x-price-primary span')[0].text
        pattern = r'\$\d+(\.\d{1,2})?'
        match = re.search(pattern, res)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None

def bestbuy_scraper(link):
    try:
        page = httpsGet(link)

        res = page.select('div.priceView-hero-price.priceView-customer-price span')[0].text
        return res
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None

def target_scraper(link):
    try:
        page = httpsGet(link)

        res = page.select('span.styles__CurrentPriceFontSize-sc-1mh0sjm-1.bksmYC')[0].text
        return res
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None
    
def searchEtsy(query, df_flag, currency):
    """
    The searchEtsy function scrapes Etsy.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on Etsy.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    url = f"https://www.etsy.com/search?q={query}"
    products = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    for item in soup.findAll(".wt-grid__item-xs-6"):
        str = item.select("a")
        if str == []:
            continue
        else:
            links = str

        ratings=None
        num_ratings=None
       
        titles, prices = (item.select("h3")), (item.select(".currency-value"))
        ratings_text = item.find("div",class_='wt-align-items-center wt-max-height-full wt-display-flex-xs flex-direction-row-xs wt-text-title-small wt-no-wrap')
        
        if ratings_text:
            ratings = ratings_text.get_text().split()[0]
            num_ratings = ratings_text.get_text().split()[1]
        
        trending = item.select("span.wt-badge")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "Etsy",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
        )
        products.append(product)
    
    return products


def searchGoogleShopping(query, df_flag, currency):
    """
    The searchGoogleShopping function scrapes https://shopping.google.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on shopping.google.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    URL = f"https://www.google.com/search?tbm=shop&q={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"class": "sh-dgr__grid-result"})
    results1 = page.find_all()
    products = []
    pattern = re.compile(r"[0-9]+ product reviews")
    for i,res in enumerate(results):
        titles, prices, links = (
            res.select("h3"),
            res.select("span.a8Pemb"),
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "Rsc7Yb"})
        num_ratings=None
        ratings_number = res.find("span", {"class": "QIrs8"}).get_text()
        if ratings_number:
            match = re.search(r'(\d+,\d+)', ratings_number)
            if match:
                num_ratings = match.group(1)
        trending = res.select("span.Ib8pOd")
        img_links = results1[i].select("div.SirUVb.sh-img__image img")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "google",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_links
        )
        products.append(product)
    return products


def searchBJs(query, df_flag, currency):
    """
    The searchBJs function scrapes https://www.bjs.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on bjs.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    URL = f"https://www.bjs.com/search/{query}"
    page = httpsGet(URL)
    # print("page", URL)
    results = page.findAll("div", {"class": "product"})
    products = []
    for res in results:
        titles, prices, links = (
            res.find("p", {"class": "no-select d-none auto-height"}),
            res.select("span.price"),
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "on"})
        num_ratings = res.select("span.prod-comments-count")
        trending = res.select("p.instantSavings")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "bjs", titles, prices, links, "", num_ratings, trending, df_flag, currency
        )
        if len(ratings) != 0:
            product["rating"] = len(ratings)
        products.append(product)
    return products

def searchEbay(query, df_flag, currency):
    """
    The searchEbay function scrapes https://www.ebay.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on ebay.com that match the product entered by the user
    """
    EBAY_APP = 'BradleyE-slash-PRD-2ddd2999f-2ae39cfa'

    try:
        api = Connection(appid=EBAY_APP, config_file=None, siteid='EBAY-US')
        response = api.execute('findItemsByKeywords', {'keywords': query})
    except ConnectionError as e:
        print(e)
        return []

    data = response.dict()

    products = []
    if 'searchResult' in data:
        for p in data['searchResult']['item']:
            
            titles = p['title']
            prices = '$' + p['sellingStatus']['currentPrice']['value']
            links = p['viewItemURL']
            img_link = p['galleryURL']
            ratings = None
            num_ratings = None
            trending = None
            
            product = formatResult(
                "ebay",
                titles,
                prices,
                links,
                ratings,
                num_ratings,
                trending,
                df_flag,
                currency,
                img_link
            )
            products.append(product)

    return products

def searchBestbuy(query, df_flag, currency):
    """
    The searchBestbuy function scrapes bestbuy.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on bestbuy.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    URL = f"https://www.bestbuy.com/site/searchpage.jsp?st={query}"
    page = httpsGet(URL)
    results = page.findAll("li", {'class': 'sku-item'})

    products = []

    pattern = re.compile(r"out of 5 stars with")

    for res in results:
        titles, prices, links = (
            res.select("h4.sku-title a"),
            res.select("div.priceView-customer-price span"),
            res.select("a"),
        )
        ratings = res.find("div", class_="c-ratings-reviews").findAll("p", string=pattern)
        num_ratings = res.select("span.c-reviews")
        trending = None
        img_link = res.select("img.product-image")
        product = formatResult(
            "bestbuy",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_link
        )
        products.append(product)

    return products

def condense_helper(result_condensed, list, num):
    """This is a helper function to limit number of entries in the result"""
    for p in list:
        if num != None and len(result_condensed) >= int(num):
            break
        else:
            if p["title"] != None and p["title"] != "":
                result_condensed.append(p)

def filter(data, price_min = 1, price_max = 100000, rating_min = 1):
    filtered_result = []
    for row in data:
        try:
            price = float(row['price'][1:])
        except:
            price = None
        try:
            rating = float(row['rating'])
        except:
            rating = None
        
        if price_min is not None and (price is None or price < float(price_min)):
            continue
        elif price_max is not None and (price is None or price > price_max):
            continue
        elif rating_min is not None and (rating is None or rating < rating_min):
            continue
        else:
            filtered_result.append(row)
    return filtered_result



def driver(
    product, currency, num=None, df_flag=0, csv=False, cd=None, ui=False, sort=None, website=None):
    """Returns CSV if the user enters the --csv arg,
    else displays the result table in the terminal based on the args entered by the user"""

    # Fetch products from selected sources
    products_2 = searchWalmart(product, df_flag, currency)
    products_6 = searchEbay(product, df_flag, currency)
    products_7 = searchBestbuy(product, df_flag, currency)

    print(f"Selected website: {website}")  # Debugging statement
    
    # Combine results based on the website filter
    if website == 'all' or website is None:
        results = products_2 + products_6 + products_7
    else:
        if website == 'walmart':
            results = products_2
        elif website == 'ebay':
            results = products_6
        elif website == 'bestbuy':
            results = products_7
        else:
            results = []
            
    #print(f"Results structure: {results}")

    # Limit the number of results if specified
    results = results[:num] if num else results

    # Convert to DataFrame for processing
    results_df = pd.DataFrame(results)

    # Drop converted_price if currency is not specified
    if not currency:
        results_df = results_df.drop(columns="converted_price", errors='ignore')

    # Handle CSV output
    if csv:
        file_name = os.path.join(
            cd, f"{product}_{datetime.now():%y%m%d_%H%M}.csv"
        )
        results_df.to_csv(file_name, index=False, header=True)
        print("CSV Saved at:", cd)
        print("File Name:", file_name)
        return results_df  # Return DataFrame directly if CSV is generated

    # UI Processing
    if ui:
        result_condensed = []
        if website == 'all' or website is None:
            condense_helper(result_condensed, products_2, num)
            condense_helper(result_condensed, products_6, num)
            condense_helper(result_condensed, products_7, num)
        else:
            if website == 'walmart':
                condense_helper(result_condensed, products_2, num)
            elif website == 'ebay':
                condense_helper(result_condensed, products_6, num)
            elif website == 'bestbuy':
                condense_helper(result_condensed, products_7, num)

        # Apply currency conversion if specified
        if currency and currency != "USD":
            rate = get_currency_rate('USD', currency)
            for item in result_condensed:
                if item['price']:
                    item['original_price'] = item['price']
                    item['price'] = convert_currency(item['price'], currency, rate)

        # Fix URLs
        for p in result_condensed:
            if "link" in p and "http" not in p["link"]:
                p["link"] = "http://" + p["link"]

        # Sort results if specified
        if sort:
            result_condensed_df = pd.DataFrame(result_condensed)
            result_condensed_df = sortList(result_condensed_df, "ra" if "ra" in sort else "pr", sort.endswith("asc"))
            result_condensed = result_condensed_df.to_dict(orient="records")

        # Output sorted/condensed results to CSV if requested
        if csv:
            result_condensed_df = pd.DataFrame(result_condensed)
            file_name = os.path.join(
                cd, f"{product}_{datetime.now():%y%m%d_%H%M}.csv"
            )
            result_condensed_df.to_csv(file_name, index=False, header=True)
            print("CSV Saved at:", cd)
            print("File Name:", file_name)

    return result_condensed if ui else results_df

def get_currency_rate(from_currency="USD", to_currency="USD"):
    api_key = "f3ac7c18adc2a995e895d289"
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()
    rate = data['rates'][to_currency]
    return rate

def convert_currency(amount, to_currency, rate):
    
            # Remove currency symbol and convert to float
    amount = float(amount.replace('$', '').replace(',', ''))
    converted_amount = amount * rate
    return f"{to_currency} {converted_amount:.2f}"
