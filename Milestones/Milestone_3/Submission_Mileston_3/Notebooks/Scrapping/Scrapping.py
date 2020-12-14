import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import os

years_election = [1968, 1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020]
months_considered = [6, 7, 8, 9, 10, 11]


def reformat_gdp():
    df = pd.read_csv('data/GDP/GDP.csv')
    gdp = df['GDPC1'].values
    # separate them into list of 7 values: one per year of non-election and 4 per election year
    gdps = [gdp[i:i + 7] for i in range(0, len(gdp), 7)]
    attributes = ['Year0', 'Year1', 'Year2', 'Electiony1', 'Electiony2', 'Electiony3', 'Electiony4']
    new_df = pd.DataFrame(gdps, columns=attributes)
    return new_df


def reformat_rdi():
    df = pd.read_csv('data/Fundamentals/RDI/RDI.csv')
    rdi = df[df.columns[1]].values
    rdis = [rdi[i:i + 4] for i in range(0, len(rdi), 4)]
    attributes = ['rdi_y0', 'rdi_y1', 'rdi_y2', 'rdi_ey']
    new_df = pd.DataFrame(rdis, columns=attributes)
    return new_df


def reformat_payroll():
    df = pd.read_csv('data/Fundamentals/Payroll/PAYEMS.csv')
    payroll = df['PAYEMS'].values
    payroll_reformated = []
    payroll_per_year = [payroll[i:i + 12] for i in range(0, len(payroll), 12)]
    #  print(payroll_per_year)
    year = 1
    for payroll_year in payroll_per_year:
        if year % 4 == 0:
            payroll_year_reformated = payroll_year[7:10]
        else:
            payroll_year_reformated = [payroll_year[9]]
        payroll_reformated.append(payroll_year_reformated)
        year += 1
    #  now aggregate the data for every election
    payroll_final = [np.hstack(payroll_reformated[i:i + 4]) for i in range(0, len(payroll_reformated), 4)]
    attributes_payroll = ['payroll_y1', 'payroll_y2', 'payroll_y3', 'payroll_ey1', 'payroll_ey2', 'payroll_ey3']
    payroll_df = pd.DataFrame(payroll_final, columns=attributes_payroll)
    return payroll_df


def reformat_dowjones():
    dowjones_yearly = np.hstack(pd.read_csv('data/Fundamentals/Stock_market/Dowjones.csv').values)
    dowjones_yearly = [float(s[:-1]) / 100. for s in dowjones_yearly[::-1]]
    dowjones_per_election = [dowjones_yearly[i:i + 4] for i in range(0, len(dowjones_yearly), 4)]
    dowjones_per_election[-1].append(-0.0371)
    stock_market = pd.DataFrame(dowjones_per_election, columns=['Stock_y1', 'Stock_y2', 'Stock_y3', 'Stock_ey'])
    return stock_market


def dataframe_fundamentals():
    data_directory = 'data/Fundamentals/'
    dfs = []
    columns_name = []
    values = None
    for i, f in enumerate(os.listdir(data_directory)):
        try:
            for j, file in enumerate(os.listdir(os.path.join(data_directory, f))):
                wdirectory = os.path.join(data_directory, f)
                if file.endswith('.csv'):
                    csv_file = os.path.join(wdirectory, file)
                    df = pd.read_csv(csv_file)
                    columns_name.extend(list(df.columns))
                    if values is None:
                        values = df.values
                    else:
                        values = np.concatenate((values, df.values), axis=1)
        except:
            continue
    df_fundamental = pd.DataFrame(values, columns=columns_name)
    df_fundamental.drop(df_fundamental.columns[0], axis=1, inplace=True)
    return df_fundamental


def load_polls():
    df = pd.read_csv('data/poll_average_1968_2020.csv')
    return df


