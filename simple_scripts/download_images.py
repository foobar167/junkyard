# Google Images Download
# This is a command-line python program to search keywords / key-phrases on Google Images
# and optionally download images to your computer.
#
# If you would want more than 100 images per keyword, then you would need to install
# 'Selenium' library along with 'chromedriver'.
#
# Requirements:
#   pip install google_images_download
from google_images_download import google_images_download   # importing the library

# Prepare list of arguments
download_dir = '../temp/downloads'  # download directory will be created automatically
arguments = {'keywords': 'balloon, tree, computer',
             'limit': 20,
             'print_urls': True,
             'output_directory': f'{download_dir}'}

response = google_images_download.googleimagesdownload()   # class instantiation
output = response.download(arguments)   # download with the arguments

print(f'Output:\n{output}')   # print absolute paths of the downloaded images
