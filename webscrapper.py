from selenium import webdriver
from bs4 import BeautifulSoup

# Can be used for any category of products in the site
BASE_URL = "https://busca.saraiva.com.br/pages/games/playstation-4?page="
ERROR_MENSAGE = "Não localizamos nenhum resultado para:"

def real_to_float(real_str):
    return float(real_str[2:].replace(".", "").replace(",", "."))

class SaraivaCrawler(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.items = []

    def craw_url(self, url):
        page = 1
        while (True):
            self.driver.get(BASE_URL+str(page))
            html = BeautifulSoup(self.driver.page_source, "html.parser")
            if ERROR_MENSAGE in str(html):
                break
            self.items += self.get_products(html)
            page += 1

    def get_products(self, html):
        ul = html.find_all("ul", {"class": "neemu-products-container nm-view-type-grid"})
        return ul.find_all("li")

    def get_products_names(self):
        names = []
        for product in self.items:
            names.append(product.find("h2", {"class": "nm-product-name"}).text.strip("\n"))
        return names

    def get_products_prices(self):
        prices = {
            "base_price": [],
            "pay_up_front_price": [],
        }
        for product in self.items:
            if product.find("div", {"class": "nm-price-container"}) is None:
                prices["base_price"].append("Produto Indisponível")
                prices["pay_up_front_price"].append(None)
            else:
                prices["base_price"].append(real_to_float(product.find("div", {"class": "nm-price-container"}).text.strip("\n")))
                try:
                    prices["pay_up_front_price"].append(real_to_float(product.find_all("strong")[1].text))
                except:
                    prices["pay_up_front_price"].append(None)        
        return prices
