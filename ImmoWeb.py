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

class Immoweb:

    REQUESTS_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0"}
    SEARCHPAGE_IMMOWEB = "https://www.immoweb.be/fr/recherche/"
    IMMOWEB_CLASSIFIED = "https://www.immoweb.be/fr/annonce/"

    def set_config_from_json(self,file_json):
        # Retrieve search configuration from config.json
        
        with open(file_json) as json_file:
            data = json.load(json_file)
        return data

    def set_search_critera(self,criteria_file="config/config.json"):
        return self.set_config_from_json(criteria_file)

    def set_sub_types(self,sub_types="config/sub_types.json"):
        return self.set_config_from_json(sub_types)

    def set_mapping_table(self, map_table="config/classified_map_table.json"):
        return self.set_config_from_json(map_table)

    def prepare_search_page_url(self, page_nbr):
        """ Construct a search page URL for ImmoWeb in Belgium.

        Standard, search is on rent apartement."""
        search_page = [self.SEARCHPAGE_IMMOWEB]
            
        search_page.append("appartement/" if self.SEARCH_IMMOWEB['apartement'] else "maison/")
        search_page.append("a-louer?orderBy=newest&countries=BE" if self.SEARCH_IMMOWEB['rent'] else "a-vendre?orderBy=newest&countries=BE")
        search_page.append("&page="+str(page_nbr))
        
        # Add criteria (min & max) on Price/Surface/Room
        if isinstance(self.SEARCH_IMMOWEB['min_price'],int) and self.SEARCH_IMMOWEB['min_price'] > 0:
            search_page.append("&minPrice="+str(self.SEARCH_IMMOWEB['min_price']))
        if isinstance(self.SEARCH_IMMOWEB['max_price'],int) and self.SEARCH_IMMOWEB['max_price'] >0: #Verify if max_price > min_price is needed
            search_page.append("&maxPrice="+str(self.SEARCH_IMMOWEB['max_price']))
        if isinstance(self.SEARCH_IMMOWEB['min_room'],int) and self.SEARCH_IMMOWEB['min_room'] > 0:
            search_page.append("&minBedroomCount="+str(self.SEARCH_IMMOWEB['min_room']))
        if isinstance(self.SEARCH_IMMOWEB['max_room'],int) and self.SEARCH_IMMOWEB['max_room'] > 0: #Verify if max_room > min_room is needed
            search_page.append("&maxBedroomCount="+str(self.SEARCH_IMMOWEB['max_room']))
        if isinstance(self.SEARCH_IMMOWEB['min_surf'],int) and self.SEARCH_IMMOWEB['min_surf'] > 0:
            search_page.append("&minSurface="+str(self.SEARCH_IMMOWEB['min_surf']))
        if isinstance(self.SEARCH_IMMOWEB['max_surf'],int) and self.SEARCH_IMMOWEB['max_surf'] > 0: #Verify if max_surf > min_surf is needed
            search_page.append("&maxSurface="+str(self.SEARCH_IMMOWEB['max_surf']))
        
        # Add all postal codes
        if isinstance(self.SEARCH_IMMOWEB['postal_code'],list):
            self.SEARCH_IMMOWEB['postal_code'].sort()
            search_page.append("&postalCodes=BE-"+"%2C".join(str(x) for x in self.SEARCH_IMMOWEB['postal_code']))
        else:
            search_page.append("&postalCodes=BE-"+str(self.SEARCH_IMMOWEB['postal_code']))
        
        return ''.join(search_page)

    def prepare_classified_page_url(self,classified):
        """Prepare an URL for a specific classified from ImmoWeb."""
        property_type = self.SUB_TYPES[classified["property"]["subtype"]] + "/"
        transaction = "a-louer/" if classified["transaction"]["type"] == "FOR_RENT" else "a-vendre/"
        
        return self.IMMOWEB_CLASSIFIED + property_type + transaction + classified["property"]["location"]["locality"].lower() + "/" + classified["property"]["location"]["postalCode"] + "/" + str(classified["id"])

    def prepare_search_page_soup(self,nbr_page):
        """ Retrieve a search page and return a BeautifulSoup page."""
        # return the searchPage
        search_page = requests.get(self.prepare_search_page_url(nbr_page),headers=self.REQUESTS_HEADERS)
        search_soup = BeautifulSoup(search_page.content, "html.parser")

        return search_soup

    def split_take_first(self,str_to_split, splitting_str):
        """Split a string using splitting_str and return the first element."""
        return str_to_split.split(splitting_str)[0]

    def format_new_classified(self,classified):
        """Replace str in int for integer values ."""
        classified["floor"] = int(classified["floor"]) if "floor" in classified.keys() else 0
        classified["bedrooms"] = int(classified["bedrooms"]) if "bedrooms" in classified.keys() else 0
        classified["bathrooms"] = int(classified["bathrooms"]) if "bathrooms" in classified.keys() else 0
        
        classified["surf"] = int(self.split_take_first(classified["surf"],"m²")) if "surf" in classified.keys() else 0
        classified["terrasse"] = int(self.split_take_first(classified["terrasse"],"m²")) if "terrasse" in classified.keys() else 0
        classified["loyer"] = int(self.split_take_first(classified["loyer"],"€").replace(".","")) if "loyer" in classified.keys() else 0
        classified["charge"] = int(self.split_take_first(classified["charge"],"€")) if "charge" in classified.keys() else 0
        classified["etat"] = classified["etat"].encode("utf-8").decode("utf-8") if "etat" in classified.keys() else ""
        return classified

    def create_new_classified(self,soup):
        classified_id = str(soup.find("div",class_="classified__information--immoweb-code").string.split(":")[1].strip())
        
        
        new_classified = {"first_seen": str(datetime.date.today()), "last_seen": str(datetime.date.today())}

        # Localisation
        localisation = eval((soup.find("div",class_="classified").find("script").string.split("property\":")[1].split("location\":")[1].split(",\"box\"")[0] +"}").replace("null","None"))
        new_classified["postal_code"] = localisation["postalCode"]
        new_classified["street"] = localisation["street"]
        new_classified["number"] = localisation["number"]
        
        try:
            new_classified["description"] = soup.find("p",class_="classified__description").string.strip()
        except AttributeError:
            new_classified["description"] = None

        for desktop6 in soup.find_all(class_="desktop--6") :
            for key, values in zip(desktop6.find_all("th"),desktop6.find_all("td")):
                try:
                    new_classified[self.CLASSIFIED_MAP_TABLE[key.text.strip()]] = " ".join(values.text.split())
                except KeyError:
                    pass                    
        
         # Save the photos in a folder named by the id of the classified
        if self.SEARCH_IMMOWEB['photos']:
            # create the folder
            if not pathlib.Path("classifieds/" + classified_id).is_dir():
                pathlib.Path("classifieds/" + classified_id).mkdir(parents=True, exist_ok=True)
            # save pictures if program can reach the pictures
            for picture in json.loads(str(classified_soup.find("script", string=re.compile("{\"pictures\":")).string.split("{\"pictures\":")[1].split(",\"virtualTourUrl\":null")[0])):
                picture_request = requests.get(picture["largeUrl"],headers=self.REQUESTS_HEADERS)
                if picture_request.status_code == 200:    
                    with open("classifieds/" + classified_id+"/"+picture["largeUrl"].split("/")[-1].split("?")[0], "wb") as f:
                        f.write(picture_request.content)
        
        return self.format_new_classified(new_classified)
    
    
    def __init__(self):
        self.SEARCH_IMMOWEB = self.set_search_critera()
        self.SUB_TYPES = self.set_sub_types()
        self.CLASSIFIED_MAP_TABLE = self.set_mapping_table()
        



