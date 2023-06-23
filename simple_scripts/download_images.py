# Google Images Download
# This is a command-line python program to search keywords / key-phrases on Google Images
# and optionally download images to your computer.
#
# For more than 100 images per keyword install 'Selenium' library along with 'chromedriver'.
# ChromeDriver - WebDriver for Chrome: https://sites.google.com/a/chromium.org/chromedriver/downloads
#
# Requirements:
#   pip install google_images_download
import os

from google_images_download import google_images_download   # importing the library

# Prepare list of arguments
output_dir = '../temp/downloads'
os.makedirs(output_dir, exist_ok=True)  # create directory
keywords = ['balloon tree',
            'computer cake',]
arguments = {
    'keywords': ', '.join(keywords),  # use ',' between words for several requests
    'limit': 120,  # download 120 images for EACH keyword, separated by ','
    'print_urls': True,  # print URLs
    'output_directory': output_dir,  # download dir will be created automatically
    'chromedriver': '../temp/chromedriver.exe',  # path to chromedriver.exe file
}

response = google_images_download.googleimagesdownload()   # class instantiation
output = response.download(arguments)   # download with the arguments

print(f'Output:\n{output}')   # print absolute paths of the downloaded images
