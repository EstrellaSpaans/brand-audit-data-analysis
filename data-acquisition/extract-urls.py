from bs4 import BeautifulSoup
import json

def extract_urls(html_content, website):
    """Extracts product URLs from the given HTML page with Shopify JSON-LD data or fallback to anchor tags."""
    
    urls = []

    # Find the script tag containing JSON-LD data
    script_tag = html_content.find('script', type='application/ld+json')
    
    if script_tag and script_tag.string:
        # Extract the JSON-LD data from the script tag
        json_data = json.loads(script_tag.string)

        if 'mainEntity' in json_data:
            main_entity = json_data['mainEntity']
            
            # Generic URL extraction logic based on common patterns
            if isinstance(main_entity, list):
                for item in main_entity:
                    if 'itemListElement' in item:
                        for sub_item in item['itemListElement']:
                            extracted_url = sub_item.get("url") or sub_item["item"].get("url")
                            if extracted_url:
                                url = '/products' + str(extracted_url).split('/products')[1]
                                urls.append(url)
                    else:
                        extracted_url = item.get('url') or item.get('offers', {}).get('url')
                        if extracted_url:
                            url = '/products' + str(extracted_url).split('/products')[1]
                            urls.append(url)
            else:
                for item in main_entity.get("itemListElement", []):
                    extracted_url = item.get("url") or item["item"].get("url")
                    if extracted_url:
                        url = '/products' + str(extracted_url).split('/products')[1]
                        urls.append(url)
            return urls

    # If JSON-LD extraction fails or is not applicable, use alternative method
    exclusions = ['/collections', '/product', 'hair', 'skin', 'fragrance']
    for a in html_content.find_all('a', href=True):
        href = a['href']
        if href.startswith('/') and not any(exclusion in href for exclusion in exclusions):
            urls.append(href)

    # Remove duplicate URLs
    urls = list(set(urls))
    
    return urls
