from gc import callbacks
import graphlib
from turtle import width
from unittest.case import DIFF_OMITTED
import pandas as pd
import plotly.express as px

import dash
from dash import html, dcc
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Get bees data and clean it
df = pd.read_csv("intro_bees.csv")

df = df.groupby(["State", 'ANSI', 'Affected by', 'Year', 'state_code'])[
    ['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)

plagueNames = {
    'Disease': 'Disease',
    'Other': 'Other',
    'Pesticides': 'Pesticides',
    'Pests_excl_Varroa': 'P. without Varroa',
    'Unknown': 'Unknown',
    'Varroa_mites': 'Varroa Mites'
}

# Plague types: ['Disease', 'Other', 'Pesticides', 'Pests_excl_Varroa', 'Unknown', 'Varroa_mites']
affectationOptions = [
    {'label': 'Disease', 'value': 'Disease'},
    {'label': 'Pesticides', 'value': 'Pesticides'},
    {'label': 'Varroa Mites', 'value': 'Varroa_mites'},
    {'label': 'P. without Varroa', 'value': 'Pests_excl_Varroa'},
    {'label': 'Other', 'value': 'Other'},
    {'label': 'Unknown', 'value': 'Unknown'},
]

yearOptions = [
    {'label': '2015', "value": 2015},
    {"label": "2016", "value": 2016},
    {"label": "2017", "value": 2017},
    {"label": "2018", "value": 2018}
]

# Age and plague pickers


def itemSelector():
    return html.Div(
        style={
            'display': 'flex',
            'align-items': 'center',
            'border-bottom': 'solid 2px gray',
            'justify-content': 'space-between',
            'padding': '0.2em'
        },
        children=[
            html.Div(
                dcc.Dropdown(
                    id='slct_year',
                    options=yearOptions,
                    multi=False,
                    value=2015,
                    clearable=False,
                    searchable=False,
                ),
                style={'width': '10em'}
            ),
            html.Div(id='output_container', children=[]),
            html.Div(
                dcc.Dropdown(
                    id='slct_affect',
                    options=affectationOptions,
                    multi=False,
                    value="Varroa_mites",
                    clearable=False,
                    searchable=False,
                ),
                style={'width': '10em'}
            )
        ])


app.title = 'Bees'

graphStyles = {
    'width': '48%',
    'min-width': '38em',
    'padding-bottom': '0.2em'
}

# App layout
app.layout = html.Div(
    [
        html.H1('Bee Colinies and Diseases',
                style={'text-align': 'center'}),
        itemSelector(),
        html.Br(),
        html.Div([
            html.Div([dcc.Graph(id='bee_map', figure={})], style=graphStyles),
            html.Div([dcc.Graph(id='bee_pie', figure={})], style=graphStyles),
        ], style={
            'display': 'flex',
            'flex-wrap': 'wrap',
            'justify-content': 'space-evenly'
        }
        ),
        html.Div([dcc.Graph(id='bee_line', figure={})]),
    ], style={'font-family': 'Sans-Serif'})

# Communicate graphs with UI components (MAP)


@app.callback(
    Output(component_id='output_container', component_property='children'),
    Output(component_id='bee_map', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_affect', component_property='value'),
)
def update_graph(yr_slctd, affect_slctd):

    container = "Selected year: {}, Affection: {}".format(
        yr_slctd, affect_slctd)

    # Create a copy of the main dataframe to avoid mutations in the callback
    dff = df.copy()
    dff = dff[dff["Year"] == yr_slctd]
    dff = dff[dff["Affected by"] == affect_slctd]

    # Create map figure and send it to component through the output
    fig = px.choropleth(
        title="Bees affected",
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope='usa',
        color='Pct of Colonies Impacted',
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Pct of Colonies Impacted': 'Affected Colonies (%)'},
        template='plotly_dark'
    )

    return container, fig

# Pie Comunication


@app.callback(
    Output(component_id='bee_pie', component_property='figure'),
    Output(component_id='bee_line', component_property='figure'),
    Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_affect', component_property='value'),
)
def update_pie(yr_slctd, affect_slctd):
    # Pie data
    pie_df = df.copy()
    pie_df = pie_df[pie_df["Year"] == yr_slctd]
    chart_df = pie_df.groupby('Affected by').mean()
    chart_df['Affected by'] = chart_df.index
    print('chart_df')
    print(chart_df)

    # Line data
    line_df = df.copy()
    line_df = line_df[line_df['Affected by'] == affect_slctd]
    line_chart_df = line_df.groupby(['Year']).mean()
    line_chart_df['Year'] = line_chart_df.index
    print('line_chart_df')
    print(line_chart_df)

    # Pie Cahrt
    pie_fig = px.pie(
        chart_df,
        title=f"Diseases in year {yr_slctd}",
        values='Pct of Colonies Impacted',
        names='Affected by',
        color_discrete_sequence=px.colors.sequential.Redor,
        template='plotly_dark'
    )

    # Line Chart
    line_fig = px.line(
        line_chart_df,
        x='Year',
        y='Pct of Colonies Impacted',
        title=f'Trend of disease: {affect_slctd}',
        color_discrete_sequence=px.colors.sequential.Redor,
        template='plotly_dark'
    )

    return pie_fig, line_fig


if (__name__ == '__main__'):
    app.run(debug=True)
