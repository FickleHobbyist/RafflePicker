import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import raffle.db.utils as rdbu
import pandas as pd

example_users = [u['name'] for u in rdbu.get_all_users()]

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    title='Raffle Admin',
    suppress_callback_exceptions=True
)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

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
        # dbc.NavbarToggler(id="navbar-toggler"),
        # dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)

sale_input = [
    dbc.Row([
        dbc.Col(
            html.H3("Add new or edit existing sale data:"),
            width=5
        ),
        dbc.Col([
            dbc.RadioItems(
                id="add-edit-radio",
                options=[
                    {"label": "Add", "value": 1},
                    {"label": "Edit", "value": 2},
                ],
                value=1,
                persistence=True,
                inline=True,
                className='mt-1 d-flex justify-content-center',
            ),
        ],
            width=2,
        ),
        dbc.Col([
            dbc.Input(
                value=None,
                id="edit-sale-id-input",
                placeholder='Sale ID to Edit',
                type="number",
                min=1,
                step=1,
                persistence=False,
                disabled=True,
            ),
        ],
            width=2
        ),
    ],
        align='center',
        className='mb-1 mt-1',
        form=True
    ),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [dbc.InputGroupAddon("@", addon_type="prepend"),
                 dbc.Input(
                     value='',
                     id="username-input",
                     placeholder="Username",
                     type="text",
                     debounce=True,
                     persistence=True,
                     autoComplete=False,
                     list='existing-users',
                     maxLength=25,
                 )
                 ],
            ),
            width=3,
        ),
        dbc.Col(
            dbc.Input(
                value=None,
                id="num-tickets-input",
                placeholder='Number of Tickets',
                type="number",
                min=1,
                step=1,
                persistence=False,
            ),
            width=2,
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Checkbox(
                    id="prize-addition-input",
                    checked=False,
                    persistence=False,
                    className='form-check-input'
                ),
                dbc.Label(
                    'Prize Addition',
                    html_for='prize-addition-input',
                    className='form-check-label'
                )
            ],
                check=True,
                # inline=True,
            ),

            width=2,
            className='d-flex justify-content-center'
        ),
        dbc.Col([
            dbc.Button(
                "Add Sale",
                id='sale-submit-button',
                color='primary',
                block=True
            ),
        ],
            width=2,
            align='center',
        ),

    ],
        align="center",
        form=True
    ),
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
    [Output('username-input', 'value'),
     Output('num-tickets-input', 'value'),
     Output('prize-addition-input', 'checked'),
     Output('edit-sale-id-input', 'invalid')],
    [Input('edit-sale-id-input', 'n_submit'),
     State('edit-sale-id-input', 'value')
     ],
)
def edit_sale_id_populated(nsub, sale_id: int):
    invalid = False
    if sale_id is not None:
        sale = rdbu.get_sale(sale_id)
        if sale is not None:
            return sale['user_name'], sale['num_tickets'], sale['prize_addition'], invalid
        else:
            invalid = True

    return [], [], False, invalid


@app.callback(
    [Output("edit-sale-id-input", 'disabled'),
     Output("edit-sale-id-input", 'value'),
     Output('sale-submit-button', 'children')],
    [Input('add-edit-radio', 'value'),
     State("edit-sale-id-input", 'value')],
)
def add_edit_sale_toggled(value: int, current_id: int):
    if value == 1:
        return True, None, 'Add Sale'  # add sale
    elif value == 2:
        return False, current_id, 'Edit Sale'  # edit sale


@app.callback(
    [Output('username-input', 'invalid'),
     Output('num-tickets-input', 'invalid'),
     Output('sale-output-alert', 'children'),
     Output('sale-output-alert', 'color'),
     Output('sale-output-alert', 'is_open')],
    [Input('sale-submit-button', 'n_clicks'),
     State('username-input', 'value'),
     State('num-tickets-input', 'value'),
     State('prize-addition-input', 'checked'),
     State('add-edit-radio', 'value'),
     State('edit-sale-id-input', 'value')],
)
def submit_sale_clicked(n: int, user_name: str, num_tickets: int, prize_addition: bool, add_edit_value: int,
                        sale_id: int):
    failure_content, failure_color = sale_failure_content()
    # Verify all info is present
    out = {'name-invalid': False,
           'num-invalid': False,
           'alert-children': failure_content,
           'alert-color': failure_color,
           'alert-open': False if n is None else True
           }
    if n is None:
        return *out.values(),

    flag = False
    if user_name is None or (isinstance(user_name, (list, str)) and len(user_name) == 0):
        out['name-invalid'] = True
        flag = True
    if num_tickets is None or (isinstance(num_tickets, list) and len(num_tickets) == 0):
        out['num-invalid'] = True
        flag = True
    if flag:
        return *out.values(),

    if sale_id is None and add_edit_value == 1:
        # user adding a new sale
        sale_id = rdbu.add_sale(user_name, num_tickets, prize_addition)

        out['alert-children'], out['alert-color'] = sale_success_content(sale_id, 'Added')
    elif add_edit_value == 2:
        rdbu.edit_sale(sale_id, user_name, num_tickets, prize_addition)
        out['alert-children'], out['alert-color'] = sale_success_content(sale_id, 'Edited')
    return *out.values(),


def sale_success_content(sale_id, add_edit):
    content = [
        html.H4('Success!'),
        html.P(f'{add_edit} sale with sale ID: {sale_id}.',
               className='mb-0'),
    ]
    return content, 'success'


def sale_failure_content():
    content = [
        html.H4('Oops! Looks like you forgot something.'),
        html.P('The highlighted fields are required.',
               className='mb-0'),
    ]
    return content, 'danger'


# @app.callback(
#     [],
#     [Input('sale-output-alert', 'is_open'),
#      State('sale-output-alert', 'color')]
# )
# def
#


@app.callback(
    Output('card-content', 'children'),
    [Input('card-tabs', 'active_tab'),
     Input('sale-output-alert', 'is_open'),
     ]
)
def tab_swap(active_tab, alert_open):
    if active_tab == 'sales-tab':
        return get_sale_table_content()
    else:
        return []


def get_sale_table_content():
    sale_data = rdbu.get_all_sales()
    sale_col_clean = ['Sale ID', 'Username', 'Number of Tickets', 'Prize Addition']
    sales_df = pd.DataFrame.from_dict(sale_data)
    sales_df = sales_df.drop(columns=['time_created'])

    sale_tab = [
        dash_table.DataTable(
            id='sales-table',
            columns=[{'id': key, 'name': val, } for key, val in zip(sales_df.columns, sale_col_clean)],
            # returns keys of the dict in first sale
            data=sales_df.to_dict('records'),
            page_size=10,
            editable=False,
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            cell_selectable=False,
            sort_by=[{'column_id': 'id', 'direction': 'desc'}]
        )
    ]
    return sale_tab

# def get_drawing_table_content():


# # add callback for toggling the navbar collapse on small screens
# @app.callback(
#     Output("navbar-collapse", "is_open"),
#     [Input("navbar-toggler", "n_clicks")],
#     [State("navbar-collapse", "is_open")],
# )
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open


if __name__ == '__main__':
    app.run_server(debug=True)
