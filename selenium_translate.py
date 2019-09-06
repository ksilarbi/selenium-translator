from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium.webdriver.chrome.options import Options
import os
import re
import sys
import glob
from loguru import logger
from nltk import tokenize
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--target", type=str, choices=["french", "english", "german", "spanish", "portuguese", "italian", "dutch", "polish", "russian"],
                help="""Choose target language for translation {"french", "english", "german", "spanish", "portuguese", "italian", "dutch", "polish", "russian"}""")
args = parser.parse_args()

logger.add(sys.stderr, format="{time} {message}", filter="selenium_translate", level="INFO")

TEXTS_FOLDER_PATH = './texts_folder/'
TRANSLATED_TEXTS_PATH = './texts_folder/translated_texts/'

if os.path.exists(TEXTS_FOLDER_PATH):
    text_paths = glob.glob(TEXTS_FOLDER_PATH + "*.txt")
    if not os.path.exists(TRANSLATED_TEXTS_PATH):
        logger.info(f"Creating new folder: '{TRANSLATED_TEXTS_PATH}'")
        os.makedirs(TRANSLATED_TEXTS_PATH)
else:
    raise AssertionError("Could not find './texts_folder/', folder in which you should add the texts files you want to translate")

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

WEBDRIVER_PATH = './webdrivers/chromedriver'
DEEPL_URL = 'https://www.deepl.com/fr/translator'

HEADLESS = True
if HEADLESS:
    driver = webdriver.Chrome(WEBDRIVER_PATH, options=options)
    logger.info("Running headless...")
else:
    driver = webdriver.Chrome(WEBDRIVER_PATH)

TARGET_LANGUAGES = ({"french":1,
                    "english":2, 
                    "german":3, 
                    "spanish":4, 
                    "portuguese":5,
                    "italian":6,
                    "dutch":7,
                    "polish":8,
                    "russian":9})

def translate(text_to_translate, target_language=TARGET_LANGUAGES["english"]):

    driver.get(DEEPL_URL)

    input_text_xpath = """//*[@id="dl_translator"]/div[1]/div[2]/div[2]/div/textarea"""
    output_text_xpath = """//*[@id="dl_translator"]/div[1]/div[3]/div[3]/div[1]/textarea"""
    language_select_xpath = """//*[@id="dl_translator"]/div[1]/div[3]/div[1]/div/button/div"""
    target_language_xpath = f"""//*[@id="dl_translator"]/div[1]/div[3]/div[1]/div/div/button[{target_language}]"""

    input_box = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(input_text_xpath))
    output_box = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(output_text_xpath))

    driver.execute_script('arguments[0].value = arguments[1]', input_box, text_to_translate)

    select = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(language_select_xpath))
    select.click()
    sleep(0.5)
    lang = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(target_language_xpath))
    lang.click()
    sleep(random.uniform(8,10))

    translated_text = output_box.get_attribute('value')

    return translated_text


def make_chunks(text, max_chunk_len=4999):
    """Making chunks of text with max chunk length. Since these chukns will be 
       fed to a translator, we need to properly tokenize by sentences to keep context.
    """
    if len(text) <= max_chunk_len:
        return {0:text}

    sentence_list = sentence_tokenize(text)
    
    assert all([max_chunk_len > len(s) for s in sentence_list]), "max_chunk_size value smaller than the length of a sentence !"
    
    current_len = 0
    buffer = ""
    chunks_dict = {}
    i = 0
    for sentence in sentence_list:
        current_len += len(sentence)
        if current_len > max_chunk_len:
            i += 1
            buffer = ""
            current_len = len(sentence)
        buffer += sentence
        chunks_dict[i] = buffer
    
    # tests:
    #assert sum([len(v) for k, v in chunks_dict.items()]) == sum([len(t) for t in sentence_list]), "total sum of chunks is not consistent with text length"
    #assert all([len(v) <= max_chunk_len for k, v in chunks_dict.items()]), "Some chunks are larger than max chunk len"
    
    return chunks_dict

def sentence_tokenize(text):
    sentence_list = tokenize.sent_tokenize(text)
    return sentence_list


def main(target):
    for i, path in enumerate(text_paths):
        with open(path) as f:
            text = f.read()

        chunks = make_chunks(text)
        translated_text = ""
        
        for _, v in chunks.items():
            translated_text += translate(v, TARGET_LANGUAGES[target])
            sleep(random.uniform(2,3))

        logger.info(f"Progress: Translated -> {i+1}/{len(text_paths)}")
        output_fname = os.path.join(TRANSLATED_TEXTS_PATH, 'TRANSLATED_' + os.path.basename(path))
        logger.info(f"Writing to file '{output_fname}'")
        with open(output_fname, 'w') as out:
            out.write(translated_text)

    if not HEADLESS:
        sleep(10)

    driver.close()
    logger.info("Done.")

if __name__ == "__main__":
    if args.target in TARGET_LANGUAGES.keys():
        main(args.target)
    else:
        logger.info("""Could not understand the target language for translation. Target language mut be in this set {"french", "english", "german", "spanish", "portuguese", "italian", "dutch", "polish", "russian"}""")

