import numpy as np
import pandas as pd
import datetime

import plotly
import plotly.express as px
import plotly.graph_objects as go

import warnings
warnings.simplefilter('ignore')

def generate_daily(dfs):
    new_dfs = []
    for df in dfs:
        daily = df.iloc[:,3:]
        daily = daily.diff(axis=1, periods=1)
        daily['Lat'] = df['Lat']
        daily['Long'] = df['Long']
        daily['Name'] = df['Name']
        cols = ['Name', 'Lat', 'Long'] + daily.columns.tolist()[:-3]
        daily = daily[cols]
        new_dfs.append(daily)
    return new_dfs

def plot(df, color, title):
    x = pd.DataFrame(df.iloc[:,3:].stack()).rename(columns={0:'cases'})
    x = x.reset_index().set_index('level_0').rename(columns={'level_1':'date'})
    x['Lat'] = df['Lat']
    x['Long'] = df['Long']
    x['Name'] = df['Name']
    x.index.name = 'index'

    fig = px.scatter_geo(x, lat=x['Lat'], lon=x['Long'],
                        hover_name="Name",
                        size="cases",
                        size_max=50,
                        animation_frame='date',
                        projection="natural earth",
                        width=900,height=540
                        )
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_layout(title_text=title, title_x=0.5)
    for f in fig.frames:
        f.data[0]['marker']['color'] = color
    return fig.to_json()

def generate_list(df, color):
    recent = df.columns[-1]
    recent_df = df[['Name',recent]]
    recent_df = recent_df.sort_values(by = recent, ascending = False)
    recent_df = recent_df[recent_df[recent] > 0]
    recent_df[recent] = recent_df[recent].astype(int)
    total = recent_df[recent].sum()

    ret = ""
    for row in recent_df.iterrows():
        ret += '<li class="list-group-item">' \
                + '<span class="text-'+ color +'">' \
                + str(row[1][recent]) \
                + '</span>  ' \
                + row[1]['Name'] \
                + '</li>'

    return total, ret

def generate_lists(dfs, colors, cases):
    lists = {}
    for df, color, case in zip(dfs, colors, cases):
        total, list = generate_list(df, color)
        lists[case] = {'total' : total, 'list' : list}
    return lists
        

def do_merge_df(confirmed, deaths, recovered):
    DATES = list(confirmed.columns)[3:]
    conf_lf = confirmed.melt(
        id_vars=['Name', 'Lat', 'Long'],
        value_vars=DATES,
        var_name='Date',
        value_name='Confirmed'
        )
    deaths_lf = deaths.melt(
        id_vars=['Name', 'Lat', 'Long'],
        value_vars=DATES,
        var_name='Date',
        value_name='Deaths'
        )
    recov_lf = recovered.melt(
        id_vars=['Name', 'Lat', 'Long'], 
        value_vars=DATES,
        var_name='Date',
        value_name='Recovered'
        )
    merged_df = conf_lf.merge(
        right=deaths_lf, 
        how='left',
        on=['Name', 'Date', 'Lat', 'Long']
        )
    merged_df = merged_df.merge(
        right=recov_lf, 
        how='left',
        on=['Name', 'Date', 'Lat', 'Long']
        )
    merged_df['Recovered'] = merged_df['Recovered'].fillna(0)
    merged_df['Active'] = merged_df['Confirmed'] - merged_df['Deaths'] - merged_df['Recovered']
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])
    return merged_df

def plot_trend(df):
    df = df.groupby('Date')['Confirmed', 'Deaths', 'Recovered'].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], 
                            y=df['Confirmed'], 
                            name='Confirmed', 
                            fill='tozeroy',
                            line=dict(color='royalblue', width=2),
                            ))
    fig.add_trace(go.Scatter(x=df['Date'], 
                            y=df['Recovered'], 
                            name='Recovered',
                            fill='tozeroy',
                            line=dict(color='green', width=2),
                            ))
    fig.add_trace(go.Scatter(x=df['Date'], 
                            y=df['Deaths'], 
                            name = 'Death', 
                            fill='tozeroy',
                            line=dict(color='firebrick', width=2),
                            ))

    fig.update_layout(title='Covid 19 worldwide trend (March)',
                    xaxis_title='Date',
                    yaxis_title='Count',
                    title_x=0.5,
                    width=900,
                    height=540)
    return fig.to_json()

def log_ratio(df, daily):
    df = df.set_index('Name')
    daily = daily.set_index('Name')

    log_daily = np.log(daily.iloc[:,3:]).replace([np.inf, -np.inf], 0)
    log_df = np.log(df.iloc[:,3:]).replace([np.inf, -np.inf], 0)

    log_df = log_daily/log_df
    log_df = log_df.fillna(0)

    log_df['Long'] = daily['Long']
    log_df['Lat'] = daily['Lat']
    cols = ['Long', 'Lat']+log_df.columns.to_list()[:-2]

    log_df = log_df[cols].reset_index()
    return log_df

def plot_log(df):
    DATES = list(df.columns)[3:]
    df = df.melt(
        id_vars=['Name', 'Lat', 'Long'],
        value_vars=DATES,
        var_name='Date',
        value_name='Confirmed'
        )
    fig = px.choropleth(
        df,
        locations='Name',
        hover_name='Name',
        locationmode='country names',
        color='Confirmed',
        animation_frame='Date',
        projection='natural earth',
        title=f'World-wide ratio of log daily and log cummulative confirmed cases',
        width=900,
        height=540)

    return fig.to_json()

