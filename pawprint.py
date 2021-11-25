#! 
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

def graph(df):

    df.loc[:, 'date'] = pd.to_datetime(df['date'])
    df_symptom = df[(df['category'] == 'Symptom')]
    df_energy = df[(df['category'] == 'Energy')]
    df_sleep = df[(df['category'] == 'Sleep')]
    df_factors = df[(df['category'] == 'Factors')]
    df_daily = pd.DataFrame(columns = ['date', 'symptom_sum'])
    df_daily.loc[:, 'date'] = df['date'].unique()

    df_sleep.loc[:, 'rating/amount'] = df_sleep['rating/amount'].astype('string') 
    df_sleep.loc[:, 'rating/amount'] = df_sleep['rating/amount'] + ":0"

    # gather daily counts
    for date in df['date'].unique():
        # for symptoms
        symptom_ondate = df_symptom[(df_symptom['date'] == date)]
        symptom_sum = [date, symptom_ondate['rating/amount'].astype(int).sum()][1]

        # for energy
        energy_ondate = df_energy[(df_energy['date'] == date)]
        energy_sum = [date, energy_ondate['rating/amount'].astype(int).sum()][1]

        # for sleep
        sleep_ondate = df_sleep[(df_sleep['date'] == date)]
        sleep_count = [date, sleep_ondate['rating/amount']][1]
        sleep_count = pd.to_timedelta(sleep_count, errors='ignore')
        sleep_count = sleep_count / datetime.timedelta(minutes=1) / 60
        # print("1 --- sleep count: ", sleep_count)

        ind = df_daily[(df_daily['date'] == date)].index

        try:
            df_daily.loc[ind, 'symptom_sum'] = symptom_sum
            df_daily.loc[ind, 'energy_sum'] = energy_sum
            df_daily.loc[ind, 'sleep_count'] = sleep_count.sum()

        except Exception as e:
            print("Exception: ", e)
    # print("ind, energy_sum: ", df_daily.loc[ind, 'energy_sum'])
    # print("2 --- ind, sleep_count: ", df_daily.loc[ind, 'sleep_count'])

    # filna makes 0's out of missing values for every date! this can distort data!
    # df_daily.fillna(value=0, inplace=True)

    # rolling average params
    avg_days = 5

    #symptoms
    df_daily['symptom_sum'] = df_daily['symptom_sum'].astype(float)
    df_daily['symptom_avg'] = df_daily['symptom_sum'].rolling(avg_days).mean()

    # energy
    df_daily['energy_sum'] = df_daily['energy_sum'].astype(float)
    df_daily['energy_avg'] = df_daily['energy_sum'].rolling(avg_days).mean()

    #sleep
    df_daily['sleep_count'] = df_daily['sleep_count'].astype(float)
    df_daily['sleep_avg'] = df_daily['sleep_count'].rolling(avg_days).mean()

    fig_date = df_daily.date
    fig_symp = df_daily.symptom_sum
    fig_rolling = df_daily.symptom_avg
    fig_energy = df_daily.energy_avg
    fig_sleep = df_daily.sleep_avg
    # fig_app_usage = df_daily.app_usage
    # fig_app_usage_avg = df_daily.app_usage_avg
    # fig_notes = df_daily.notes

    # print(df_daily)
    # print(df_daily.loc[(df_daily['date'] == '2020-10-08')].index[0])

    fig = go.Figure()
    # fig.add_trace(go.Scatter(x=df_daily.date, y=fig_symp,
    #                     mode='lines+text',
    #                     name='Symptom score',
    #                     line_shape='spline'
    #                     # text=fig_notes
    #                     ))
    fig.add_trace(go.Scatter(x=df_daily.date, y=fig_rolling,
                        mode='lines',
                        name='Symptoms',
                        line_shape='spline'))
    fig.add_trace(go.Scatter(x=df_daily.date, y=fig_energy,
                        mode='lines',
                        name='Energy',
                        line_shape='spline'))
    fig.add_trace(go.Scatter(x=df_daily.date, y=fig_sleep,
                        mode='lines',
                        name='Sleep',
                        line_shape='spline',
                        connectgaps=True))
    fig.update_layout(
        width=900,
        height=400,
        autosize=False,
        margin=dict(t=40, b=10, l=10, r=10),
        template="plotly",
        )

    return fig
