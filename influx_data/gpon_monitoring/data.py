import requests
from openpyxl import Workbook

# Define the API URL and headers for fetching building-to-ONU associations
API_URL = 'http://app.sasakonnect.net:13000/api/onus/'
HEADERS = {
    'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
}

# Function to fetch data for a region and save it to an XLSX file
def fetch_and_save_to_xlsx(region, xlsx_filename):
    url = f'http://app.sasakonnect.net:13000/api/onus/{region}'
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()

        # Create a new Excel workbook
        workbook = Workbook()
        worksheet = workbook.active

        # Define the header row
        header = ["BuildingName", "BuildingCode", "Serial_Code", "ClientName", "ClientContact"]
        worksheet.append(header)

        # Write data to the worksheet
        for site in data:
            if site.get('OnuStatus') == 'Installed' and site.get('confirmed_by') is None:
                row = [
                    site.get('BuildingName'),
                    site.get('BuildingCode'),
                    site.get('Serial_Code'),
                    site.get('ClientName'),
                    site.get('ClientContact')
                ]
                worksheet.append(row)

        # Save the workbook to the specified XLSX file
        workbook.save(xlsx_filename)

        print(f"Data saved to {xlsx_filename}")

    else:
        print("Failed to fetch data. Status code:", response.status_code)

# Example: Fetch and save data for the "STN" region to "offline.xlsx"
fetch_and_save_to_xlsx('kwd', 'offline.xlsx')







