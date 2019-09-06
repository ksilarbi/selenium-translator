# selenium-translator
A little python 3 script that uses selenium to translate text by feeding it to the deepl website.

## Set up
```bash
.
├── README.md
├── requirements.txt
├── selenium_translate.py
├── texts_folder/
└── webdrivers/
```

* You first need to install a chrome webdriver in the './webdrivers' folder. You can download [here](https://www.seleniumhq.org/download/) the chrome webdriver.
* For more information you can check this [link](https://chromedriver.chromium.org/getting-started)

## Install
```bash
pip install -r requirements.txt
```

## Usage
Add the text files you want to translate in './texts_folder'

exemple: translate to english all the text files in './texts_folder':
```bash
python selenium_translate.py --target english 
```

for more info on the params:
```bash
python selenium_translate.py --help
```

