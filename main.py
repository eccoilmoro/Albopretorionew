import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
#import logging
import os
from functions_framework import http
from flask import jsonify

@http
def scrape_and_post_fb(request):
    """HTTP Cloud Function to scrape a website and post data to Facebook."""

    comuni = ["Lugo", "Bagnacavallo", "Alfonsine", "Fusignano", "Cotignola", "Santagata", "Bagnara"]

    try:
        for comune in comuni:
            scraped_data = scrape_website(comune)
            post_fb(scraped_data, comune)
        
        return jsonify({"status": "success", "message": f"Data for {', '.join(comuni)} posted to Facebook"}), 200
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def scrape_website(comune):
    """Scrape the website for a specific 'comune' and return data."""
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    data_list = []
    root_url = "http://albopretorio.comune.lugo.ra.it/"
    url = f"{root_url}?ente={comune}"

    # Send an HTTP request to the webpage
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all('table')

        for table in tables:
            table_body = table.find('tbody')
            if table_body:
                rows = table_body.find_all('tr')
                caption = table.find('caption').get_text(strip=True) if table.find('caption') else ""

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 10:
                        try:
                            date_start = cells[6].get_text(strip=True)
                        except:
                            continue

                        if date_start == yesterday:
                            data = {
                                'id': cells[0].get_text(strip=True),
                                'number': cells[1].get_text(strip=True),
                                'year': cells[2].get_text(strip=True),
                                'date_issued': cells[3].get_text(strip=True),
                                'protocol_number': cells[4].get_text(strip=True),
                                'description': cells[5].get_text(strip=True),
                                'date_start': date_start,
                                'date_end': cells[7].get_text(strip=True),
                                'date_effective': cells[8].get_text(strip=True),
                                'attachment_link': root_url+cells[9].find('img')['onclick'].split("'")[1] if cells[9].find('img') else None,  # Extract link from onclick attribute
                                'type': caption
                            }
                            data_list.append(data)
                    elif len(cells) == 7:
                        try:
                            date_start = cells[4].get_text(strip=True)
                        except:
                            continue

                        if date_start == yesterday:
                            data = {
                                'id': cells[0].get_text(strip=True),
                                'protocol_number': cells[1].get_text(strip=True),
                                'type': cells[2].get_text(strip=True),
                                'description': cells[3].get_text(strip=True),
                                'date_start': date_start,
                                'date_end': cells[5].get_text(strip=True),
                                'attachment_link': root_url+cells[6].find('img')['onclick'].split("'")[1] if cells[6].find('img') else None  # Extract link from onclick attribute
                            }
                            data_list.append(data)
    else:
        logging.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        raise Exception(f"Failed to retrieve webpage, status code: {response.status_code}")

    return json.dumps(data_list, ensure_ascii=False)

def post_fb(json_input, comune):
    """Post the scraped data to Facebook using the Graph API."""
    
    ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
    PAGE_ID = os.getenv('FB_PAGE_ID')
    POST_URL = f'https://graph.facebook.com/{PAGE_ID}/feed'

    if not ACCESS_TOKEN or not PAGE_ID:
        raise Exception("Facebook ACCESS_TOKEN or PAGE_ID not set in environment variables")

    json_data = json.loads(json_input)

    for entry in json_data:
        description = entry.get('description', "")
        protocol_number = entry.get('protocol_number', "")
        date_start = entry.get('date_start', "")
        date_end = entry.get('date_end', "")
        attachment_link = entry.get('attachment_link', "")
        entry_type = entry.get('type', "")

        msg = f"\n**{comune.upper()}**\n{entry_type.upper()} - {date_start}\n{description}\nPDF: {attachment_link}\nRef: {protocol_number}\nScade: {date_end}"
        
        post_data = {
            'message': msg,
            'access_token': ACCESS_TOKEN
        }

        response = requests.post(POST_URL, data=post_data)

        if response.status_code != 200:
            logging.error(f"Failed to post entry ID {entry.get('id')} to Facebook. Error: {response.text}")
            raise Exception(f"Failed to post entry to Facebook: {response.text}")

    logging.info(f"Successfully posted data for {comune} to Facebook.")
