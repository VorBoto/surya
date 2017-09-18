import argparse
import csv
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape_item_page(url,page_source):
    # Wanted info:
    #  URL_of_Product,SKU,Variants,Description,Image_URL,Collection

    # Instantiate the dictionary of product info
    item_info = {"URL":url,
                 "SKU":"NONE",
                 "Variants": "NONE",
                 "Description":"NONE",
                 "Image_URL":"NONE",
                 "Collection":"NONE"}

    # Create the soup
    soup = BeautifulSoup(page_source,'html.parser')

    # Gather the desired information
    item_info['Collection']  = soup.h1.text.split()[0]
    item_info['SKU']         = soup.h1.text.split()[1]
    item_info['Image_URL']   = soup.find('div',class_="main-image").img['src']
    item_info['Description'] = soup.h1.next_sibling.next_sibling.text.strip().strip("$")
    item_info['Variants']    = []

    # Populate with Variants
    for entry in soup.table.find_all('td',class_="size"):
        item_info['Variants'].append(entry.text.strip())

    return item_info

                                     
if __name__ == "__main__":

    # Setting up the command line info
    parser = argparse.ArgumentParser(description="Gather information about a listing of product SKUs")
    parser.add_argument("input_file",type=str, help="Name of a file containg a list of SKUs")
    args = parser.parse_args()

    # Gather skus into a list
    sku_list = (open(args.input_file,"r").read()).split()

    # Base url for searching
    base_url = "http://www.surya.com/search/?searchtext="

    # CSV file header
    header   = ["URL",
                "SKU",
                "Variants",
                "Description",
                "Image_URL",
                "Collection"]

    # Instantiate output file and the csvwriter
    output = open("sku_information.csv","w")
    csvw = csv.DictWriter(output,fieldnames=header,dialect="unix")
    csvw.writeheader()

    # Instantiate driver
    driver = webdriver.Chrome()
    
    # Loop through the list of skus
    for sku in sku_list:
        
        # Create and go to the search url
        res = requests.get(base_url + sku)

        # Create search soup
        soup = BeautifulSoup(res.text,"html.parser")

        try:
            # Get the url of the item
            item_url = soup.find('div',class_="product").a['href']

            # Navigatge to the item page
            # Should trip the try block here if item_url is a None value
            driver.get(item_url)
        
            # Send the item url and the page_source to the scraping function and write the row
            csvw.writerow(scrape_item_page(item_url,driver.page_source))
        except:
            # In case there is a sku without a valid site
            item_info = {"URL":"NONE",
                         "SKU":sku,
                         "Variants": "NONE",
                         "Description":"NONE",
                         "Image_URL":"NONE",
                         "Collection":"NONE"}
            csvw.writerow(item_info)
            continue


    # Close the selenium session and the ouput file
    driver.close()
    output.close()
