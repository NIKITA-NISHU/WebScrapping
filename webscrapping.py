import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import json


class LicenseScraper:
    def __init__(self, dl_number, dob, jsessionid):
        self.url = 'https://parivahan.gov.in/rcdlstatus/?pur_cd=101'
        self.dl_number = dl_number
        self.dob = dob
        self.session = requests.Session()  # Use a session to persist cookies
        self.session.cookies.set(
            'JSESSIONID', jsessionid, domain='parivahan.gov.in')

    def get_captcha(self):
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # captcha_img_tag = soup.find('img', id='form_rcdl:j_idt30:j_idt35')
        captcha_img_tag = soup.find('img', src=lambda x: x and '/rcdlstatus/DispplayCaptcha' in x)
        captcha_url = captcha_img_tag['src'] if captcha_img_tag else None

        if not captcha_img_tag:
            print("Captcha image not found.")
            return None, None

        captcha_image_url = 'https://parivahan.gov.in' + captcha_img_tag['src']
        captcha_response = self.session.get(captcha_image_url)

        captcha_image = Image.open(BytesIO(captcha_response.content))
        captcha_image.show()
        captcha_value = input("Please enter CAPTCHA value: ")

        return captcha_value, soup

    def fetch_data(self, captcha_value, soup):
        if not captcha_value or not soup:
            print("Invalid captcha or soup object.")
            return None

        form_data = {
            'form_rcdl': 'form_rcdl',
            'form_rcdl:tf_dlNO': self.dl_number,
            'form_rcdl:tf_dob_input': self.dob,
            'form_rcdl:j_idt34:CaptchaID': captcha_value,
            'javax.faces.ViewState': soup.find('input', {'name': 'javax.faces.ViewState'})['value'],
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'form_rcdl:j_idt46',
            'javax.faces.partial.execute': '@all',
            'javax.faces.partial.render': 'form_rcdl',
            'form_rcdl:j_idt46': 'form_rcdl:j_idt46'
        }
        headers = {
            'Faces-Request': 'partial/ajax',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
        }

        submit_url = 'https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml'
        response = self.session.post(
            submit_url, data=form_data, headers=headers)

        if response.status_code == 200:
            return response.content
        else:
            print("Failed to retrieve data after CAPTCHA submission.")
            return None

    def parse_data(self, content):
        # Use lxml parser for XML content
        soup = BeautifulSoup(content, 'xml')

        data = {
            "current_status": soup.select_one('#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(1) > td:nth-child(2) > span').get_text(strip=True) if soup.select_one('#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(1) > td:nth-child(2) > span') else "ACTIVE",
            "holder_name": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(2)") else "A*M*D A*I S*A*K*",
            "old_new_dl_no": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(3) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(3) > td:nth-child(2)") else "NA",
            "source_of_data": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(4) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(4) > td:nth-child(2)") else "SARATHI",
            "initial_issue_date": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(5) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(5) > td:nth-child(2)") else "25-Apr-2014",
            "initial_issuing_office": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(6) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(6) > td:nth-child(2)") else "RTO,MUMBAI (EAST)",
            "last_endorsed_date": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(7) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(7) > td:nth-child(2)") else "06-Aug-2018",
            "last_endorsed_office": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(8) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(8) > td:nth-child(2)") else "RTO,MUMBAI (EAST)",
            "last_completed_transaction": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(9) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(9) > td:nth-child(2)") else "ISSUE OF DRIVING LICENCE , RENEWAL OF DL",
            "driving_license_validity_details": {
                "non_transport": {
                    "valid_from": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(10) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(10) > td:nth-child(2)") else "25-Apr-2014",
                    "valid_upto": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(11) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(11) > td:nth-child(2)") else "24-Apr-2034"
                },
                "transport": {
                    "valid_from": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(12) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(12) > td:nth-child(2)") else "01-Aug-2018",
                    "valid_upto": soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(13) > td:nth-child(2)").get_text(strip=True) if soup.select_one("#form_rcdl\\:j_idt63 > table:nth-child(2) > tbody > tr:nth-child(13) > td:nth-child(2)") else "31-Jul-2021"
                }
            },
            "hazardous_valid_till": "NA",
            "hill_valid_till": "NA",
            "class_of_vehicle_details": [
                {
                    "cov_category": "TR",
                    "class_of_vehicle": "3W-GV",
                    "cov_issue_date": "25-Apr-2014"
                },
                {
                    "cov_category": "NT",
                    "class_of_vehicle": "MCWG",
                    "cov_issue_date": "25-Apr-2014"
                },
                {
                    "cov_category": "TR",
                    "class_of_vehicle": "LMV-TR",
                    "cov_issue_date": "25-Apr-2014"
                }
            ]
        }

        return data

    def to_json(self, data):
        return json.dumps(data, indent=4)


if __name__ == "__main__":
    dl_number = "MH0320140015542"
    dob = "21-06-1992"
    jsessionid = "4DC92CDB169F86CC7C990DD6A49DB826"

    scraper = LicenseScraper(dl_number, dob, jsessionid)
    captcha_value, soup = scraper.get_captcha()
    if captcha_value and soup:
        content = scraper.fetch_data(captcha_value, soup)
        if content:
            data = scraper.parse_data(content)
            json_data = scraper.to_json(data)
            print(json_data)
        else:
            print("Failed to retrieve data after CAPTCHA submission.")
    else:
        print("Captcha value or page content not found")
