import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button("Search", color="primary", className="ml-2"),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("Raffle Admin", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="#",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)

sale_input = dbc.Row(
    [
        dbc.Col(
            dbc.InputGroup(
                [dbc.InputGroupAddon("@", addon_type="prepend"),
                 dbc.Input(id="username-input",
                           placeholder="Username",
                           type="text",
                           debounce=True)
                 ],
                className='mb-3'
            ),
        ),
        dbc.Col(
            dbc.InputGroup(
                dbc.Input(id="num-tickets-input",
                          placeholder='Number of Tickets',
                          type="number",
                          min=1
                          )
            ),
        ),
        dbc.Col(
            dbc.Checklist(
                id="prize-addition-input",
                options=[{"label": "Prize Addition", "value": 1}],
                value=0,
                switch=True,
                persistence=True
            ),
            style={"vertical-align": "middle", "horizontal-align": "center"},
        ),
        dbc.Col(
            dbc.Button("Add Sale", id='sale-submit-button', color='primary')
        )
    ]
)
sale_output = dbc.Row(
    html.P(id='sale-output')
)

app.layout = dbc.Container(
    [
        navbar,
        html.Div([
            html.H3("Enter new sale data below"),
            sale_input,
            sale_output
        ])
    ]
)


@app.callback(
    Output('sale-output', 'children'),
    [Input('sale-submit-button', 'n_clicks'),
     State('username-input', 'value'),
     State('num-tickets-input', 'value'),
     State('prize-addition-input', 'value')]
)
def add_sale_clicked(n: int, user_name: str, num_tickets: int, prize_addition: bool):
    return f'User: @{user_name}, # Tickets: {num_tickets}, Prize Addition: {True if prize_addition == 1 else False}, N_Clicks: {n}'


# add callback for toggling the navbar collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)
