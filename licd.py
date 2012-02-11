#!/usr/bin/env python
#
# Least I Could Do Strip Scraper
# By Brandon Smith (brandon.smith@studiobebop.net)
#
import os
import sys
import time
import urlparse
import requests
import BeautifulSoup
import progressBar
import threading

###
# Config stuff
###

thread_limit = 16
current_count = 0
showing_bar = False
output_root = ""

#!# End Config #!#

def get_archived_strip_urls():
    sys.stdout.write("[+] Grabbing all strip URLs from archive pages, ")
    sys.stdout.flush()
    
    # get archive year page links
    archive_url = "http://leasticoulddo.com/archive/calendar/"
    page = requests.get(archive_url).content
    soup = BeautifulSoup.BeautifulSoup(page)
    year_links = []
    for tag in soup.findAll("a"):
        if not tag.has_key("href") or not tag["href"].startswith("/archive/calendar/2"):
            continue
        link = urlparse.urljoin(archive_url, tag["href"])
        year_links.append(link)

    # parse each archive year page for strip page links
    strip_page_links = []
    for archive_page_url in year_links:
        page = requests.get(archive_page_url).content
        soup = BeautifulSoup.BeautifulSoup(page)
        for tag in soup.findAll("a"):
            if not tag.has_key("href") or not tag["href"].startswith("/comic/"):
                continue
            link = urlparse.urljoin(archive_url, tag["href"])
            if link not in strip_page_links:
                strip_page_links.append(link)

    print "Done"
    return strip_page_links

def start_bar(total):
    global current_count
    showing_bar = True
    bar = progressBar.progressBar(total)
    while current_count < total:
        sys.stdout.write("\r[+] %s %d/%d" % (bar.get_bar(current_count), current_count+1, total))
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r[+] %s %d/%d" % (bar.get_bar(total), total, total))
    sys.stdout.flush()
    showing_bar = False

def download_strip(strip_page_url):
    global current_count, output_root
    try:
        page = requests.get(strip_page_url).content
        soup = BeautifulSoup.BeautifulSoup(page)
    
        # prep file name and path
        title = soup.find("title").string.split("&raquo;")[-1]
        title = title.strip()
        index = strip_urls.index(strip_page_url) + 1
        index = str(index).zfill(len(str(len(strip_urls))))
        title = "%s - %s" % (index, title)
    
        # get strip image url
        image_url = soup.find("td", attrs={"id": "comic"}).find("img")
        if not image_url or not image_url.has_key("src"):
            current_count += 1
            return
        image_url = image_url["src"]
        if not image_url.startswith("http"):
            image_url = urlparse.urljoin(strip_page_url, image_url)
    
        # get image format extension and complete file name and path
        file_extension = image_url.split(".")[-1]
        file_name = "%s.%s" % (title, file_extension)
        file_path = os.path.join(output_root, file_name)
        if os.path.exists(file_path):
            current_count += 1
            return
    
        # save the strip already!
        image_data = requests.get(image_url).content
        out = open(file_path, "wb")
        out.write(image_data)
        out.close()
    except:
        pass
    current_count += 1


if __name__ == '__main__':
    # get strip page URLs
    strip_urls = get_archived_strip_urls()
    strip_urls.sort()
    strip_urls = strip_urls[:200]

    # prep output directory
    print "[+] Prepping output directory (./out)"
    output_root = os.path.join(os.path.abspath("."), "out")
    if not os.path.exists(output_root):
        os.mkdir(output_root)

    # Start downloading strips
    print "[+] Starting download of all %d strips." % len(strip_urls)
    threading.Thread(target=start_bar, args=(len(strip_urls),)).start()
    for strip_page_url in strip_urls:
        while threading.activeCount() >= thread_limit:
            time.sleep(0.3)
        threading.Thread(target=download_strip, args=(strip_page_url,)).start()
    while threading.activeCount() > 1:
        time.sleep(0.25)

    print
    print "[+] All done, all strip images have been saved."
    raw_input("[+] Press enter to exit...")