import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import logging


def scrape_website(comune):
    # Calculate yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')

    data_list=[]

    root_url = "http://albopretorio.comune.lugo.ra.it/";

    # URL of the webpage to scrape
    url = root_url+"?ente="+comune

    # Send an HTTP request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the page content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Initialize a list to hold the scraped data
        data_list = []

        tables = soup.find_all('table')

        # Find the table body containing the rows
        
        
        for table in tables:
            table_body = table.find('tbody')
            if table_body:
                rows = table_body.find_all('tr')  # find all rows in the table body
                caption = ""
                captiontag = table.find_all('caption')
                if captiontag[0]:
                    caption = captiontag[0].get_text(strip=True)
                    #print(caption)
                for row in rows:
                    cells = row.find_all('td')  # find all table cells
                    #print(len(cells))
                    entryType = caption
                    
                    if len(cells) == 10:
                        # Extract the "date published" field
                        try: 
                            date_start = cells[6].get_text(strip=True)
                        except :
                            continue
                        # Only extract rows with "date published" equal to yesterday
                        if date_start == yesterday:
                            # Extract information based on the table structure
                            data = {
                            'id': cells[0].get_text(strip=True),              # 1st column: ID
                            'number': cells[1].get_text(strip=True),          # 2nd column: Number
                            'year': cells[2].get_text(strip=True),            # 3rd column: Year
                            'date_issued': cells[3].get_text(strip=True),  # 4th column: Date published
                            'protocol_number': cells[4].get_text(strip=True), # 5th column: Protocol number
                            'description': cells[5].get_text(strip=True),     # 6th column: Description
                            'date_start': date_start,                         # 7th column: Start date
                            'date_end': cells[7].get_text(strip=True),        # 8th column: End date
                            'date_effective': cells[8].get_text(strip=True),  # 9th column: Effective date
                            'attachment_link': root_url+cells[9].find('img')['onclick'].split("'")[1] if cells[9].find('img') else None,  # Extract link from onclick attribute
                            'type': caption
                            }
                            data_list.append(data)
                    elif len(cells) == 7:
                        # Extract the "date published" field
                        try: 
                            date_start = cells[4].get_text(strip=True)
                        except :
                            continue
                        # Only extract rows with "date published" equal to yesterday
                        if date_start == yesterday:
                            # Extract information based on the table structure
                            data = {
                            'id': cells[0].get_text(strip=True),              # 1st column: ID
                            'protocol_number': cells[1].get_text(strip=True), # 2nd column: Protocol number
                            'type': cells[2].get_text(strip=True),            # 3rd column: Type
                            'description': cells[3].get_text(strip=True),     # 4th column: Description
                            'date_start': date_start,                         # 5th column: Start date
                            'date_end': cells[5].get_text(strip=True),        # 6th column: End date
                            'attachment_link': root_url+cells[6].find('img')['onclick'].split("'")[1] if cells[6].find('img') else None  # Extract link from onclick attribute
                            }
                            data_list.append(data)
    
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    # Convert the list of data into a JSON formatted string
    json_output = json.dumps(data_list, indent=4, ensure_ascii=False)
    return json_output

def post_fb(json_input,comune):

    ACCESS_TOKEN = "AAABrf5Yz1C0BAEWOEg1qAmIWcXbsPdG103fcQg5LSyUjPh1nRWZCvSZAnZBSNtapBZAfkcN50aNAEGgViVDCWSSryviBX3WEMcNEX7Iq42jkjAJBO38H"
    PAGE_ID = "205271689605193"
    POST_URL = f'https://graph.facebook.com/{PAGE_ID}/feed'

    

    # Print the output (or you can write to a file)
    #print(json_input)
    json_data = json.loads(json_input)

    for entry in json_data:
        print(entry)
    # Assign values to variables
        entry_id = entry.get('id', None)
        number = entry.get('number', None)
        year = entry.get('year', None)
        date_issued = entry.get('date_issued', None)
        protocol_number = entry.get('protocol_number', None)
        description = entry.get('description', None)
        date_start = entry.get('date_start', None)
        date_end = entry.get('date_end', None)
        date_effective = entry.get('date_effective', None)
        attachment_link = entry.get('attachment_link', None)
        entry_type = entry.get('type', None)
    
        # Output for debugging or further use
        print(f"ID: {entry_id}")
        print(f"Number: {number}")
        print(f"Year: {year}")
        print(f"Date Issued: {date_issued}")
        print(f"Protocol Number: {protocol_number}")
        print(f"Description: {description}")
        print(f"Date Start: {date_start}")
        print(f"Date End: {date_end}")
        print(f"Date Effective: {date_effective}")
        print(f"Attachment Link: {attachment_link}")
        print(f"Type: {entry_type}")  
        
        msg=""
        msg = msg + "\n**" + comune.upper() +"**" + "\n" + str(entry_type.upper()) + " - " + str(date_start) + "\n" + str(description) + "\n" + "PDF:" + str(attachment_link) + "\n" + "Ref:" + str(protocol_number) + "\n" + "Scade:" + str(date_end)
        print(msg)
        print('-' * 40)  # Separator between entries
        
        id_msg = "abc"
        logging.info("Ready to post :")
        logging.info(msg)   
        messaggio = msg.encode('ascii','ignore')

        
        post_data = {
        'message': messaggio,
        'access_token': ACCESS_TOKEN
        }

        # Send POST request to Facebook Graph API
        response = requests.post(POST_URL, data=post_data)

        # Check the response status
        if response.status_code == 200:
            print(f"Successfully posted entry ID {entry.get('id')} to Facebook!")
        else:
            print(f"Failed to post entry ID {entry.get('id')} to Facebook. Error: {response.text}")

        

if __name__ == '__main__':
    # You can get user input if needed or just run the function
    print("Starting the scraping process...")
    comuni = ["Lugo","Bagnacavallo","Alfonsine","Fusignano","Cotignola","Santagata","Bagnara","Unione"]
    for comune in comuni:
        post_fb(scrape_website(comune),comune)

    # For testing purposes, you can simulate user input like:
    #name = input("Enter a name (or press enter for 'World'): ") or 'World'
    #print(f"Hello {name}!")
