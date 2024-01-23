###############################################################################
#   This program compares two inputs and returns a similarity score.           #
#    Copyright (C) 2024  Tom Welsh twelsh37@gmail.com                         #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.   #
###############################################################################

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html


app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="skills_warrior"
)
server = app.server

app.layout = dbc.Container(
    fluid=True,
    style={"padding": "30px"},
    children=[
        # Skill Warrior Headline H1
        dbc.Row(
            [
                dbc.Col(
                    html.H1("Skills Warrior"),
                    width=12,
                ),
            ]
        ),  # ROW END
        # Upload CV area. Takes word or PDF documents
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Upload(
                            id="upload-cv",
                            children=html.Div(
                                ["Drag and Drop or ", html.A("Select a CV")]
                            ),
                            className="mt-2 mr-2 mb-2 text-center upload-hover rounded-3",
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "solid",
                                "borderColor": "black",
                                "borderRadius": "5px",
                                "boxShadow": "rgba(0, 0, 0, 0.24) 0px 3px 8px",
                                "backgroundColor": "white",
                            },
                            # causes bar to change colour when a file is dragged over it
                            style_active={
                                "backgroundColor": "rgba(39, 213, 245, 0.12)",
                                "borderColor": "green",
                            },
                            multiple=False,
                        ),
                        width=12,
                    ),
                ]
            ),  # ROW END
        ),
        # Row of two columns. The first column is the CV text area. The second column is the radar graph.
        dbc.Row(
            [
                dbc.Col(
                    html.H4("Your CV", className="m-2"),
                    md=6,
                ),
                dbc.Col(
                    html.H4("CV Word Cloud", className="m-2"),
                    md=3,
                ),
                dbc.Col(
                    html.H4("Skills Overlay", className="m-2"),
                    md=3,
                ),
            ]
        ),  # ROW END
        # Row of two columns. The first column is the CV text area. The second column is the radar graph.
        dbc.Row(
            [
                # CV text area
                dbc.Col(
                    dcc.Textarea(
                        id="cv-text",
                        placeholder="CV text will appear here...",
                        className="bs-100pct p-3 rounded-3 w-100 h-100",
                    ),
                    md=6,
                ),
                # CV Word cloud image
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.Div(
                                    "Awaiting analysis run", id="word-cloud-placeholder"
                                ),
                                html.Img(
                                    id="word-cloud",
                                    className="w-100 h-100 p-2",
                                ),
                            ],
                            className="bs-100pct rounded-3 custom-border",
                        ),
                    ],
                    md=3,
                ),
                # Radar graph
                dbc.Col(
                    dbc.Card(
                        [
                            dcc.Graph(
                                id="radar-graph",
                                className="w-100 h-100",
                                style={"display": "none", "height": "500px"},
                            ),
                            html.Div(
                                id="no-data-message",
                                children=["Awaiting analysis run"],
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                    "fontSize": "20pt",
                                    "height": "100%",
                                },
                            ),
                        ],
                        className="bs-100pct rounded-3 custom-border",
                    ),  # dbc.card closing parenthesis here
                    md=3,
                ),
            ],
            className="h-100",
            # style={"height": "100%"},
        ),  # ROW END
        # Row of two columns. The first column is the job description text area. The second column is the similarity
        # score.
        dbc.Row(
            [
                dbc.Col(html.H4("Job Description", className="m-2 mt-3"), md=6),
                dbc.Col(
                    html.H4("Job Description Word Cloud", className="m-2 mt-3"),
                    md=3,
                ),
                dbc.Col(
                    html.H4(
                        "Percentage Match",
                        className="m-2 mt-3",
                    ),
                    md=3,
                ),
            ]
        ),  # ROW END
        # Row of two columns. The first column is the job description text area. The second column is the similarity
        # score.
        dbc.Row(
            [
                # Job description text area
                dbc.Col(
                    dcc.Textarea(
                        id="job-description",
                        placeholder="Cut and paste job description, or enter Job URL here...",
                        className="bs-100pct p-3 rounded-3 w-100 h-100",
                    ),
                    md=6,
                ),
                # Job Description Word cloud image
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.Div(
                                    "Awaiting analysis run",
                                    id="word-cloud-jd-placeholder",
                                ),
                                html.Img(
                                    id="word-cloud-jd",
                                    className="w-100 h-100 p-2",
                                ),
                            ],
                            className="bs-100pct rounded-3 custom-border",
                        ),
                    ],
                    md=3,
                ),
                # Percentage match
                dbc.Col(
                    [
                        # Insert the new H4 label with padding here
                        dbc.Card(
                            [
                                html.Div(
                                    id="similarity-score",
                                    style={
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "color": "black",
                                        "fontFamily": "Arial",
                                        "fontSize": "calc(23vh + 3vw)",  # 80% of the card's height
                                        "height": "33vh",  # Set the height of the card
                                    },
                                ),
                                # Insert the new H4 label with padding here
                                html.Label(
                                    "Adjust Match Threshold",
                                    style={
                                        "fontSize": "20px",
                                        "textAlign": "left",
                                        "marginLeft": "20px",
                                        "marginBottom": "5px",
                                        "padding": "5px",
                                    },
                                ),
                                # Insert the new slider here
                                dcc.Slider(
                                    id="threshold-slider",
                                    min=0,
                                    max=100,
                                    step=1,
                                    value=51,  # Default threshold value
                                    marks={
                                        i: "{}%".format(i) for i in range(0, 101, 10)
                                    },
                                ),
                            ],
                            className="bs-100pct rounded-3 custom-border",
                        ),
                    ],
                    md=3,
                ),
            ],
            className="h-100",
            # style={"height": "50%"},
        ),  # ROW END
        # Row of two columns. The first column is the analyze button. The second column is the clear button.
        dbc.Row(
            [
                # Analyze and clear buttons
                dbc.Col(
                    children=[
                        # Analyze button
                        dbc.Button(
                            "Analyze",
                            id="analyze-button",
                            color="primary",
                            n_clicks=0,
                            className="me-2",
                            disabled=True,
                            style={
                                "width": "150px",
                                "minWidth": "100px",
                            },
                        ),
                        # Clear button
                        dbc.Button(
                            "Clear",
                            id="clear-button",
                            color="primary",
                            n_clicks=0,
                            className="me-2",
                            disabled=True,
                            style={
                                "width": "150px",
                                "minWidth": "100px",
                            },
                        ),
                    ],
                    width=3,
                    style={
                        "padding": "20px",
                    },
                    className="d-flex align-items-start",
                )
            ],
            # style={"marginBottom": "80px"},
            className="g-0",
        ),  # ROW END
        dbc.Row(
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Img(
                                src="/assets/aiaa-circle.png",
                                style={
                                    "position": "absolute",
                                    "top": "10px",
                                    "left": "20px",
                                    "width": "50px",
                                    "height": "50px",
                                    "zIndex": "1",
                                },
                            ),
                            html.P(
                                "Copyright © 2024 The AIAA Consultants Ltd",
                                style={
                                    "textAlign": "center",
                                    "color": "#B98600",
                                    "padding": "20px",
                                    "fontSize": "20px",
                                    "backgroundColor": "#364A9F",
                                    "borderColor": "#111111",
                                    "width": "100%",
                                    "position": "relative",
                                },
                            ),
                        ],
                        style={"position": "relative"},
                    ),
                ]
            )
        ),
    ],
)
