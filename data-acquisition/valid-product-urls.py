def extract_shades(html_content):
    """Extract shade data from HTML content."""
    pattern = re.compile(r"'id': '([^']+)',\s*'name': '([^']+)',\s*'description': '([^']+)',\s*'handle': '([^']+)',\s*'hex': '([^']+)',\s*'category': '([^']+)'")
    matches = pattern.findall(html_content)

    shades = []
    for match in matches:
        text = match[1].lower().replace("'", "").replace(" / ", "")
        text = text.split('-', 1)[-1] if '-' in text else text
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        if re.match(r'^#\d+', text):
            text = text.lstrip('#').strip("-")
        shades.append(text)

    return list(set(shades))

def validate_urls(url):
    """Validate generated URLs by checking their existence."""
    try:
        response = requests.get(f'https://fentybeauty.com{url}')
        if response.status_code != 404:
            return url  # Return the URL if it exists
    except requests.exceptions.RequestException as e:
        # Log the error if needed
        print(f"Error checking URL {url}: {e}")
    return None  # Return None if the URL is invalid or an error occurred

def generate_all_urls(dataframe, url_list, target_counts):
    """Generate and validate all possible URLs for products that dont have S"""
    all_urls = {}  # Dictionary to store URLs

    # Iterate through each URL in the product_url column for Fenty Beauty
    for url in dataframe[dataframe['brand'] == 'Fenty Beauty']['product_urls'][0]:
        longest_match = max((shade for shade in url_list if shade in url), key=len, default="")

        # If a matching shade URL is found
        if longest_match:
            key_url, _, extra = url.partition('-' + longest_match)
            base_key = re.sub(r'[^a-zA-Z0-9-]', '', url).rstrip('-')

            if base_key not in all_urls:
                all_urls[base_key] = {"longest_match": set(), "extra": set()}

            all_urls[base_key]["longest_match"].add(longest_match)
            if extra:
                all_urls[base_key]["extra"].add(extra)

            # Categorize shades into numeric, alphanumeric, and alphabetic
            for shade_url in url_list:
                if shade_url not in all_urls[base_key]["longest_match"]:
                    if longest_match.isdigit():
                        if shade_url.isdigit():
                            all_urls[base_key]["longest_match"].add(shade_url)
                    elif any(char.isdigit() for char in longest_match):
                        if any(char.isdigit() for char in shade_url) and not shade_url.isdigit():
                            all_urls[base_key]["longest_match"].add(shade_url)
                    else:
                        if shade_url.isalpha():
                            all_urls[base_key]["longest_match"].add(shade_url)
                            
    #create placeholder for valid urls
    valid_urls = []
    url_set = set()  # Set to track added URLs

    # Collect valid URLs based on conditions
    for key, url_data in all_urls.items():
        for ending in url_data['longest_match']:
            product_url = key + '-' + ending

            # Check if extra exists and has exactly one item
            if url_data['extra'] and len(url_data['extra']) == 1:
                extra = next(iter(url_data['extra']))  # Get the first (and only) item in extra
                product_url = key + '-' + ending + extra

            # Validate the product URL
            test = validate_urls(product_url)
            if test and product_url not in url_set:  # Check for duplicates and None values
                valid_urls.append(test)
                url_set.add(product_url)  # Add to the set to track added URLs

                # Check for product types and stop collecting when the target count is met
                if any(product in key.lower() for product in target_counts.keys()):
                    product_type = next(product for product in target_counts.keys() if product in key.lower())
                    if len(valid_urls) >= target_counts[product_type]:
                        break

        # If the target count is met, break the outer loop as well
        if len(valid_urls) >= target_counts.get(product_type, 0):
            break

    return valid_urls
