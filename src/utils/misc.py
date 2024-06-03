import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_website_info(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Extract the website name
    website_name = domain.split('.')[-2]  # e.g., "youtube"

    # Get the favicon URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Look for the favicon in the <link> tags
    icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
    if icon_link:
        favicon_url = icon_link.get('href')
        parsed_favicon_url = urlparse(favicon_url)
        if not parsed_favicon_url.netloc:  # relative URL
            favicon_url = urljoin(url, favicon_url)
    else:
        # Default favicon location
        favicon_url = urljoin(url, '/favicon.ico')

    return website_name, favicon_url