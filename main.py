import csv
import sys
import requests
from playwright.sync_api import sync_playwright
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup


def extract_substack_article(url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        # Wait for the article content to load, you may need to adjust the timing here
        page.wait_for_selector('article.post')
        # Extract the article content
        article_content = page.inner_html('article.post')
        browser.close()
        return article_content


def scrape_substack_url(url):
    soup = BeautifulSoup(extract_substack_article(url), 'html.parser')

    header = soup.find('div', {'class': 'post-header'})
    title = header.find('h1', {'class': 'post-title'}).text
    subtitle = header.find('h3', {'class': 'subtitle'}).text

    body = soup.find('div', {'class': 'body'})

    output = ""

    for item in body.find_all(['p', 'h2']):
        if item.name == "p":
            output += item.text + "\n"
            continue

        if item.name == "h2":
            output += "\n" + item.text + "\n"
            continue

    return title, subtitle, output


def filter_urls(urls, keywords):
    return [url for url in urls if all(keyword not in url for keyword in keywords)]

def get_articles(profile_url):
    sitemap_url = f"{profile_url}sitemap.xml"
    response = requests.get(sitemap_url)

    if response.ok:
        root = ET.fromstring(response.content)
        urls = [element.text for element in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        urls = filter_urls(urls, ["about", "archive", "podcast"])
        return urls
    else:
        print(f'Error fetching sitemap: {response.status_code}')
        return []


def write_to_csv(title, subtitle, content):
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([title, subtitle, content])


def main():
    profile_url = input("Enter the profile you'd want to scrape: ")
    urls = get_articles(profile_url)
    for url in urls:
        title, subtitle, content = scrape_substack_url(url)
        write_to_csv(title, subtitle, content)



if __name__ == '__main__':
    main()
