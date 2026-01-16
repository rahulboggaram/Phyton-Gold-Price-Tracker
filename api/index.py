from http.server import BaseHTTPRequestHandler
import json
import cloudscraper
from bs4 import BeautifulSoup
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Use a browser-like scraper to bypass blocks
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        
        try:
            # Indian gold rates often vary slightly; BankBazaar is a stable source
            url = "https://www.bankbazaar.com/gold-rate-india.html"
            res = scraper.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            gold_1g = 0
            
            # 2. Aggressive Search: Find all table rows
            for row in soup.find_all('tr'):
                cells = [c.get_text(strip=True).lower() for c in row.find_all(['td', 'th'])]
                
                # We look for the row that has '24 carat' and '1 gram'
                if any("24 carat" in c for c in cells) and any("1 gram" in c for c in cells):
                    # Usually, the price is in the second or last cell
                    for cell_text in cells:
                        # Find the first cell that looks like a price (contains digits and is > 5000)
                        digits = re.sub(r'[^\d]', '', cell_text)
                        if digits and int(digits) > 5000:
                            gold_1g = int(digits)
                            break
                if gold_1g > 0: break

            # 3. Emergency Fallback: If scraping fails, use a secondary data selector
            if gold_1g == 0:
                # Look for the first 24K price in the entire page text if table parsing failed
                prices = re.findall(r'₹\s?(\d{1,2},?\d{3})', soup.text)
                if prices:
                    gold_1g = int(prices[0].replace(',', ''))

            # 4. Calculation (Jan 16, 2026 rates)
            gst = round(gold_1g * 0.03)
            
            data = {
                "success": True,
                "gold_1g": gold_1g,
                "gst_3_percent": gst,
                "total": gold_1g + gst,
                "source": "Python Advanced Scraper",
                "status": "Live" if gold_1g > 0 else "Fetch Failed"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            self.send_response(200) # Send 200 so the app doesn't crash
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
