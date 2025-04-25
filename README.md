# Web motor scraping
> Access engines manufacturer sites and get information about their products

This program access and scraping web site from manufacturer that made engines and get:
    - Product id and name
    - Specifications
    - Bom data
    - Cad files

## Install requirements

Run:

```
pip install requirements.txt
```

## Scrappers

In this folder you add the code to scraper web page, don't forget their config file. Follows the [ABB](https://www.baldor.com/) example.

## Config

At config you can configure some actions:
* scraping_limit: By default the code access the site and get all products ids avaible, with limit different of None, instead of run for all products, the code get a random sample from all products list.
* unique: If you run for specific ids, set here 
* only_new: If you want to skip already downloaded ids
* log_verbose: To print log information in the terminal
* log_folder: Set the log folder for log and hydra output

## Usage example

To run with default config, in this case the code will be run for the all 12733 products ids, and without print logs information.

```
    src/main.py
```

Run for a random sample with 15 products ids.

```
    python src/main.py scraping_limit=15
```

To skip products ids already downloaded.

```
    python src/main.py only_new=True
```

To get data only to 105W motor id

```
    python src/main.py unique=["105W"]
```

Run for a random sample with 15 products ids and skip products ids already downloaded.

```
    python src/main.py scraping_limit=15 only_new=True
```

## Release History

* 1.0.0
    * scraping ABB companys site
