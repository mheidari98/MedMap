
import logging
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = 'https://api.iranassistance.com/healthcenter/api/v1/HealthCenters'
TYPE_MAPPING = {
    41: 'کلینیک',
    61: 'تصویربرداری',
    1000083: 'عینک سازی',
    1000103: 'جراحی محدود',
    1000104: 'فیزیوتراپی',
    1000105: 'داروخانه',
    1000106: 'آزمایشگاه',
    1000107: 'بیمارستان خصوصی',
    1000108: 'بیمارستان دولتی',
    1000109: 'دندان پزشکی',
    1000123: 'بیمارستان غیر دولتی عمومی',
    1000143: 'مطب',
    1000144: 'خیریه',
    1000166: 'درمانگاه'
}

def fetch_health_centers(city_id=None):
    """
    Fetch health centers data from the API.
    
    Args:
        city_id (int): The ID of the city to filter health centers.
        
    Returns:
        list: A list of health centers data.
    """
    params = {'cityId': city_id} if city_id else {}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    result = data['result']
    logger.info(f"Found {data['rowCount']} centers")
    for i in range(2, data['pageCount'] + 1):
        params['pageNumber'] = str(i)
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            result += response.json()['result']
        else:
            logger.error(f"Failed to fetch page {i}: {response.status_code}")
            break
    return result

def main():
    health_centers = fetch_health_centers()
    df = pd.DataFrame(health_centers)
    df['URL'] = df['id'].apply(lambda x: f'https://iranassistance.com/medical-centers/{x}')
    df['type_name'] = df['typeId'].map(TYPE_MAPPING)
    df.sort_values(by='id').to_csv("medical-centers.csv", encoding='utf-8', index=False, header=True)
    logger.info("Data saved to medical-centers.csv")

if __name__ == "__main__":
    main()