def load_national_polls():  # produces the csv file polls_aggregated
    df = load_polls()
    df_state = df[df['state'] == 'National']
    df_state = df_state.dropna(inplace=False)
    polls = df_state.drop('pct_estimate', axis=1, inplace=False)  # drop the pct_estimate and keep the pct_adjusted
    polls_per_year = pd.DataFrame()
    for year_election in years_election:
        election_polls = polls[polls['cycle'] == year_election]  # select only the polls of the election year
        mask_interesting_months = election_polls['modeldate'].apply(
            lambda x: True if (
                        int(x.split('/')[0]) > 5) else False)  # select the polls of election year, from June to October
        interesting_months_poll = election_polls[mask_interesting_months]
        candidates = np.unique(
            interesting_months_poll['candidate_name'].values)  # candidates for the presidential election
        for candidate in candidates:
            candidate_polls = interesting_months_poll[interesting_months_poll['candidate_name'] == candidate]
            for month in months_considered:
                mask_month_considered_candidate = candidate_polls['modeldate'].apply(
                    lambda x: True if (int(x.split('/')[0])) == month else False)  # get the poll for every month
                month_considered_candidate = candidate_polls[mask_month_considered_candidate]
                stats_polls_candidate = np.mean(month_considered_candidate[
                                                    'pct_trend_adjusted'])  # compute the mean poll for every month considered
                polls_per_year = polls_per_year.append({'cycle': int(year_election),
                                                        'state': 'National',
                                                        'modeldate': int(month),
                                                        'candidate_name': candidate,
                                                        'pct_median_adjusted': stats_polls_candidate},
                                                       ignore_index=True)
    # drop the rows 'Convention Bounce for ...' which are only apparent in the 2020 election
    mask_polls_per_year = polls_per_year['candidate_name'].apply(
        lambda x: False if x.startswith('Convention') else True)
    polls_per_year = polls_per_year[mask_polls_per_year]
    return polls_per_year


def select_candidates(polls_1):  # this function only retains the two best candidates for every election year, being R vs D
    # drop the candidates which are not Democrats or Republicans: these are consistently the candidates that had the higher polls
    polls_2 = pd.DataFrame()
    for year in years_election:
        polls_year = polls_1[polls_1['cycle'] == year]
        candidates = np.unique(polls_year['candidate_name'])
        # now, create a dictionary {candidate: mean(score)} for every candidate, sort it according to the score and select the best 2
        scores_candidates = {
            candidate: np.mean(polls_year[polls_year['candidate_name'] == candidate]['pct_median_adjusted']) for
            candidate in candidates}
        sorted_scores = {name: score for (name, score) in sorted(scores_candidates.items(), key=lambda x: x[1])}
        retained_candidates = list(sorted_scores.keys())[-2:]  # the sort is being made in increasing order
        mask_retained_candidates = polls_year['candidate_name'].apply(
            lambda x: True if x in retained_candidates else False)
        retained_candidates_df = polls_year[mask_retained_candidates]
        polls_2 = polls_2.append(retained_candidates_df, ignore_index=True)
    return polls_2


def reformat_dataframe(polls):
    """This function reformats our dataframe as wanted: one row per candidate to the presidential Election. It
    also gets rid of the unwanted columns and guarantees that the types are the one we want"""
    polls.drop('state', axis=1, inplace=True)
    polls_restructured = pd.DataFrame()
    for year in years_election:
        polls_year = polls[polls['cycle'] == year]
        for candidate in np.unique(polls_year['candidate_name']):
            polls_year_candidate = polls_year[polls_year['candidate_name'] == candidate]
            scores = polls_year_candidate['pct_median_adjusted']
            dictionnary_candidate = {'Month_' + str(i + 6): score for i, score in enumerate(scores)}
            dictionnary_candidate['Name'] = candidate
            dictionnary_candidate['Year'] = year
            polls_restructured = polls_restructured.append(dictionnary_candidate, ignore_index=True)
    polls_restructured['Year'] = polls_restructured['Year'].astype(np.int64, copy=True)
    return polls_restructured



if __name__ == '__main__':
    polls = pd.read_csv('data/Polls/Polls_final.csv')
    print(polls)



