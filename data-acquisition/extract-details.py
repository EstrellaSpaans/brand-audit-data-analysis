def extract_page_details(html_content):
    # Initialize variables
    
    page_details = {
        'text_content': None,
        'images_content': None,
        'meta_title': None,
        'meta_description': None
    }
    
    # Metadata extraction
    for tag in html_content.find_all("meta"):
        if tag.get("property") == "og:title":
            page_details['meta_title'] = tag.get("content", None)
        elif tag.get("property") == "og:description":
            page_details['meta_description'] = tag.get("content", None)
    
    # Extract main content based on various conditions
    main_content = html_content.find('main', {'id': 'main'}) or \
                   html_content.find('main', {'class': 'main', 'id': 'main', 'tabindex': '-1'}) or \
                   html_content.find('main', {'id': 'main', 'class': 'page-wrap', 'role': 'main'})

    if main_content:
        # Extract text content
        content = []
        divs = main_content.find_all('div', id=lambda x: x and 'shopify-section-template' in x)
        
        for div in divs:
            div_text = str(div)  # Convert div to string to handle HTML properly
            
            # Converter to handle HTML properly
            html_convert = html2text.HTML2Text()
            html_convert.ignore_links = True  # Ignore links
            html_convert.ignore_images = True  # Ignore images
            html_convert.ignore_emphasis = True  # Ignore emphasis like * or _
            html_convert.body_width = 0  # Do not wrap text
            clean_text = html_convert.handle(div_text)
            
            # Remove extra symbols and excessive newlines added by html2text
            clean_text = clean_text.replace('* ', '').replace('## ', '').replace('\u200b', '').strip()
            clean_text = ' '.join(line.strip() for line in clean_text.splitlines() if line.strip())
            
            # Format the cleaned text into paragraphs
            paragraphs = clean_text.split('\n')  # Split by paragraphs (assuming paragraphs are separated by newline)
            formatted_text = '\n\n'.join(p.strip() for p in paragraphs if p.strip())  # Join paragraphs with double newlines

            # Add text to list
            content.append(formatted_text)
        
        page_details['text_content'] = list(filter(None, content)) or None
        
        # Extract image information
        image_info = []
        seen_urls = set()

        for img in main_content.find_all('img'):
            # Determine the source of the image
            src = img.get('data-src') or img.get('data-normal') or img.get('src')
            if src and '.svg' not in src:
                # Remove {width} placeholder and normalize URL
                src = src.replace('_{width}x', '')
                src = src.replace('//', 'https://')
                if src not in seen_urls:
                    # Extract alt text or title
                    alt_text = img.get('alt') or img.get('title', '')
                    image_info.append({'url': src, 'alt': alt_text})
                    seen_urls.add(src)
        
        page_details['images_content'] = image_info or None

    return page_details

def extract_product_details(html_content):
    """Extract and parse product data from HTML content."""

    def get_value(*paths):
        # Returns the first non-null value in the given paths
        for path in paths:
            if path:
                return path
        return None

    try:
        # Extracting JSON-LD data from the script tag
        script_tag = html_content.find('script', type='application/ld+json')
        json_content = script_tag.string.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
        json_ld_data = json.loads(json_content) if script_tag else {}

    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"Error extracting product details: {e}")
        return None

    else:
        # Extracting common product details
        product = json_ld_data.get('name', None)
        description = json_ld_data.get('description', None)
        
        # Initialize the consolidated product dictionary
        product_data = {
            "product": product,
            "description": description,
            "variation_urls": [],
            "prices": [],
            "currencies": [],
            "images": [],
            "skus": [],
            "variations": [],
            "rating_values": [],
            "review_counts": []
        }
        
        if 'offers' in json_ld_data:
            for offer in json_ld_data['offers']:
                offer_item = offer.get('itemOffered', {})
                aggregate_rating = offer_item.get('aggregateRating', {})
                
                # Append offer data to the respective lists
                product_data["variation_urls"].append(offer.get('url', None))
                product_data["prices"].append(offer.get('price', None))
                product_data["currencies"].append(offer.get('priceCurrency', None))
                product_data["images"].append(get_value(offer.get('image'), offer_item.get('image'), json_ld_data.get('image')))
                product_data["skus"].append(get_value(offer.get('sku'), offer_item.get('sku'), json_ld_data.get('sku')))
                product_data["variations"].append(get_value(offer_item.get('name')))
                product_data["rating_values"].append(aggregate_rating.get('ratingValue', None))
                product_data["review_counts"].append(aggregate_rating.get('reviewCount', None))

    # Returning the consolidated product data dictionary
    return product_data
