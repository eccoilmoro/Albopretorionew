import functions_framework
import json

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    
    import requests
    from bs4 import BeautifulSoup
    import json
    from datetime import datetime, timedelta

    # Calculate yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')

    # URL of the webpage to scrape
    url = "http://albopretorio.comune.lugo.ra.it/?ente=lugo"

    # Send an HTTP request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the page content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Initialize a list to hold the scraped data
        data_list = []

        # Find the table body containing the rows
        table_body = soup.find('tbody')

        if table_body:
            rows = table_body.find_all('tr')  # find all rows in the table body

            for row in rows:
                cells = row.find_all('td')  # find all table cells
                if len(cells) > 0:
                    # Extract the "date published" field
                    date_published = cells[3].get_text(strip=True)
                    
                    # Only extract rows with "date published" equal to yesterday
                    if date_published == yesterday:
                        # Extract information based on the table structure
                        data = {
                            'id': cells[0].get_text(strip=True),              # 1st column: ID
                            'number': cells[1].get_text(strip=True),          # 2nd column: Number
                            'year': cells[2].get_text(strip=True),            # 3rd column: Year
                            'date_published': date_published,                 # 4th column: Date published
                            'protocol_number': cells[4].get_text(strip=True), # 5th column: Protocol number
                            'description': cells[5].get_text(strip=True),     # 6th column: Description
                            'date_start': cells[6].get_text(strip=True),      # 7th column: Start date
                            'date_end': cells[7].get_text(strip=True),        # 8th column: End date
                            'date_effective': cells[8].get_text(strip=True),  # 9th column: Effective date
                            'status': cells[9].get_text(strip=True),          # 10th column: Status
                            'attachment_link': cells[10].find('img')['onclick'].split("'")[1] if cells[10].find('img') else None  # Extract link from onclick attribute
                        }
                        data_list.append(data)

        # Convert the list of data into a JSON formatted string
        json_output = json.dumps(data_list, indent=4, ensure_ascii=False)

        # Print the output (or you can write to a file)
        print(json_output)

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(name)