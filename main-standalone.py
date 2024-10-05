import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def scrape_website():
    # Calculate yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')

    data_list=[]

    root_url = "http://albopretorio.comune.lugo.ra.it/";

    comune = "Bagnacavallo"

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
                    print(caption)
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

def post_fb(json_input):
    # Print the output (or you can write to a file)
    print(json_input)

if __name__ == '__main__':
    # You can get user input if needed or just run the function
    print("Starting the scraping process...")
    post_fb(scrape_website())

    # For testing purposes, you can simulate user input like:
    #name = input("Enter a name (or press enter for 'World'): ") or 'World'
    #print(f"Hello {name}!")
