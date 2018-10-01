from selenium import webdriver
from bs4 import BeautifulSoup
from pandas import DataFrame
# Can be used for any category of products in the site
BASE_URL = "https://busca.saraiva.com.br/pages/games/playstation-4?page="
ERROR_MENSAGE = "Não localizamos nenhum resultado para:"

def real_to_float(real_str):
    return float(real_str.replace("R$", "").replace(".", "").replace(",", "."))

class SaraivaCrawler(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(options=options)
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
        self.driver.quit()

    def get_products(self, html):
        ul = html.find("ul", {"class": "neemu-products-container nm-view-type-grid"})
        return ul.find_all("li")

    def get_products_names(self):
        names = []
        for product in self.items:
            names.append(product.find("h2", {"class": "nm-product-name"}).text.strip("\n"))
        return names

    def get_products_prices(self):
        prices = {
            "base": [],
            "pay_up_front": [],
            "on_sale": [],
        }
        for product in self.items:
            if product.find("div", {"class": "nm-price-container"}) is None:
                prices["base"].append("Produto Indisponível")
                prices["pay_up_front"].append(None)
                prices["on_sale"].append(False)
            else:
                prices["base"].append(real_to_float(product.find("div", {"class": "nm-price-value"}).text.rstrip()))
                try:
                    prices["pay_up_front"].append(real_to_float(product.find_all("strong")[1].text.rstrip()))
                except:
                    prices["pay_up_front"].append(None)
                if product.find("div",{"class":"nm-flag discount"}):
                    prices["on_sale"].append(True)
                else:
                    prices["on_sale"].append(False)
        return prices
    
    def save_list(self):
        names = self.get_products_names()
        prices = self.get_products_prices()
        df = DataFrame.from_dict(
            {
                'Product Name': names,
                'Base Price': prices["base"],
                'Pay Up Front Price': prices["pay_up_front"],
                'On Sale?': prices["on_sale"]
            }
        )
        cols = ['Product Name', 'Base Price', 'Pay Up Front Price', 'On Sale?']
        df = df[cols]
        df.to_csv('Products_Table.csv', index=False)

crawler = SaraivaCrawler()
crawler.craw_url(BASE_URL)
crawler.save_list()