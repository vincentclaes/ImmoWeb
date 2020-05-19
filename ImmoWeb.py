# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import requests
import math
import time


REQUESTS_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'}
SEARCHPAGE_IMMOWEB = "https://www.immoweb.be/fr/recherche/"

Rent = True # If Rent = True, Louer sinon Acheter
Apartement = True # If Appartement = True, Appartement else Maison
PostalCode = [1090,1083,1070,1020,1081,1080] # Verify if PostalCode exists in Belgium
MinSurf = 50
MaxSurf = 80


# Retrieve Search Page from ImmoWeb in Belgium.
# Standard, search is on rent apartement. 
def serve_search_page(PostalCodes, PageNbr=1, Apartement=True, Rent=True,MinPrice=0, MaxPrice=0, MinRoom=0, MaxRoom=0,MinSurf=0,MaxSurf=0):
    SearchPage = [SEARCHPAGE_IMMOWEB]
    SearchPage.append("appartement/" if Apartement else "maison/")
    SearchPage.append("a-louer?orderBy=newest&countries=BE" if Rent else "a-vendre?orderBy=newest&countries=BE")
    SearchPage.append("&page="+str(PageNbr))
    if isinstance(MinPrice,int) and MinPrice > 0:
        SearchPage.append("&minPrice="+str(MinPrice))
    if isinstance(MaxPrice,int) and MaxPrice >0: #Verify if MaxPrice > MinPrice is needed
        SearchPage.append("&maxPrice="+str(MaxPrice))
    if isinstance(MinRoom,int) and MinRoom > 0:
        SearchPage.append("&minBedroomCount="+str(MinRoom))
    if isinstance(MaxRoom,int) and MaxRoom > 0: #Verify if MaxRoom > MinRoom is needed
        SearchPage.append("&maxBedroomCount="+str(MaxRoom))
    if isinstance(MinSurf,int) and MinSurf > 0:
        SearchPage.append("&minSurface="+str(MinSurf))
    if isinstance(MaxSurf,int) and MaxSurf > 0: #Verify if MaxRoom > MinRoom is needed
        SearchPage.append("&maxSurface="+str(MaxSurf))
    PostalCodes.sort()
    SearchPage.append("&postalCodes=BE-"+"%2C".join(str(x) for x in PostalCodes))
    
    return ''.join(SearchPage)

print(serve_search_page([1090,1070,1083],MinSurf=MinSurf,MaxSurf=MaxSurf))

# Retrieve saved BCE page and prepare it for parsin
def serve_saved_page_soup(file):
    file_bce = open(file,'r')
    if file_bce.mode == 'r':
        contents = file_bce.read()
        file_bce.close()
    return BeautifulSoup(contents.encode('latin-1').decode('utf-8'), 'html.parser')

def verify_existence_company(soup):
    print(soup.h1)
    if soup.h1.string == None:
        return False
    elif soup.h1.string == "Données de l'entité enregistrée":
        return True
    elif soup.h1.string.find("n'existe pas dans la BCE") != -1:
        return False
    else:
        print(soup)
        raise

def retrieve_info_company(soup):
    # Retrieve info if company exists
    if verify_existence_company(soup) == True:
        data = soup.div.table
        #print(data)
        for td in data.find_all('td'):
            if td.string == None:
                continue
            if td.string.find("Statut") != -1:
                status = td.next_sibling.span.string
            elif td.string.find("Situation") != -1:
                legal_situation = td.next_sibling.contents[0].text
                # Date à retravailler avec "Depuis le"
                legal_situation_date = td.next_sibling.contents[2].text
            elif td.string.find("Date de début") != -1:
                # Date à retravailler
                start_date = td.next_sibling.contents[0]
            elif td.string.find("Dénomination") != -1:
                name = td.next_sibling.contents[0]
                # Date à retravailler avec "depuis le"
                name_date = td.next_sibling.contents[2].text.split(",")[1]

            elif td.string.find("Adresse du siège") != -1:
                address_street = readable_text(td.next_sibling.contents[0])
                address_city = readable_text(td.next_sibling.contents[3])
                address_country = readable_text(td.next_sibling.contents[5])
                # Date à retravailler avec "Depuis le"
                address_date = td.next_sibling.contents[6].text
            elif td.string.find("téléphone") != -1:
                phone = td.next_sibling.contents[0]
            elif td.string.find("mail") != -1:
                email = td.next_sibling.contents
            elif td.string.find("entité") != -1:
                entity_type = td.next_sibling.contents[0]
            elif td.string.find("Forme légale") != -1:
                legal_form = readable_text(td.next_sibling.contents[0])
            elif td.string.find("Fonctions") != -1:
                print(td.previous_element.next_sibling.contents[0].contents[0])
                # A verifier
                functions = []
            elif td.string.find("") != -1:
                professional_skills = []
            elif td.string.find("") != -1:
                Licences = []
            elif td.string.find("") != -1:
                VAT_activities = []
                
            

# for i in range(100):
#     bce_number = calculate_next_bce_number(bce_number)
#     print(bce_number)
#     
#     soup = serve_bce_page_soup(bce_number)
#     #print(soup)
#     if verify_existence_company(soup) == True:
#         f = open("bce_number.txt","a+")
#         f.write(bce_number)
#         f.close()
#         f2 = open(bce_number+".html","w+")
#         f2.write(soup.prettify())
#         f2.close()
#     time.sleep(30)