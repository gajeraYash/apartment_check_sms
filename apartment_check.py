import time, sys, bs4, json, logging, os
from decouple import config
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from alert import alert

logging.basicConfig(
    format="%(name)s - %(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("{0}_{1}.log".format(config('APTCHECKLOGS'),datetime.now().strftime('%Y%m%d'))),
        logging.StreamHandler()
    ])
logger=logging.getLogger() 
if config("DEBUG",cast=bool):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

wrkdir = os.path.dirname(__file__)
file = open(os.path.join(wrkdir,"apartment_list.json"),"r+")
data = json.load(file)
file.close()
noWindow = Options()
noWindow.headless = True

def checkUpdateNotify(available,apartment,floorplan,unit_id="",jsonBlock=""):
    if available:
        if unit_id in data[apartment]['floorplans'][floorplan]['units']:
            old_data = data[apartment]['floorplans'][floorplan]['units'][unit_id]
            new_data = jsonBlock[unit_id]
            if old_data != new_data:
                data[apartment]['floorplans'][floorplan]['units'].update(jsonBlock)
                print(f"Apartment Update\n{('-'*20)}\nName: {data[apartment]['name']}\nFloorplan: {floorplan}\nUnit#: {jsonBlock[unit_id]['number']}\nSQFT: {jsonBlock[unit_id]['sqft']}\nTerm: {jsonBlock[unit_id]['term']}\nRent: {jsonBlock[unit_id]['rent']}")
        else:
            data[apartment]['floorplans'][floorplan]['units'].update(jsonBlock)
            print(f"Apartment Update\n{('-'*20)}\nName: {data[apartment]['name']}\nFloorplan: {floorplan}\nUnit#: {jsonBlock[unit_id]['number']}\nSQFT: {jsonBlock[unit_id]['sqft']}\nTerm: {jsonBlock[unit_id]['term']}\nRent: {jsonBlock[unit_id]['rent']}")
    else:
        pass

def unavailableUpdateNotify(apartment,floorplan, units):
    storedUnits = list(data[apartment]['floorplans'][floorplan]['units'].keys())
    if len(units) < len(storedUnits):
        for unit in units:
            storedUnits.remove(unit)
        for i in storedUnits:
            alertinfo = data[apartment]['floorplans'][floorplan]['units'][i]
            print(f"Apartment Update\n{('-'*20)}\nName: {data[apartment]['name']}\nFloorplan: {floorplan}\nUnit#: {alertinfo['number']}\nSQFT: {alertinfo['sqft']}\nUNAVAILABLE")
            data[apartment]['floorplans'][floorplan]['units'].pop(i,None)
            
def parcatwylie():
    if config("PROD",cast=bool):
        browser = webdriver.Chrome(executable_path=config("CHROMEDRIVER"))
    else:
        browser = webdriver.Chrome(options=noWindow,executable_path=config("CHROMEDRIVER"))
    apt = data['parcatwylie']
    logging.info(apt)
    url = apt['url']
    logging.info(url)
    browser.get(url)
    time.sleep(5)
    html = browser.page_source
    soup = bs4.BeautifulSoup(html,features="html.parser")
    for i in apt['floorplans']:
        id = apt['floorplans'][i]['id']
        currentUnits = []
        try:
            check = (soup.find("div", {"id":f"floorplan_{id}","data-floorplan-name":f"{i}"})).find("div",{"class":"unit-show-hide"}).text
            if check == 'Available Units':
                units = (soup.find("div", {"id":f"par_{id}"})).find_all("div", {"class":"unit-container"})
                for unit in units:
                    unit_id = unit.get('id')
                    unit_details = soup.find("div", {"id":unit_id})
                    unit_number = unit_details.find("div",{"class":"unit-number"}).text.split()[1]
                    unit_sqft = unit_details.find("div", {"class":"unit-sqft"})
                    unit_available = unit_sqft.find_next_siblings()[0].text.split(":")[1].strip()
                    unit_term = unit_sqft.find_next_siblings()[1].text.split(":")[1].strip()
                    unit_rent = unit_details.find("div", {"class":"unit-rent"}).text.split(":")[1].strip()
                    jsonBlock = {
                        unit_id.replace("unit-",""):{
                            "number":unit_number,
                            "sqft":unit_sqft.text,
                            "available":unit_available,
                            "term":unit_term,
                            "rent":unit_rent
                        }
                    }
                    currentUnits.append(unit_id.replace("unit-",""))
                    checkUpdateNotify(True,'parcatwylie',i,unit_id.replace("unit-",""),jsonBlock)
            else:
                checkUpdateNotify(available=False, apartment='parcatwylie',floorplan=i)
        except Exception as e:
            print(f"Error: {e}")
        unavailableUpdateNotify(apartment='parcatwylie',floorplan=i,units=currentUnits)

if __name__ == "__main__":
    apartment = sys.argv[1]
    if apartment == "parcatwylie":
        logging.info("ARGS: ",apartment)
    parcatwylie()
    
    with open(os.path.join(wrkdir,"apartment_list.json"), 'w') as file:
        json.dump(data,file,indent=4)
       