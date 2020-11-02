import numpy as np
import pandas as pd
import datetime

import plotly
import plotly.express as px
import plotly.graph_objects as go

import warnings
warnings.simplefilter('ignore')

def plot_US(df, color, title):
    x = pd.DataFrame(df.iloc[:,3:].stack()).rename(columns={0:'cases'})
    x = x.reset_index().set_index('level_0').rename(columns={'level_1':'date'})
    x['Lat'] = df['Lat']
    x['Long'] = df['Long']
    x['Name'] = df['Name'].map(lambda s: s[:-4])
    x.index.name = 'index'

    fig = px.scatter_geo(x, lat=x['Lat'], lon=x['Long'],
                        hover_name="Name",
                        size="cases",
                        size_max=50,
                        animation_frame='date',
                        width=900,height=540
                        )
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_layout(title_text=title, title_x=0.5, geo_scope='usa')
    for f in fig.frames:
        f.data[0]['marker']['color'] = color
    return fig.to_json()

def generate_list_US(df, color):
    recent = df.columns[-1]
    recent_df = df[['Name',recent]]
    recent_df['Name'] = recent_df['Name'].map(lambda s: s[:-4])
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

def generate_lists_US(dfs, colors, cases):
    lists = {}
    for df, color, case in zip(dfs, colors, cases):
        total, list = generate_list_US(df, color)
        lists[case] = {'total' : total, 'list' : list}
    return lists

def do_merge_df_US(confirmed, deaths):
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
    merged_df = conf_lf.merge(
        right=deaths_lf, 
        how='left',
        on=['Name', 'Date', 'Lat', 'Long']
        )
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])
    return merged_df

def plot_trend_US(df):
    df = df.groupby('Date')['Confirmed', 'Deaths'].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], 
                            y=df['Confirmed'], 
                            name='Confirmed', 
                            fill='tozeroy',
                            line=dict(color='royalblue', width=2),
                            ))
    fig.add_trace(go.Scatter(x=df['Date'], 
                            y=df['Deaths'], 
                            name = 'Death', 
                            fill='tozeroy',
                            line=dict(color='firebrick', width=2),
                            ))

    fig.update_layout(title='Covid 19 US trend (March)',
                    xaxis_title='Date',
                    yaxis_title='Count',
                    title_x=0.5,
                    width=900,
                    height=540)
    return fig.to_json()