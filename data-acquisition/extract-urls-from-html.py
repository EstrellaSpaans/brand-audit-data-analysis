def extract_urls_from_html(html_content, website):
    """Extracts URLs from the given HTML page and product urls if Shopify JSON-LD data is present."""
    
    urls = []

    # Find the script tag containing JSON-LD data
    script_tag = html_content.find('script', type='application/ld+json')
    
    if script_tag and script_tag.string:
        # Extract the JSON-LD data from the script tag
        json_data = json.loads(script_tag.string)

        if 'mainEntity' in json_data:
            main_entity = json_data['mainEntity']
            
            # Determine URL extraction logic based on website
            if website == 'rarebeauty.com':
                for item in main_entity["itemListElement"]:
                    extracted_url = item["item"]["url"]
                    url = '/products' + str(extracted_url).split('/products')[1]
                    urls.append(url)
            elif website == 'rembeauty.com':
                for item in main_entity["itemListElement"]:
                    extracted_url = item["url"]
                    url = '/products' + str(extracted_url).split('/products')[1]
                    urls.append(url)
            elif website == 'fentybeauty.com':
                for item in main_entity:
                    extracted_url = item['offers']['url']
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
