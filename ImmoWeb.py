# -*- coding: utf8 -*-
# Standard library imports
import json
import re
import pathlib
import math
import time
import datetime

# Third party imports
from bs4 import BeautifulSoup
import requests


def set_config_from_json(file_json):
    # Retrieve search configuration from config.json
    with open(file_json) as json_file:
        data = json.load(json_file)
    return data

def set_config_sub_types_mapping_table(config="config/config.json", sub_types="config/sub_types.json", classified_map_table="config/classified_map_table.json"):
    return set_config_from_json(config), set_config_from_json(sub_types), set_config_from_json(classified_map_table)

def prepare_search_page_url(page_nbr):
    # Retrieve Search Page from ImmoWeb in Belgium.
    # Standard, search is on rent apartement.
    search_page = [CONFIG['SEARCHPAGE_IMMOWEB']]
    
    search_page.append("appartement/" if CONFIG['apartement'] else "maison/")
    search_page.append("a-louer?orderBy=newest&countries=BE" if CONFIG['rent'] else "a-vendre?orderBy=newest&countries=BE")
    search_page.append("&page="+str(page_nbr))
    
    # Add criteria (min & max) on Price/Surface/Room
    if isinstance(CONFIG['min_price'],int) and CONFIG['min_price'] > 0:
        search_page.append("&minPrice="+str(CONFIG['min_price']))
    if isinstance(CONFIG['max_price'],int) and CONFIG['max_price'] >0: #Verify if max_price > min_price is needed
        search_page.append("&maxPrice="+str(CONFIG['max_price']))
    if isinstance(CONFIG['min_room'],int) and CONFIG['min_room'] > 0:
        search_page.append("&minBedroomCount="+str(CONFIG['min_room']))
    if isinstance(CONFIG['max_room'],int) and CONFIG['max_room'] > 0: #Verify if max_room > min_room is needed
        search_page.append("&maxBedroomCount="+str(CONFIG['max_room']))
    if isinstance(CONFIG['min_surf'],int) and CONFIG['min_surf'] > 0:
        search_page.append("&minSurface="+str(CONFIG['min_surf']))
    if isinstance(CONFIG['max_surf'],int) and CONFIG['max_surf'] > 0: #Verify if max_surf > min_surf is needed
        search_page.append("&maxSurface="+str(CONFIG['max_surf']))
    
    # Add all postal codes
    CONFIG['postal_code'].sort()
    search_page.append("&postalCodes=BE-"+"%2C".join(str(x) for x in CONFIG['postal_code']))
    
    return ''.join(search_page)

def prepare_classified_page_url(classified):
    # Return the url of a classified
    property_type = SUB_TYPES[classified["property"]["subtype"]] + "/"
    transaction = "a-louer/" if classified["transaction"]["type"] == "FOR_RENT" else "a-vendre/"
    
    return CONFIG['IMMOWEB_CLASSIFIED'] + property_type + transaction + classified["property"]["location"]["locality"].lower() + "/" + classified["property"]["location"]["postalCode"] + "/" + str(classified["id"])

def prepare_search_page_soup(nbr_page):
    # Request the first searchPage and take all the Immoweb Code on this page
    if not TEST:
        search_page = requests.get(prepare_search_page_url(nbr_page),headers=CONFIG['REQUESTS_HEADERS'])
        search_soup = BeautifulSoup(search_page.content, "html.parser")
        
        if SAVE :
            with open("test/search_soup.html", "w", encoding="utf-8") as classified_file:
                classified_file.write(search_soup.prettify())
    else:
        with open('test/search_soup.html','r', encoding="utf-8") as search_file :
            search_page = search_file.read()
        search_soup = BeautifulSoup(search_page,"html.parser")        
    return search_soup

def split_take_first(str_to_split, splitting_str):
    # split a string using splitting_str and return the first element
    return str_to_split.split(splitting_str)[0]

def format_new_classified(classified):
    # replace str in int for integer values
    classified["floor"] = int(classified["floor"]) if "floor" in classified.keys() else 0
    classified["bedrooms"] = int(classified["bedrooms"]) if "bedrooms" in classified.keys() else 0
    classified["bathrooms"] = int(classified["bathrooms"]) if "bathrooms" in classified.keys() else 0
    
    classified["surf"] = int(split_take_first(classified["surf"],"m²")) if "surf" in classified.keys() else 0
    classified["terrasse"] = int(split_take_first(classified["terrasse"],"m²")) if "terrasse" in classified.keys() else 0
    classified["loyer"] = int(split_take_first(classified["loyer"],"€").replace(".","")) if "loyer" in classified.keys() else 0
    classified["charge"] = int(split_take_first(classified["charge"],"€")) if "charge" in classified.keys() else 0
    classified["etat"] = classified["etat"].encode("utf-8").decode("utf-8") if "etat" in classified.keys() else ""
    return classified

