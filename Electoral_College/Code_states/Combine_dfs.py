import pandas as pd
import os
import numpy as np


years = [1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020]
years_gdp = [2000, 2004, 2008, 2012, 2016, 2020]
weights = [1, 2, 3, 4]


def create_dirs():
    for i, f in enumerate(os.listdir('states/')):
        if 'txt' not in f:
            state = f[3:-4]
            df = pd.DataFrame({'election': []})
            df.to_csv('states/' + state + '_loyalty.csv')


def get_loyalty():
    for i, f in enumerate(os.listdir('states/')):
        if 'txt' not in f and 'v1' not in f:
            state = f[:-12]
            corresponding = 'v1_' + state + '.csv'
            previous = pd.read_csv('states/' + f)
            df = pd.read_csv('states/' + corresponding)
            republican_scores = df.loc[df['republican'] == 1, 'Result'].values
            republican_scores_before = previous['election'].values
            loyalty = np.concatenate((republican_scores_before, republican_scores))
            weights = np.array([1, 2, 3, 4])
            loyalty_score = [np.sum(weights * loyalty[i - 4:i]) / 10 for i in range(4, len(loyalty)) if
                             np.nan not in loyalty[i - 4:i]]
            df.loc[df['republican'] == 1, 'rep_loyalty'] = loyalty_score
            df.loc[df['republican'] == 0, 'rep_loyalty'] = loyalty_score
            df.to_csv('states/v2' + state + '.csv')


def pop_density():
    pop_density = pd.read_csv('../data/Population_Density/population_density.csv')
    for i, file in enumerate(os.listdir('states')):
        state_density = []
        df_state = pd.read_csv('states/' + str(file))
        density_state = pop_density.iloc[5:, i + 1].values
        for i, density in enumerate(density_state):
            if years[i] in np.unique(df_state['Year']):
                state_density.append(density)
                state_density.append(density)
            else:
                continue
        df_state['density'] = state_density
        # df_state.to_csv('states/' + str(file))


def combine_rdi():
    personal_income_2020 = pd.read_csv('personal_income_2020.csv')['Mean'].values
    personal_income = pd.read_csv('personal_income.csv')
    personal_income = personal_income.iloc[:, 58:]
    pd.set_option('display.max_columns', 500)
    personal_income['2020'] = personal_income_2020
    value_state_election = {}
    for i, year in enumerate(years):
        range = slice(i, i + 4, 1)
        years_considered = personal_income.iloc[:, range].values
        for j, state in enumerate(years_considered):
            weighted_average = np.sum(weights * state) / 10
            try:
                value_state_election[j].append(weighted_average)
            except:
                value_state_election[j] = [weighted_average]

    for i, file in enumerate(os.listdir('states')):
        df_state = pd.read_csv('states/' + file)
        df_state.drop(df_state.columns[0], axis=1, inplace=True)
        rdi_state = value_state_election.get(i)
        final_rdi_state = []
        for i, year in enumerate(years):
            if year in np.unique(df_state['Year']):
                final_rdi_state.append(rdi_state[i])
                final_rdi_state.append(rdi_state[i])
            else:
                continue
        df_state['RDI'] = final_rdi_state
        # df_state.to_csv('states/' + file, index=False)


def combine_gdp():
    gdp = pd.read_csv('GDP_per_year.csv')
    gdp = gdp.iloc[:, 2:]
    value_state_election = {}
    for i, year in enumerate(years_gdp):
        range = slice(i, i + 4, 1)
        years_considered = gdp.iloc[:, range].values
        for j, state in enumerate(years_considered):
            weighted_average = np.sum(weights * state) / 10
            try:
                value_state_election[j].append(weighted_average)
            except:
                value_state_election[j] = [weighted_average]

    for i, file in enumerate(os.listdir('states')):
        df_state = pd.read_csv('states/' + file)
        df_state = df_state.iloc[6:, :]
        gdp_state = value_state_election.get(i)
        final_rdi_state = []
        for i, year in enumerate(years_gdp):
            if year in np.unique(df_state['Year']):
                final_rdi_state.append(gdp_state[i])
                final_rdi_state.append(gdp_state[i])
            else:
                continue
        df_state['GDP'] = final_rdi_state
        df_state.to_csv('states_with_GDP/' + file, index=False)


if __name__ == '__main__':
    pass





