import logging
import os
import asyncio
import aiohttp
import pandas as pd
import json
from typing import List, Dict

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

async def fetch_page(session: aiohttp.ClientSession, page: int, city_id: int = None) -> List[Dict]:
    """Fetch a single page of health centers data."""
    params = {'pageNumber': str(page)} if page > 1 else {}
    if city_id:
        params['cityId'] = city_id
    
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data['result']
            else:
                logger.error(f"Failed to fetch page {page}: {response.status}")
                return []
    except Exception as e:
        logger.error(f"Error fetching page {page}: {str(e)}")
        return []

async def fetch_health_centers(city_id=None):
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Get first page to determine total pages
        params = {'cityId': city_id} if city_id else {}
        async with session.get(BASE_URL, params=params) as response:
            initial_data = await response.json()
            total_pages = initial_data['pageCount']
            first_page = initial_data['result']
            
        logger.info(f"Found {initial_data['rowCount']} centers across {total_pages} pages")
        
        # Fetch remaining pages concurrently
        tasks = [fetch_page(session, page, city_id) for page in range(2, total_pages + 1)]
        results = await asyncio.gather(*tasks)
        
        # Combine all results
        all_centers = first_page + [item for page_result in results for item in page_result]
        return all_centers

def save_as_json(health_centers: List[Dict], filename: str):
    """Save health centers data as JSON file optimized for web loading."""
    # Add URL and type_name fields
    for center in health_centers:
        center['URL'] = f'https://iranassistance.com/medical-centers/{center["id"]}'
        center['type_name'] = TYPE_MAPPING.get(center['typeId'], 'Unknown')
    
    # Filter out centers without coordinates
    valid_centers = [center for center in health_centers if center.get('latitude') and center.get('longitude')]
    
    # Save the optimized JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(valid_centers, f, ensure_ascii=False)
    
    logger.info(f"Data saved to {filename}")

async def main():
    health_centers = await fetch_health_centers()
    
    # Save as CSV (keeping original functionality)
    df = pd.DataFrame(health_centers)
    df['URL'] = df['id'].apply(lambda x: f'https://iranassistance.com/medical-centers/{x}')
    df['type_name'] = df['typeId'].map(TYPE_MAPPING)
    df.sort_values(by='id').to_csv("medical-centers.csv", encoding='utf-8', index=False, header=True)
    logger.info("Data saved to medical-centers.csv")
    
    # Ensure docs directory exists then save JSON for static docs
    os.makedirs("docs", exist_ok=True)
    save_as_json(health_centers, "docs/medical-centers.json")
    logger.info("Data saved to docs/medical-centers.json")

if __name__ == "__main__":
    asyncio.run(main())