if __name__ == "__main__":
    nbr_saved_classified = 0
    nbr_new_classified = 0
    nbr_updated_classified = 0
    
    immo = Immoweb()
    
    # Save number of classified in Brussels in a separate file
    if not pathlib.Path(str(datetime.date.today())+".json").exists():
        total_classified = {}
        postal_codes = [1000,1020,1030,1040,1050,1060,1070,1080,1081,1082,1083,1090,1120,1130,1140,1150,1160,1170,1180,1190,1200,1210]

        for postal_code in postal_codes:
            immo.SEARCH_IMMOWEB["postal_code"] = postal_code
            search_soup = immo.prepare_search_page_soup(1)
            total_classified[postal_code] = int(str(search_soup.find('iw-search')).split("result-count=\"")[1].split("\"")[0])
            print(str(postal_code) + " : " + str(total_classified[postal_code]))
#             time.sleep(immo.SEARCH_IMMOWEB["time_search_page"])
        
        with open(str(datetime.date.today())+'.json', 'w') as fp:
            json.dump(total_classified, fp,ensure_ascii=False)
        print(sum(total_classified.values()))
    else:
        print(str(datetime.date.today()))
        
    exit()
    # Load saved classifieds
    if pathlib.Path("saved_classified.json").exists():
        with open("saved_classified.json", "r") as f:
            saved_classified = json.load(f)
            nbr_saved_classified = len(saved_classified)
    else:
        saved_classified = {}
    
    search_soup = immo.prepare_search_page_soup(1)
    total_pages = math.ceil(int(str(search_soup.find('iw-search')).split("result-count=\"")[1].split("\"")[0])/30)
        
    for i in range(total_pages):
        print("*** PAGE : "+str(i+1)+" / "+ str(total_pages) + " **")
        search_soup = immo.prepare_search_page_soup(i+1)
        classifieds = json.loads(str(search_soup.find('iw-search')).split("results-storage='")[1].split("' :unique-id")[0])
        
        # Cross ImmoWebCodes to find the new classifieds or update open classifieds
        # If classifieds don't exist no more, nothing to do
        for classified in classifieds:
            id = str(classified["id"])
            if id in saved_classified.keys() :
                print(id + " already exists")
                saved_classified[id]["last_seen"] = str(datetime.date.today())
                nbr_updated_classified += 1
            else:
                print(id + " doesn't exist")

                classified_page = requests.get(immo.prepare_classified_page_url(classified),headers=immo.REQUESTS_HEADERS)
                classified_soup = BeautifulSoup(classified_page.content,"html.parser")
                
                if immo.SEARCH_IMMOWEB['save'] : 
                    with open("classifieds/" + id+".html", "w", encoding="utf-8") as classified_file:
                        classified_file.write(classified_soup.prettify())
                            
                saved_classified[id] = immo.create_new_classified(classified_soup)
                nbr_new_classified += 1

#                 time.sleep(immo.SEARCH_IMMOWEB["time_classified"])
#         time.sleep(immo.SEARCH_IMMOWEB["time_search_page"])

    with open('saved_classified.json', 'w') as fp:
        json.dump(saved_classified, fp,ensure_ascii=False)
        
    print("""****\n\nThere are {} classified :\n - {} new classified \n - {} updated classified \n - {} out dated classified"""
              .format(len(saved_classified),nbr_new_classified, nbr_updated_classified, nbr_saved_classified - nbr_updated_classified))