def create_new_classified(soup):
    classified_id = str(soup.find("div",class_="classified__information--immoweb-code").string.split(":")[1].strip())
    
    new_classified = {"first_seen": str(datetime.date.today()), "last_seen": str(datetime.date.today())}
    for desktop6 in soup.find_all(class_="desktop--6") :
        for key, values in zip(desktop6.find_all("th"),desktop6.find_all("td")):
            if key.text.strip() in CLASSIFIED_MAP_TABLE:
                new_classified[CLASSIFIED_MAP_TABLE[key.text.strip()]] = " ".join(values.text.split())
    
     # Save the photos in a folder named by the id of the classified
    if CONFIG['photos']:
        # create the folder
        if not pathlib.Path("classifieds/" + classified_id).is_dir():
            pathlib.Path("classifieds/" + classified_id).mkdir(parents=True, exist_ok=True)
        # save pictures if program can reach the pictures
        for picture in json.loads(str(classified_soup.find("script", string=re.compile("{\"pictures\":")).string.split("{\"pictures\":")[1].split(",\"virtualTourUrl\":null")[0])):
            picture_request = requests.get(picture["largeUrl"],headers=CONFIG['REQUESTS_HEADERS'])
            if picture_request.status_code == 200:    
                with open("classifieds/" + classified_id+"/"+picture["largeUrl"].split("/")[-1].split("?")[0], "wb") as f:
                    f.write(picture_request.content)
    
    return format_new_classified(new_classified)

if __name__ == "__main__":
    
    global TEST, SAVE
    TEST = False # True if we are in testing
    SAVE = False
    
    # Load configuration files
    global CONFIG, SUB_TYPES, CLASSIFIED_MAP_TABLE
    CONFIG, SUB_TYPES, CLASSIFIED_MAP_TABLE = set_config_sub_types_mapping_table()
    # Load saved classifieds
    if pathlib.Path("saved_classified.json").exists():
        with open("saved_classified.json", "r") as f:
            saved_classified = json.load(f)
    else:
        saved_classified = {}
    
    search_soup = prepare_search_page_soup(1)
    total_pages = math.ceil(int(str(search_soup.find('iw-search')).split("result-count=\"")[1].split("\"")[0])/30)
        
    for i in range(total_pages):
        print("*** PAGE :"+str(i+1)+" / "+ total_pages)
        search_soup = prepare_search_page_soup(i+1)
        classifieds = json.loads(str(search_soup.find('iw-search')).split("results-storage='")[1].split("' :unique-id")[0])
        
        # Cross ImmoWebCodes to find the new classifieds or update open classifieds
        # If classifieds don't exist no more, nothing to do
        for classified in classifieds:
            if str(classified["id"]) in saved_classified.keys() :
                print(str(classified["id"]) + " already exists")
                saved_classified[str(classified["id"])]["last_seen"] = str(datetime.date.today())
            else:
                print(str(classified["id"]) + " doesn't exist")
                if not TEST:
                    classified_page = requests.get(prepare_classified_page_url(classified),headers=CONFIG['REQUESTS_HEADERS'])
                    classified_soup = BeautifulSoup(classified_page.content,"html.parser")
                    
                    if SAVE : 
                        with open("classifieds/" + str(classified["id"])+".html", "w", encoding="utf-8") as classified_file:
                            classified_file.write(classified_soup.prettify())
                    time.sleep(CONFIG["stop_tim"])
                else:
                    with open("classifieds/" + str(classified["id"])+".html",'r', encoding="utf-8") as classified_file :
                        classified_page = classified_file.read()
                    classified_soup = BeautifulSoup(classified_page,"html.parser")
             
                saved_classified[classified['id']] = create_new_classified(classified_soup)
    
    with open('saved_classified.json', 'w') as fp:
        json.dump(saved_classified, fp,ensure_ascii=False)
#     print(json.dumps(saved_classified,indent=4,ensure_ascii=False))
#     print(str(datetime.date.today()))