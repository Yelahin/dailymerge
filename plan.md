# News aggregator

***

## What is news aggregator?

**News aggregator website** - is a website which organize lots of different articles from different sources(websites) in single page. 

>**Wikipedia** - Aggregation technology often consolidates web content into one page that can show only the new or updated information from many sites. aggregators reduce the time and effort needed to regularly check websites for updates, creating a unique information space or personal newspaper. 

***

## Creating plan

- Select name for project ✅

- Create repository for project

- Connect to GitHub

- Start project

- Separate project logic in different apps

- Set up basic backend for website

- Set up database

- Select niche for aggregator

- Using [*feedparser*](https://feedparser.readthedocs.io/en/latest/) set up data collection through RSS

- Using [*requests*](https://requests.readthedocs.io/en/latest/) set up data through external APIs

- Normalization data in needed format, article

- Store articles in database


- Set up nice filters and search

- Caching using ***Redis***

- Make nice UI

***

## How to parse data?

#### Use [*feedparser*](https://requests.readthedocs.io/en/latest/)

> **Use [*feedparser*](https://requests.readthedocs.io/en/latest/) to parse RSS/Atom feeds. (More sources, less customization)**
>>[*feedparser*](https://feedparser.readthedocs.io/en/latest/) -  a Python module that parses feeds in all known formats, including RSS, RDF, and Atom.
<br>
>> **Official documentation** - [*feedparser*](https://feedparser.readthedocs.io/en/latest/) is a Python module for downloading and parsing syndicated feeds. It can handle RSS 0.90, Netscape RSS 0.91, Userland RSS 0.91, RSS 0.92, RSS 0.93, RSS 0.94, RSS 1.0, RSS 2.0, Atom 0.3, Atom 1.0, CDF and JSON feeds. It also parses several popular extension modules, including Dublin Core and Apple’s iTunes extensions.

#### Use [*requests*](https://requests.readthedocs.io/en/latest/) package 

> **Use [*requests*](https://requests.readthedocs.io/en/latest/) to fetch data using external APIs. (Less sources, more customization)**
>> [*requests*](https://requests.readthedocs.io/en/latest/) - is a library allows you to send HTTP requests, such as GET and POST , and handle responses from web servers. requests is a user-friendly and powerful module for interacting with web resources. This is where Python 3 makes working with web protocols especially accessible for beginners.
<br>
>> **Official documentation** - [*requests*](https://requests.readthedocs.io/en/latest/) is an elegant and simple HTTP library for Python, built for human beings. 