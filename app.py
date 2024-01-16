import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import docx2txt
import PyPDF2
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import Counter
import base64


nltk.download("stopwords")
nltk.download("punkt")

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="skills_warrior"
)

app.layout = dbc.Container(
    fluid=True,
    style={"margin": "5px 10px"},
    children=[
        dbc.Row(
            [
                dbc.Col(html.H1("Skills Warrior"), width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Upload(
                        id="upload-cv",
                        children=html.Div(["Drag and Drop or ", html.A("Select a CV")]),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderColor": "blue",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px 10px 10px 0",
                        },
                        multiple=False,
                    ),
                    width=9,
                ),
            ]
        ),
        dbc.Row([
            dbc.Col(html.H4("Your CV"), md=9),
            dbc.Col(html.H4('Matching Skills'), md=3)
        ]),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Textarea(
                        id="cv-text",
                        placeholder="CV text will appear here...",
                        style={"width": "100%", "height": "35vh"},
                    ),
                    md=9,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dcc.Graph(id="radar-graph"),

                        ],
                        style={"height": "35vh"}
                    ),
                    md=3,
                ),
            ]
        ),
        dbc.Row([
            dbc.Col(html.H4("Job Description"), md=9),
            dbc.Col(html.H4('Similarity Score'), md=3)
        ]),

        dbc.Row(
            [
                dbc.Col(
                    dcc.Textarea(
                        id="job-description",
                        placeholder="Enter job description URL or text here...",
                        style={"width": "100%", "height": "100%"},
                    ),
                    md=9,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.Div(
                                id='similarity-score',
                                style={
                                    'height': '100%',
                                    'display': 'flex',
                                    'justifyContent': 'center',
                                    'alignItems': 'center',
                                    'color': 'black',
                                    'fontFamily': 'Arial',
                                    'fontSize': '128px'
                                }
                            ),
                            html.Label('Adjust threshold',
                                       style={'fontSize': '20px',
                                              'textAlign': 'left',
                                              'marginLeft': '20px',
                                              'marginBottom': '5px'
                                              }
                                       ),
                            dcc.Slider(
                                id='threshold-slider',
                                min=0,
                                max=100,
                                step=1,
                                value=60,  # Default threshold value
                                marks={i: '{}%'.format(i) for i in range(0, 101, 10)},
                            )
                        ],
                        style={"height": "100%"},
                    ),
                    md=3,
                ),
            ],
            style={"display": "flex", "align-items": "stretch"},
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Analyze",
                        id="analyze-button",
                        color="primary",
                        n_clicks=0,
                        className="mt-2",
                    ),
                    width=3,
                    style={"max-width": "200px"},
                )
            ]
        ),
    ],
)


def extract_text_from_cv(contents, filename):
    """
    Extract text from CV in Word or PDF format.
    """
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "doc" in filename:
            text = docx2txt.process(BytesIO(decoded))
        elif "pdf" in filename:
            reader = PyPDF2.PdfReader(BytesIO(decoded))
            text = " ".join(
                [reader.pages[i].extract_text() for i in range(len(reader.pages))]
            )
        else:
            raise Exception("Invalid file type")
    except Exception as e:
        print(e)
        return ""
    return text


def extract_text_from_url(url):
    """
    Extract text from job description URL.
    """
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        text = " ".join([p.text for p in soup.find_all("p")])
    except Exception as e:
        print(e)
        return ""
    return text


def extract_keywords(text):
    """
    Extract keywords from text.
    """
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha()]
    words = [word for word in words if word not in stopwords.words("english")]
    return Counter(words)


@app.callback(
    Output("cv-text", "value"),
    Input("upload-cv", "contents"),
    State("upload-cv", "filename"),
)
def update_cv_text(contents, filename):
    """
    Update CV text when a file is uploaded.
    """
    if contents:
        text = extract_text_from_cv(contents, filename)
        return text
    return ""


@app.callback(
    [Output('radar-graph', 'figure'), Output('similarity-score', 'children')],
    [Input('analyze-button', 'n_clicks'), Input('threshold-slider', 'value')],
    [State('cv-text', 'value'), State('job-description', 'value')]
)
def update_radar_graph(n_clicks, threshold, cv_text, job_description):
    """
    Update radar graph and similarity score when the analyze button is clicked.
    """
    if n_clicks > 0 and cv_text and job_description:
        if 'http' in job_description:
            job_description = extract_text_from_url(job_description)
        cv_keywords = extract_keywords(cv_text)
        job_keywords = extract_keywords(job_description)
        common_keywords = cv_keywords & job_keywords
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[common_keywords[keyword] for keyword in common_keywords],
            theta=list(common_keywords.keys()),
            fill='toself',
            name='CV'
        ))
        fig.add_trace(go.Scatterpolar(
            r=[job_keywords[keyword] for keyword in common_keywords],
            theta=list(common_keywords.keys()),
            fill='toself',
            name='Job Description'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            showlegend=True
        )
        similarity_score = len(common_keywords) / len(job_keywords) * 100
        similarity_score_text = f"{similarity_score:.2f}%"
        # similarity_score_color = 'green' if similarity_score >= 60 else 'red'
        # similarity_score_html = html.H4(similarity_score_text, style={'color': similarity_score_color, 'font-family': 'Arial', 'font-size': '128px', 'text-align': 'center'})
        # return fig, similarity_score_html
        # Use the threshold value from the slider to set the color
        similarity_score_color = 'green' if similarity_score >= threshold else 'red'
        similarity_score_html = html.H4(similarity_score_text,
                                        style={'color': similarity_score_color, 'font-family': 'Arial',
                                               'font-size': '128px', 'text-align': 'center'})

        return fig, similarity_score_html

    return go.Figure(), html.H4("0%", style={'color': 'red', 'font-family': 'Arial', 'font-size': '128px', 'text-align': 'center'})


if __name__ == "__main__":
    app.run_server(debug=True)
