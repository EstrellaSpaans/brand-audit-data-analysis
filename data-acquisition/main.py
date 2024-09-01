import data-acquisition.acquire_html
import data-acquisition.extract_urls
from utils.load-save-data import load_data, save_data
from data-acquisition/fenty-product-urls import intersection, is_contiguous_sublist, find_longest_common_prefix
from data-acquisition/fenty-product-urls import extract_shades, identify_product_variation, get_group_with_most_matches, get_exact_number_matches, generate_product_urls

def main():
    brands = load_data('data/general_brand_data.xlsx', file_type='xlsx')

    brands['page_urls'] = brands.apply(lambda row: extract_urls(acquire_html(row['website']), row['website']), axis=1)
    brands['product_urls'] = brands.apply( lambda x: [url for page in x['prdcts_page'] for url in find_urls(acquire_html(x['website'] + page), x['website'])],axis=1)
  
    html_content = acquire_html(website_url)
    fenty_shades = extract_shades(html_content)

    with open('data/fenty_website.html', 'r', encoding='utf-8') as file:
       fenty_shades = extract_shades(file.read())
    
    fenty = list(brands[brands['brand'] == 'Fenty Beauty']['product_urls'][0])
    fenty_products = identify_product_variation(fenty)

    product_urls = generate_product_urls(fenty_products, fenty_shades)
    brands['product_urls'] = brands.apply(lambda row: product_urls if row['brand'] == 'Fenty Beauty' else row['product_urls'], axis=1)
    
    save_data(brands, filename='data/brand_website_urls', file_type='xlsx'):

if __name__ == "__main__":
    main()
