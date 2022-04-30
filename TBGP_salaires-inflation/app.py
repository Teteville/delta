from click import style
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import plotly.express as px
import get_data
import json


class SalaryInflation():
    def __init__(self):
        self.df = get_data.get_data()
        self.years = self.df.year.unique()
        self.geodata = json.load(open('data/europe.geojson'))
        print(self.years)
        self.app = dash.Dash()
        self.app.layout = html.Div(children=[
            html.H3(children='Comparaison salaire / inflation',
                    style={'textAlign': 'center'}),
            html.Div([dcc.Graph(id='europe-map'),
                     html.Div(id='year', style={'textAlign': 'center'})], style={'display': 'inline', 'justifyContent': 'center', 'width': '80%'}),
            dcc.Slider(
                id='year-filter-slider',
                min=self.years[0],
                max=self.years[-1],
                step=1,
                value=self.years[-1],
                marks={str(year): str(year)
                       for year in range(self.years[0], self.years[-1]+1, 5)}
            ),
            # dcc.Markdown(id='md'),
            html.Div([
                dcc.Graph(id='men-graph',
                          style={'width': '33%', 'display': 'inline-block'}),
                dcc.Graph(id='total-graph',
                          style={'width': '33%', 'display': 'inline-block', 'padding-left': '0.5%'}),
                dcc.Graph(id='women-graph',
                          style={'width': '33%', 'display': 'inline-block', 'padding-left': '0.5%'}),
            ], style={'display': 'flex', 'justifyContent': 'center', }),

        ])

        self.app.callback(
            dash.dependencies.Output('year', 'children'),
            dash.dependencies.Input('year-filter-slider', 'value'))(self.update_year)

        self.app.callback(
            dash.dependencies.Output('europe-map', 'figure'),
            dash.dependencies.Input('year-filter-slider', 'value'))(self.update_graph)

        self.app.callback(
            dash.dependencies.Output('md', 'children'),
            dash.dependencies.Input('europe-map', 'clickData'))(self.print_hover)

        self.app.callback(
            dash.dependencies.Output('total-graph', 'figure'),
            [dash.dependencies.Input('europe-map', 'clickData'),
             dash.dependencies.Input('year-filter-slider', 'value')])(self.update_total_graph)
        self.app.callback(
            dash.dependencies.Output('men-graph', 'figure'),
            [dash.dependencies.Input('europe-map', 'clickData'),
             dash.dependencies.Input('year-filter-slider', 'value')])(self.update_men_graph)
        self.app.callback(
            dash.dependencies.Output('women-graph', 'figure'),
            [dash.dependencies.Input('europe-map', 'clickData'),
             dash.dependencies.Input('year-filter-slider', 'value')])(self.update_women_graph)

    def update_year(self, year):
        return f'Année: {year}'

    def print_hover(self, hover):
        if hover is None:
            return 'EU27_2020'
        return hover['points'][0]['location'] if hover['points'][0]['location'] != 'UK' else 'GB'

    def update_graph(self, year):
        data = self.df[(self.df.year == int(year)) & (self.df.age == 'TOTAL') & (
            self.df.sex == 'T')][['country', 'cumulative_sum']]
        fig = px.choropleth_mapbox(data, geojson=self.geodata,
                                   locations='country', featureidkey='properties.ISO2',  # join keys
                                   color='cumulative_sum', color_continuous_scale="Viridis",
                                   mapbox_style="carto-positron",
                                   zoom=3, center={"lat": 52, "lon": 10},
                                   opacity=0.5,
                                   )
        fig.update_layout(
            title=f"{year}",
            margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
            hovermode='closest',
            showlegend=False,
        )
        return fig

    def update_total_graph(self, hover, year):
        country = self.print_hover(hover)
        country_df = self.df[(self.df.country == country) & (
            self.df.sex == 'T') & (self.df.age == 'TOTAL')]
        w = country_df.wages_value.iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=country_df.year, y=country_df.wages_value, mode='lines', name='Salaire réel'))
        fig.add_trace(go.Scatter(x=country_df.year, y=country_df.cumulative_sum * w, mode='lines', name='Inflation'))
        fig.update_layout(
            title = 'Évolution du salaire médian en comparaison avec l\'inflation.<br>Lieu : ' + country_name[country] + '<br><sup>Au total</sup>',
            title_font_size = 12,
            title_xanchor = 'auto',
            title_pad = { 't': 0, 'b': 0, 'l': 0, 'r': 0},
            height=450,
            hovermode='closest',
            legend = {'title': 'Courbes'},
            xaxis_title='Année',
            yaxis_title='Valeur médiane',
        )
        return fig

    def update_men_graph(self, hover, year):
        country = self.print_hover(hover)
        country_df = self.df[(self.df.country == country) & (
            self.df.sex == 'M') & (self.df.age == 'TOTAL')]
        w = country_df.wages_value.iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=country_df.year, y=country_df.wages_value, mode='lines', name='Salaire réel'))
        fig.add_trace(go.Scatter(x=country_df.year, y=country_df.cumulative_sum * w, mode='lines', name='Inflation'))
        fig.update_layout(
            title = 'Évolution du salaire médian en comparaison avec l\'inflation.<br>Lieu : ' + country_name[country] + '<br><sup>Chez les hommes</sup>',
            title_font_size = 11,
            title_xanchor = 'auto',
            title_pad = { 't': 0, 'b': 0, 'l': 0, 'r': 0},
            height=450,
            hovermode='closest',
            legend = {'title': 'Courbes'},
            xaxis_title='Année',
            yaxis_title='Valeur médiane',
        )
        return fig

    def update_women_graph(self, hover, year):
        country = self.print_hover(hover)
        country_df = self.df[(self.df.country == country) & (
            self.df.sex == 'F') & (self.df.age == 'TOTAL')]
        w = country_df.wages_value.iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=country_df.year, y=country_df.wages_value, mode='lines', name='Salaire réel'))
        fig.add_trace(go.Scatter(x=country_df.year, y=country_df.cumulative_sum * w, mode='lines', name='Inflation'))
        fig.update_layout(
            title = 'Évolution du salaire médian en comparaison avec l\'inflation.<br>Lieu : ' + country_name[country] + '<br><sup>Chez les femmes</sup>',
            title_font_size = 11,
            title_xanchor = 'auto',
            title_pad = { 't': 0, 'b': 0, 'l': 0, 'r': 0},
            height=450,
            hovermode='closest',
            legend = {'title': 'Courbes'},
            xaxis_title='Année',
            yaxis_title='Valeur médiane',
        )
        return fig

    def run(self, debug=False, port='8000'):
        self.app.run_server(host='0.0.0.0', debug=debug, port=port)


country_name = {
    'AT': 'Autriche',
    'BE': 'Belgique',
    'CZ': 'République tchèque',
    'DK': 'Danemark',
    'FI': 'Finlande',
    'FR': 'France',
    'DE': 'Allemagne',
    'GR': 'Grèce',
    'HU': 'Hongrie',
    'IS': 'Islande',
    'IE': 'Irlande',
    'IT': 'Italie',
    'LU': 'Luxembourg',
    'NL': 'Pays-Bas',
    'NO': 'Norvège',
    'PL': 'Pologne',
    'PT': 'Portugal',
    'SK': 'Slovaquie',
    'ES': 'Espagne',
    'SE': 'Suède',
    'TR': 'Turquie',
    'GB': 'Royaume-Unis',
    'EE': 'Estonie',
    'SI': 'Slovénie',
    'LV': 'Lettonie',
    'LT': 'Lituanie',
    'EU27_2020': 'Union Européenne'
}

if __name__ == '__main__':
    si = SalaryInflation()
    si.run(port='8045')