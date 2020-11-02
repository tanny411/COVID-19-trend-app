from covid_19_flask_app import app
from flask import Flask, render_template, redirect, url_for
from covid_19_flask_app.preprocess import *
from covid_19_flask_app.preprocess_US import *

path = 'data/'

confirm         = pd.read_csv(path+'march_confirmed.csv')
confirm_global  = pd.read_csv(path+'march_confirmed_global.csv')
confirm_US      = pd.read_csv(path+'march_confirmed_US.csv')

death           = pd.read_csv(path+'march_deaths.csv')
death_global    = pd.read_csv(path+'march_deaths_global.csv')
death_US        = pd.read_csv(path+'march_deaths_US.csv')

active          = pd.read_csv(path+'march_active_global.csv')
recovered_global= pd.read_csv(path+'march_recovered_global.csv')

merge_df = do_merge_df(confirm_global, death_global, recovered_global)
merge_df_US = do_merge_df_US(confirm_US, death_US)

daily_confirm, daily_death, daily_recovered_global, daily_death_US, daily_confirm_US = \
    generate_daily([confirm, death, recovered_global, death_US, confirm_US])

daily_merge_df = do_merge_df(daily_confirm, daily_death, daily_recovered_global)
daily_merge_df_US = do_merge_df_US(daily_confirm_US, daily_death_US)

log_df_global = log_ratio(confirm_global, daily_confirm)
log_df_US = log_ratio(confirm_US, daily_confirm_US)

@app.route('/')
def home():
    return redirect(url_for('_global'))

@app.route('/confirmed')
def confirmed():
    return render_template('confirmed.html')

@app.route('/deaths')
def deaths():
    return render_template('deaths.html')

@app.route('/lockdown')
def lockdown():
    return render_template('confirmed.html')

@app.route('/global')
def _global():
    figs={
        'confirmed_animation' : plot(confirm,   'blue',     'World-wide Comfirmed Cases Count (March)'),
        'deaths_animation'    : plot(death,     'red',      'World-wide Death Count (March)'),
        'recovered_animation' : plot(recovered_global, 'green',    'World-wide Recovered Count (March)'),
        'active_animation'    : plot(active,    'yellow',   'World-wide Active Cases Count (March)'),
        }

    lists = generate_lists([confirm_global, death_global, active, recovered_global],
                       ['primary', 'danger', 'warning', 'success'],
                       ['confirmed', 'deaths', 'active', 'recovered'])

    trend_graph = plot_trend(merge_df)
    daily_trend_graph = plot_trend(daily_merge_df)
    log_plot = plot_log(log_df_global)

    return render_template('global.html', 
                            data = figs, 
                            lists = lists, 
                            trend = trend_graph,
                            daily_trend = daily_trend_graph,
                            log_plot = log_plot
                            )

@app.route('/us')
def us():
    figs={
        'confirmed_animation' : plot_US(confirm_US,   'blue',     'US Comfirmed Cases Count (March)'),
        'deaths_animation'    : plot_US(death_US,     'red',      'US Death Count (March)')
        }

    lists = generate_lists_US([confirm_US, death_US],
                       ['primary', 'danger'],
                       ['confirmed', 'deaths'])

    trend_graph = plot_trend_US(merge_df_US)
    daily_trend_graph = plot_trend_US(daily_merge_df_US)

    return render_template('us.html', 
                            data = figs, 
                            lists = lists, 
                            trend = trend_graph,
                            daily_trend = daily_trend_graph
                            )