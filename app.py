from calendar import weekday
import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

data = pd.read_csv("monthly_bus_data_for_visual.csv")
# data["Date"] = pd.to_datetime(data["date_col"], format="%m/%d/%Y")
data["Date"] = pd.to_datetime(data["date_col"], format="%Y-%m-%d")
data.sort_values("Date", inplace=True)

# external_stylesheets = [
#     {
#         "href": "https://fonts.googleapis.com/css2?"
#         "family=Lato:wght@400;700&display=swap",
#         "rel": "stylesheet",
#     },
# ]
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

dash_app = dash.Dash(__name__, assets_folder = 'assets')
app = dash_app.server
dash_app.title = "Florida Transit Performance Dashboard"


# Layout of the app
dash_app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🚌", className="header-emoji"),
                html.H1(
                    children="Florida Transit Performance Dash", className="header-title"
                ),
                html.P(
                    children="The trend of Florida Transit Agencies bus VOMS (Vehicles Operated  "
                    " in Annual Maximum Service) in last ten years"
                    " between 2010 and 2022",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Transit Agency Grouping", className="menu-title"),
                        dcc.Dropdown(
                            id="agency-size-filter",
                            options=[
                                {"label": VOM_CAT, "value": VOM_CAT} #
                                for VOM_CAT in np.sort(data.VOM_CAT.unique())
                            ],
                            value="50-200 peak vehicles",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Transit Agency Name", className="menu-title"),
                        dcc.Dropdown(
                            id="agency-name-filter",
                            options=[
                                {"label": agency_name, "value": agency_name}
                                for agency_name in data.agency_name.unique()
                            ],
                            value="City of Tallahassee",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            # month_format='MMMM Y',
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                            show_outside_days=True,
                            day_size=32,
                            display_format='MM/YYYY'
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="UPT-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="VRM-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@dash_app.callback(
    [Output("UPT-chart", "figure"), Output("VRM-chart", "figure")],
    [
        Input("agency-size-filter", "value"),
        Input("agency-name-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(VOM_CAT, agency_name, start_date, end_date):
    mask = (
        (data.VOM_CAT == VOM_CAT)
        & (data.agency_name == agency_name)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    UPT_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["trips_num"],
                "type": "lines",
                # "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Monthly Unlinked Passenger Trips",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": False},
            "yaxis": {"tickprefix": "", "fixedrange": False},
            "colorway": ["#17B897"],
        },
    }

    VRM_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["VRM"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Monthly Vehicle Revenue Miles", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": False},
            "yaxis": {"fixedrange": False},
            "colorway": ["#E12D39"],
        },
    }
    return UPT_chart_figure, VRM_chart_figure

if __name__ == "__main__":
    dash_app.run_server(debug=True)
