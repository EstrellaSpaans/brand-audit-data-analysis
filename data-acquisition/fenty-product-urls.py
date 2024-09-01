import re
import requests
from collections import Counter

def extract_shades(html_content):
    """Extract shade data from HTML content and organize them into a dictionary grouped by specific prefixes."""
    
    # Regular expression pattern to extract necessary details from the HTML content
    pattern = re.compile(r"'id': '([^']+)',\s*'name': '([^']+)',\s*'description': '([^']+)',\s*'handle': '([^']+)',\s*'hex': '([^']+)',\s*'category': '([^']+)'")
    matches = pattern.findall(html_content)

    shades_dict = {}

    for match in matches:
        # Extract prefix and group by the first 5 characters of the 'id'
        prefix = match[0][:4]
        group = match[0][:5]  
        
        # Generate a URL-friendly version of the product name
        url_var = match[1].lower().replace("'", "").replace(" / ", "")
        url_var = url_var.split('-', 1)[-1] if '-' in url_var else url_var
        url_var = re.sub(r'[^a-z0-9\s-]', '', url_var)
        url_var = re.sub(r'[\s-]+', '-', url_var)
        
        # Remove any leading '#' character in the URL variable
        if re.match(r'^#\d+', url_var):
            url_var = url_var.lstrip('#').strip("-")
        
        # Initialize the dictionary structure for the prefix and group if not already present
        if prefix not in shades_dict:
            shades_dict[prefix] = {}
        if group not in shades_dict[prefix]:
            shades_dict[prefix][group] = {'names': [], 'urls': []}
        
        # Ensure the names and URLs are distinct within each group
        if match[1] not in shades_dict[prefix][group]['names']:
            shades_dict[prefix][group]['names'].append(match[1])
        if url_var not in shades_dict[prefix][group]['urls']:
            shades_dict[prefix][group]['urls'].append(url_var)
            
    return shades_dict

def validate_urls(url):
    """Validate generated URLs by checking their existence through an HTTP GET request."""
    try:
        response = requests.get(f'https://{url}')
        if response.status_code != 404:
            return url  # Return the URL if it exists
    except requests.exceptions.RequestException as e:
        # Log the error if needed
        print(f"Error checking URL {url}: {e}")
    return None  # Return None if the URL is invalid or an error occurred

def intersection(lst1, lst2):
    """
    Returns a list of elements that are common between two input lists.
    """
    
    return [value for value in lst1 if value in lst2]

def is_contiguous_sublist(sublist, main_list):
    """
    Checks if a given sublist is a contiguous sublist of the main list.
    """
    if not sublist:
        return False
    sublist_len = len(sublist)
    # Check if the sublist exists as a contiguous segment in the main list
    return any(sublist == main_list[i:i + sublist_len] for i in range(len(main_list) - sublist_len + 1))

def find_longest_common_prefix(strings):
    """
    Finds the longest common prefix string amongst an array of strings.
    """
    if not strings:
        return ""
    shortest_string = min(strings, key=len)
    # Compare characters one by one across all strings
    for i, char in enumerate(shortest_string):
        for other in strings:
            if other[i] != char:
                return shortest_string[:i]
    return shortest_string

