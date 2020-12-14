import numpy as np
from bs4 import BeautifulSoup
import re
import requests
from time import sleep
import random
import pandas as pd
import os

years_election = [1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018]
base_url = 'https://en.wikipedia.org/wiki/date_United_States_House_of_Representatives_elections#state'
to_avoid = [('Alaska', 2010), ('Delaware', 2010), ('Idaho', 1986), ('Mississippi', 2010), ('Wyoming', 2002),
            ('Wyoming', 2010)]


def get_url_state(file):
    # checked
    state = file.split('.')[0]
    name_state = state.split(' ')
    if len(name_state) > 1:
        state = name_state[0] + '_' + name_state[1]
    state_url = base_url.replace('state', state)
    return state_url, state


def get_url_date(year, state_url):
    # checked
    year_url = state_url.replace('date', str(year))
    return year_url


def get_urls():
    # checked
    dict_state_urls = {}
    for file in os.listdir('states/'):
        state_url, state = get_url_state(file)
        states_url = []
        for year_election in years_election:
            if (state, year_election) in to_avoid:
                continue
            good_url = get_url_date(year_election, state_url)
            states_url.append(good_url)
        dict_state_urls[state] = states_url
    return dict_state_urls


def scrapping():
    urls = get_urls()
    for state in urls.keys():
        state_urls = urls.get(state)
        for i, state_url in enumerate(state_urls):
            cur_page = requests.get(state_url).content
            with open('states/' + str(state) + '_' + str(years_election[i]) + '.txt', 'wb') as file:
                file.write(cur_page)
            sleep(random.randint(1, 3))


def extract_info(file):
    file_contents = open(file, 'rb').read()
    soup = BeautifulSoup(file_contents, 'html.parser')
    table = soup.find_all(attrs={'class': 'wikitable'})[2:52]  # the first two wiki tables are not for states results
    scores = []
    rep = 0
    dem = 0
    for table_state in table:
        for s in table_state.text.split(' '):
            if 'Republican' in s and ('1' in s or '2' in s) and '(' not in s:
                rep += 1
            if 'Democratic' in s and ('1' in s or '2' in s) and '(' not in s:
                dem += 1
        try:
            pre_rep = (rep / (rep + dem))
            scores.append(pre_rep)
        except ZeroDivisionError:
            scores.append(np.nan)
    return scores


def extract_scores():
    scores = {}
    for year in years_election:
        file = 'states/' + str(year) + '.txt'
        scores_year = extract_info(file)
        scores[year] = scores_year
    return scores


def write_dfs():
    scores = extract_scores()
    stacked_scores = []
    for year in years_election:
        stacked_scores.append(scores.get(year))
    stacked_scores = np.array(stacked_scores)
    states = [file.split('.')[0] for file in os.listdir('states/') if file.endswith('csv')]
    for i, state in enumerate(states):
        scores_state = stacked_scores[:, i]
        df_state = pd.DataFrame({'Rep_House_Prop': scores_state,
                                 'Year': years_election,
                                 'State': [state] * 9})
        df_state.to_csv('states/' + str(state) + '_House.csv')


if __name__ == '__main__':
    print(extract_scores())
