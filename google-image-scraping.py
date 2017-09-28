from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import json
import urllib
import sys
import time

# adding path to geckodriver to the OS environment variable
os.environ["PATH"] += os.pathsep + os.getcwd()

# Configuration
download_path = "dataset/"
# Images
words_to_search = ['Rafale','Mirage 2000-5', 'Mirage 2000B', 'DR400', 'A320', 'Boeing 737-800']
nb_to_download = [3,0,0,0,0,0]
first_image_position = [5,0,0,0,0,0]

def main():
    if len(words_to_search) != len(nb_to_download) or len(nb_to_download) != len(first_image_position) :
        raise ValueError('You may have forgotten to configure one of the lists (length is different)')
    i= 0
    # For each word in the list, we download the number of images requested
    while i<len(words_to_search):
        print("Words "+str(i)+" : "+str(nb_to_download[i])+"x\""+words_to_search[i]+"\"")
        if nb_to_download[i] > 0:
            search_and_save(words_to_search[i],nb_to_download[i], first_image_position[i])
        i+=1


def search_and_save(text, number, first_position):
    # Number_of_scrolls * 400 images will be opened in the browser
    number_of_scrolls = int((number + first_position)/ 400 + 1) 
    print("Search : "+text+" ; number : "+str(number)+"; first_position : "+str(first_position)+" ; scrolls : "+str(number_of_scrolls))

    # Create directories to save images
    if not os.path.exists(download_path + text.replace(" ", "_")):
        os.makedirs(download_path + text.replace(" ", "_"))

    # Connect to Google Image
    url = "https://www.google.co.in/search?q="+text+"&source=lnms&tbm=isch"
    driver = webdriver.Firefox()
    driver.get(url)
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    extensions = {"jpg", "jpeg", "png", "gif"}
    
    img_count = 0
    downloaded_img_count = 0
    img_skip = 0
    
    # Prepare Google Page
    for _ in range(number_of_scrolls):
        for __ in range(10):
            # Multiple scrolls needed to show all 400 images
            driver.execute_script("window.scrollBy(0, 1000000)")
            time.sleep(0.2)
        # to load next 400 images
        time.sleep(2.5)
        try:
            driver.find_element_by_xpath("//input[@value='Show more results']").click()
            time.sleep(2.5)
        except Exception as e:
            print("Less images found:"+ str(e))
            break

    # Process (download) images
    imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    print("Total images:"+ str(len(imges)) + "\n")
    for img in imges:
        if img_skip < first_position:
            # Skip first images if asked to
            img_skip += 1
        else :
            # Get image
            img_count += 1
            img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
            img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
            print("Downloading image "+ str(img_count) + ": "+ img_url)
            try:
                if img_type not in extensions:
                    img_type = "jpg"
                # Download image and save it
                req = urllib.request.Request(img_url, headers=headers)
                raw_img = urllib.request.urlopen(req).read()
                f = open(download_path+text.replace(" ", "_")+"/"+str(img_skip+downloaded_img_count)+"."+img_type, "wb")
                f.write(raw_img)
                f.close
                downloaded_img_count += 1
            except Exception as e:
                print("Download failed:"+ str(e))
            finally:
                print("")
            if downloaded_img_count >= number:
                break

    print("Total skipped : "+str(img_skip)+"; Total downloaded : "+ str(downloaded_img_count)+ "/"+ str(img_count))
    driver.quit()

if __name__ == "__main__":
    main()