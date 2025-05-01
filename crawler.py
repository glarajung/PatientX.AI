# https://forum.alzheimers.org.uk/
from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd

# load the home page
URL = "https://forum.alzheimers.org.uk/"
page = requests.get(URL)
soup = BeautifulSoup(page.text, 'html.parser')

# define the base url for constructing the sub pages
base_url = "https://forum.alzheimers.org.uk"

# get forum categories
def get_category_blocks(soup_html):
    blocks = soup.find_all("div", {"class": "block--category"})
    return blocks

# get category name from html
def get_category_name_from_block(block):
    category_name = block.find(class_='uix_categoryTitle').text
    return category_name

# get list of forums listed in a html block
def get_forums_from_block(block, category_name):
    forums_list = []
    forums = block.find_all(class_='node-title')
    for forum in forums:
        forum_name = forum.a.string
        forum_url = base_url + forum.a['href']
        forum_entry = [category_name, forum_name, forum_url]
        forums_list.append(forum_entry)
    # get forum name, url
    return forums_list

# get all forums info from web page
def get_all_forums(soup):
    blocks = get_category_blocks(soup)
    all_forums = []
    for block in blocks:
        category_name = get_category_name_from_block(block)
        forum_list = get_forums_from_block(block, category_name)
        all_forums = all_forums + forum_list 
    return all_forums

# get posts from thread
def load_thread_from_soup(thread_page_soup):
    posts_info = []
    posts = thread_page_soup.find_all(class_=['message', 'message--post'])
    for post in posts:
        post_author = post.find(class_='username').text
        post_author_title = post.find(class_='message-userTitle').text
        post_id = int(post['data-content'].replace('post-', ''))
        timestamp = post.find("time")['datetime']
        post_nr = post.find(class_='message-attribution-opposite').find_all("li")[-1].text
        post_nr = str(post_nr).replace('\n', "").replace('\t', "").replace('#', "").replace(',','')
        post_nr = int(post_nr)
        quotes = []
        for div in post.find_all("blockquote", {'class':'bbCodeBlock--quote'}):
            quotes.append(div['data-source'].replace('post: ', ''))
            
        for div in post.find_all("blockquote", {'class':'bbCodeBlock--quote'}):
            div.decompose()
        post_message =  post.find(class_='message-body').text
        post_info = [post_author, post_author_title, post_id, timestamp, post_nr, post_message, quotes]
        posts_info.append(post_info)
    return posts_info

# load the threads from a webpage
def load_thread_posts(thread_page_url):
    page = requests.get(thread_page_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    posts_info = load_thread_from_soup(soup)
    return posts_info

# get all the posts from a thread
def load_thread(thread_url):
    page = requests.get(thread_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # get number of pages
    page_numbers_nav = soup.find_all(class_='pageNav-page')
    page_numbers = 1
    if len(page_numbers_nav) == 0:
        page_numbers = 1
    else:
        page_numbers = page_numbers_nav[-1].a.string

    post_list = load_thread_from_soup(soup)

    if int(page_numbers) == 1:
        return post_list
    elif int(page_numbers) == 2:
        return post_list + load_thread_posts(thread_url + 'page-2')
    # enumerate over the pages
    for i in range(2, int(page_numbers)+1):
        post_list = post_list + load_thread_posts(thread_url + 'page-' + str(i))
    # per page get the thread name and url
    result = post_list
    return result

# get thread info from a forum
def get_thread_info_from_soup(forum_page_soup):
    threads_list = []
    threads = forum_page_soup.find_all(class_='structItem-title')
    for thread in threads:
        thread_name = thread.a.string
        thread_url = thread.a['href']
        threads_list.append([thread_name, base_url + thread_url])
    return threads_list

# retreive thread info from a forum page
def get_threads_info(forum_page_url):
    page = requests.get(forum_page_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    threads_list = get_thread_info_from_soup(soup)
    return threads_list

# get all threads from a forum
def load_forum(forum_category, forum_name, forum_url):
    page = requests.get(forum_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # get number of pages
    page_numbers_nav = soup.find_all(class_='pageNav-page')
    page_numbers = 1
    if len(page_numbers_nav) == 0:
        page_numbers = 1
    else:
        page_numbers = page_numbers_nav[-1].a.string

    threads_list = get_thread_info_from_soup(soup)

    if int(page_numbers) == 1:
        result = []
        for thread in threads_list:
            thread_with_info = [forum_category, forum_name] + thread
            result.append(thread_with_info)
        return result
    elif int(page_numbers) == 2:
        threads_list = threads_list + get_threads_info(forum_url + 'page-2')
        for thread in threads_list:
            thread_with_info = [forum_category, forum_name] + thread
            result.append(thread_with_info)
        return result
    # enumerate over the pages
    for i in range(2, int(page_numbers)+1):
        threads_list = threads_list + get_threads_info(forum_url + 'page-' + str(i))
    # per page get the thread name and url
    result = []
    for thread in threads_list:
        thread_with_info = [forum_category, forum_name] + thread
        result.append(thread_with_info)
    return result

# get all the forums, threads, and posts. and store in csv
def get_entire_forum_tocsv(soup):
    forums = get_all_forums(soup)
    all_posts = []
    for forum in forums:
        print(forum[2])
        threads = load_forum(forum[0], forum[1], forum[2])
        forum_name = str(forum[1]) + '.csv'
        spamWriter = csv.writer(open(forum_name, 'a', newline=''))
        spamWriter.writerow(['category', 'forum', 'thread_title', 'thread_url','username', 'post_author_title', 'post_id','timestamp', 'message_nr' , 'post_message', 'quotes'])
        for thread in threads:
            print(thread[3])
            posts = load_thread(thread[3])
            for post in posts:
                # category, forum, thread, thread_url, username, timestamp, post_nr, post_message
                results_post = [thread[0], thread[1], thread[2], thread[3]] + post
                spamWriter = csv.writer(open(forum_name, 'a', newline=''))
                spamWriter.writerow(results_post)

# get and store for a specified forum it's threads and posts
def get_subforum_tocsv(category, forum, forum_url):
    spamWriter = csv.writer(open(forum + '.csv', 'a', newline=''))
    spamWriter.writerow(['category', 'forum', 'thread_title', 'thread_url','username', 'post_author_title', 'post_id','timestamp', 'message_nr' , 'post_message', 'quotes'])
    threads = load_forum(category, forum, forum_url)
    for thread in threads:
        # print(thread[3])
        posts = load_thread(thread[3])
        for post in posts:
            # category, forum, thread, thread_url, username, timestamp, post_nr, post_message
            results_post = [thread[0], thread[1], thread[2], thread[3]] + post
            spamWriter = csv.writer(open(forum + '.csv', 'a', newline=''))
            spamWriter.writerow(results_post)

# load the website and store the results in a csv
get_entire_forum_tocsv(soup)
