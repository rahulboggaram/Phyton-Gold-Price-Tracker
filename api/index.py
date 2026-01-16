from http.server import BaseHTTPRequestHandler
import json
import cloudscraper
from bs4 import BeautifulSoup
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper()
        try:
            # 1. Fetch the 1g Gold Rate
            res = scraper.get("https://www.bankbazaar.com/gold-rate-india.html")
            soup = BeautifulSoup(res.text, 'html.parser')
            
            gold_1g = 0
            # Target specifically the 24K 1 Gram row
            for row in soup.find_all('tr'):
                text = row.get_text().lower()
                if "24 carat" in text and "1 gram" in text:
                    # eq(1) column logic: get the second cell
                    cells = row.find_all('td')
                    price_str = cells[1].get_text().split('(')[0]
                    gold_1g = int(re.sub(r'[^\d]', '', price_str))
                    break

            # 2. Prepare the JSON response
            data = {
                "success": True,
                "gold_1g": gold_1g,
                "gst_3_percent": round(gold_1g * 0.03),
                "total": round(gold_1g * 1.03),
                "source": "Python Scraper",
                "updated": "Jan 16, 2026"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Important for apps
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.wfile.write(str(e).encode('utf-8'))