def identify_product_variation(product_urls):
    """
    Identifies product variations from a list of product URLs by grouping them based on common URL components.
    """
    
    # Split URLs into components for easier comparison
    main_list = []
    for i in product_urls: 
        splitted_url = i.split('products/')[-1].split('-')
        main_list.append(splitted_url)

    # Create two lists of the main list to compare them against each other to make groups
    list_1 = main_list
    list_2 = main_list

    final_urls = {}  # Placeholder for the final grouped URLs

    # Loop through the first list to compare against the second list
    x = 0
    while x < len(list_1):
        
        overlap_dict = {}  # Temporary dictionary to save overlap counts
    
        # Compare each item in the second list against the current item in the first list
        for i in range(len(list_2)):
            overlap = intersection(list_1[x], list_2[i])
            overlap_length = len(overlap)
    
            # Skip if the URLs are the same 
            if overlap_length == len(list_1[x]):
                pass
        
            # Overlaps lower/equal to 3 are not considered significant groups
            elif overlap_length < 3:
                pass
        
            # Add the overlap to the temporary dictionary
            elif overlap_length in overlap_dict:
                overlap_dict[overlap_length].append(overlap)
            else:
                overlap_dict[overlap_length] = [overlap]

        # If there is no overlap, then URL becomes its own group
        if not overlap_dict:
            key = '-'.join(list_1[x])
            final_urls[key] = ['-'.join(list_1[x])]
            x += 1
            continue  # Move to the next item in list_1

        # Select the group with the highest overlap
        max_key = max(overlap_dict.keys())
        list_counter = Counter(map(tuple, overlap_dict[max_key]))
        most_common_list = list_counter.most_common(1)[0][0]
        most_common_list_as_list = list(most_common_list)

        # Get all the URLs that belong to this group
        matching_items = set()
        for item in list_2:
            if is_contiguous_sublist(most_common_list_as_list, item):
                matching_items.add('-'.join(item))

        # Find the longest common prefix to use as the key for this group
        key = find_longest_common_prefix(list(matching_items))
    
        # Check if the key already exists in the final dictionary, if so merge the groups
        existing_keys = list(final_urls.keys())
        for existing_key in existing_keys:
            existing_key_elements = set(existing_key.split('-'))
            if set(most_common_list_as_list).issubset(existing_key_elements) or existing_key_elements.issubset(set(most_common_list_as_list)):
                final_urls[existing_key].extend(list(matching_items))
                break
        else:
            final_urls[key] = list(matching_items)
    
        # Remove matched items from both list_1 and list_2
        list_1 = [item for item in list_1 if '-'.join(item) not in matching_items]
        list_2 = [item for item in list_2 if '-'.join(item) not in matching_items]

        # Move to the next item in list_1
        x += 1
      
    final_urls = {k: v for k, v in final_urls.items() if k != ''}  # Clean up any empty keys
    
    return final_urls

def get_group_with_most_matches(shades_dict, fenty_list):
    """
    Identify the group with the most matching URLs from a given list of Fenty product URLs.
    """
    best_prefix = None
    best_groups = []
    highest_match_count = 0
    
    # Iterate through the dictionary to find the best matching group
    for prefix, groups in shades_dict.items():
        current_match_count = 0
        current_groups = []
        
        for group, value in groups.items():
            match_count = 0
            
            # Check how many URLs from the Fenty list match URLs in this group
            for url in value['urls']:
                for fenty_item in fenty_list:
                    if url in fenty_item:
                        match_count += 1
            
            if match_count > 0:
                current_match_count += match_count
                current_groups.append(group)
        
        # Update if this group has more matches than any previous group
        if current_match_count > highest_match_count:
            highest_match_count = current_match_count
            best_prefix = prefix
            best_groups = current_groups
    
    # Collect all matching URLs
    all_urls = []
    if best_prefix and best_groups:
        for group in best_groups:
            all_urls.extend(shades_dict[best_prefix][group]['urls'])
    
    all_urls = list(set(all_urls))  # Ensure URLs are unique
    return all_urls if all_urls else []

def get_exact_number_matches(shades_dict, fenty_list):
    """
    Identify URLs with exact number matches between the shade dictionary and the Fenty product list.
    """
    matching_groups = {}

    # Iterate through the dictionary to check for exact number matches
    for prefix, groups in shades_dict.items():
        for group, value in groups.items():
            for url in value['urls']:
                # Extract numbers from the Fenty items
                for fenty_item in fenty_list:
                    fenty_numbers = re.findall(r'\d+', fenty_item)
                    
                    # Extract numbers from the URL
                    url_numbers = re.findall(r'\d+', url)
                    
                    # Check for exact matches between numbers in the URL and Fenty item
                    if any(url_num in fenty_numbers for url_num in url_numbers):
                        if prefix not in matching_groups:
                            matching_groups[prefix] = []
                        if group not in matching_groups[prefix]:
                            matching_groups[prefix].append(group)
                        break  # Stop after the first match within this URL
    
    # Collect all matching URLs
    all_matching_urls = []

    for prefix, groups in matching_groups.items():
        for group in groups:
            all_matching_urls.extend(shades_dict[prefix][group]['urls'])
            
    all_urls = list(set(all_matching_urls))  # Ensure URLs are unique
    
    return all_urls
