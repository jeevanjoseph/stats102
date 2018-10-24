import requests
from bs4 import BeautifulSoup

cars = [{"make":"Honda", "model":"CR-V", "year":"2017", "kbbId":"421734"},
        {"make":"Ford", "model":"Escape", "year":"2017", "kbbId":"415933"},
        {"make":"Toyota", "model":"RAV4", "year":"2017", "kbbId":"421332"}]

def getDataForCar(vehicleId):
    carData = {}
    page = requests.get('https://www.kbb.com/vehicles/hub/_costtoown/?vehicleid='+vehicleId)
    html = BeautifulSoup(page.content, 'html.parser')
    insurance_cost = html.find_all("div",text="Insurance")[0].find_next_sibling().string
    maintenance_cost = html.find_all("div",text="Maintenance")[0].find_next_sibling().string
    depreciation = html.find_all( attrs={"data-modal":"#ctoLossOfValue"})[0].find_parent().find_next_sibling().string
    page = requests.get('https://www.kbb.com/vehicles/hub/_specifications/?vehicleid='+vehicleId)
    html = BeautifulSoup(page.content, 'html.parser')
    fuel_econ = html.find_all("div", class_="icon-specs-fuel")[0].find_next_sibling().find_next_sibling().string
    ## Base Price
    json = requests.get('https://www.kbb.com/Api/3.9.221.0/67021/vehicle/upa/PriceAdvisor/meter.json?action=Get&intent=buy-new&pricetype=FPP&zipcode=94568&vehicleid='+vehicleId+'&hideMonthlyPayment=False').json()
    price = json['data']['apiData']['vehicle']['values']
    base_price = 0
    for pr in price :
       if pr['type'] == 'MSRP':
         base_price = pr['base']
    carData["insurance"] = insurance_cost
    carData["maintenance"] = maintenance_cost
    carData['fuel'] = fuel_econ
    carData['depreciation'] = depreciation
    carData['base'] = base_price
    return carData


def getSafetyRatings(vYear,vMake,vModel):
    json = requests.get('https://api.nhtsa.gov/vehicles/byYmmt?data=crashtestratings,safetyfeatures,recommendedfeatures&modelYear='+vYear+'&make='+vMake+'&model='+vModel+'&trim=SUV&series=FWD&name=').json()
    car_ratings = {}
    for rating in  json['results'][0]['safetyRatings']['crashTestRatings']:
        if rating['type']=='overall':
            for rating_type in rating['ratings']:
                car_ratings[rating_type['position']]=rating_type['rating']
    return car_ratings

for car in cars :
    data = getDataForCar(car["kbbId"])
    safety = getSafetyRatings(car["year"],car["make"],car["model"])
    print ({**car,**data,**safety})

