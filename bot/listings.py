import os
import requests
import pymongo

mongo_client = pymongo.MongoClient(os.getenv('CLIENT_STRING'))
database = mongo_client['LongLostStakingDatabase']
collection = database['orders']
db = mongo_client['LongLostStakingDatabase']['nftdata']


def fetch_and_process_listings():
    url = "https://api.opensea.io/api/v2/listings/collection/the-long-lost/all"
    headers = {
        "accept": "application/json",
        "x-api-key": os.getenv('OPENSEA')
    }
    list = []
    # Initialize the URL for the first page
    next_page_url = url
    

    while next_page_url:  # While there is a next page URL to fetch
        response = requests.get(next_page_url, headers=headers)
        if response.status_code !=  200:
            print(f"Error fetching page: {response.status_code}")
            break

        result = response.json()
        listings = result["listings"]

        for x in listings:
            protocal_data = x["protocol_data"]
            parameters = protocal_data["parameters"]

            address = parameters["offerer"]
            offer = parameters["offer"]
            offer_data = offer[0]

            dict=  {"address":address, "token":offer_data['identifierOrCriteria']}
            list.append(dict)

        # Check if there is a 'next' field in the response JSON
        # If so, update the next_page_url to the value of the 'next' field
        
         
        
        try:
            next_page_url = url
            next_page_url = next_page_url + "?next=" + result["next"]
        except KeyError:
            # Handle the case where the "next" key is missing
            next_page_url = ""
            return list
        
def totalListed():
    list = fetch_and_process_listings()
    listed = []
    addressCheck = []
    index = 0

    for x in list:
        listedIndex = 0
        rate = 0
        token = x['token']
        myquery = { "nftID": int(token) }
        mydoc = db.find(myquery)
        
        for c in mydoc:
            rate = c["tokenRate"]

        if x["address"] in addressCheck:
            for i in listed:
                if i['address'] == x['address']:
                    dict = listed[listedIndex]
                    current_rate = dict['rate']
                    dict['rate'] = round(current_rate + rate,3)
                    listedIndex = 0

                else:
                    listedIndex = listedIndex + 1

        else: 
            
            listed_dict = {'address':x['address'], 'rate':rate}
            listed.append(listed_dict)
            addressCheck.append(x['address'])

    return listed