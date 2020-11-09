import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import raffle.db.utils as rdbu
import pandas as pd

rdbu.load_sample_data()

example_users = [u['name'].lstrip('@') for u in rdbu.get_all_users()]

sale_data = rdbu.get_all_sales()

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

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

sale_input = [
    dbc.Row(
        dbc.Col(
            html.H3("Enter new sale data below"), align='left'
        ),
    ),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [dbc.InputGroupAddon("@", addon_type="prepend"),
                 dbc.Input(id="username-input",
                           placeholder="Username",
                           type="text",
                           debounce=True,
                           persistence=False,
                           autoComplete=False,
                           list='existing-users')
                 ],
            ),
            width='auto',
        ),
        dbc.Col(
            dbc.Input(id="num-tickets-input",
                      placeholder='# of Tickets',
                      type="number",
                      min=1,
                      step=1,
                      persistence=False
                      ),
            width='auto',
        ),
        dbc.Col(
            dbc.Checklist(
                id="prize-addition-input",
                options=[{"label": "Prize Addition", "value": 1}],
                value=0,
                switch=True,
                persistence=False
            ),
            width='auto',
        ),
        dbc.Col(
            dbc.Button("Add Sale", id='sale-submit-button', color='primary'),
            width='auto',
        ),
    ],
        align="center",
        form=True
    )
]

sale_output = dbc.Row(
    dbc.Col(
        dbc.Alert(
            "Placeholder text",
            id='sale-output-alert',
            dismissable=True,
            fade=True,
            is_open=False,
            color='success',
            className='mt-3'
        ),
    ), align='center',
)

# sale_table = [
#     dbc.Row(
#         dbc.Col(html.H3('Sales History'))
#     ),
#     dbc.Form(
#         dbc.FormGroup([
#             dbc.Label('Showing', className='mr-2'),
#             dbc.Input(
#                 id='n-sales-input',
#                 placeholder=5,
#                 type="number",
#                 min=1, max=100, step=1,
#             ),
#             dbc.Label('sales', className='ml-2')
#         ]),
#         inline=True
#     ),
# ]

sale_col_clean = ['Sale ID', 'Username', '# Tickets', 'Prize Addition']

sales_df = pd.DataFrame.from_dict(sale_data)

sale_tab = [
    dash_table.DataTable(
        id='sales-table',
        columns=[{'id': key, 'name': key, } for key in sale_data[0]],  # returns keys of the dict in first sale
        data=sale_data,
        page_size=10
    )
]


tab_grp = [
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label='Sales', tab_id='sales-tab'),
                    dbc.Tab(label='Drawings', tab_id='drawings-tab'),
                    dbc.Tab(label='Users', tab_id='users-tab'),
                ],
                    card=True,
                    id='card-tabs',
                    active_tab='sales-tab'
                ),

            ),
            dbc.CardBody(id='card-content')
        ]
    )
]

# Put the layout together
app.layout = dbc.Container(
    [
        navbar,
        # html.P(),
        *sale_input,
        sale_output,
        dbc.Row(dbc.Col(html.Hr())),
        dbc.Row(dbc.Col(tab_grp)),
        # Data storage below here
        html.Div(
            html.Datalist([html.Option(value=usr) for usr in example_users],
                          id='existing-users'),
            style={'display': 'none'}
        )
    ],
)


@app.callback(
    [Output('sale-output-alert', 'children'),
     Output('sale-output-alert', 'color'),
     Output('sale-output-alert', 'is_open')],
    [Input('sale-submit-button', 'n_clicks'),
     State('username-input', 'value'),
     State('num-tickets-input', 'value'),
     State('prize-addition-input', 'value')],
)
def add_sale_clicked(n: int, user_name: str, num_tickets: int, prize_addition: bool):
    prize_addition = prize_addition[0] if isinstance(prize_addition, list) else prize_addition
    if prize_addition:
        out_ch = [
            html.H4('Success!'),
            html.P('Added sale with the following information:'),
            html.P(f'User: @{user_name} | # Tickets: {num_tickets} | '
                   f'Prize Addition: {True if prize_addition == 1 else False} | '
                   f'N_Clicks: {n}',
                   className='mb-0'),
            html.Hr(),
            html.P('If you need to edit this sale, edit sale ID #xx in the sales table below.')
        ]
        color = 'success'
    else:
        out_ch = [
            html.H4('Oops! Something went wrong.'),
            html.P('Could not enter the sale as specified.',
                   className='mb-0'),
        ]
        color = 'danger'

    return out_ch, color, False if n is None else True


@app.callback(
    Output('card-content', 'children'),
    [Input('card-tabs', 'active_tab')]
)
def tab_swap(active_tab):
    if active_tab == 'sales-tab':
        return sale_tab
    else:
        return []


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
