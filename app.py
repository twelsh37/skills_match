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
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
nltk.download("punkt")

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
        # Upload CV area. Takes Word or PDF documents
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
                            # Causes bar to change colour when a file is dragged over it
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
        # Row of three columns. All H4 names. The first column is the CV text area. The second column is the CV word
        # cloud, and the third column is the the radar graph.
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
        # Row of three columns. The first column is the CV text area. The second column is the CV Word cloud, and the
        # third column is the radar graph.
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
        # Row of three columns. All h4 labels. The first column is the job description. The second column is the Job
        # description word cloud, and the third is the percentage match between the CV nd Job description score.
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
        # Row of three columns. The first column is the job description text area. The second column is the Job
        # description word cloud, and the third is the percentage match between the CV nd Job description score.
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
        # copyright bar at bottom of page
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
        text_div = soup.find("div", id="md_skills")  # locate the div by id
        if text_div:
            text = " ".join(
                p.text for p in text_div.find_all("p")
            )  # get the text inside <p> tags within the div
        else:
            text = ""
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


def generate_wordcloud(text):
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="Greens",
        # stopwords=stopwords.words("english"),
        stopwords=stop_words,
        min_font_size=10,
    ).generate(text)
    return wordcloud.to_image()


def generate_wordcloud_jd(text):
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="Blues",  # Choose a different colormap for the JD WordCloud
        stopwords=stop_words,
        min_font_size=10,
    ).generate(text)
    return wordcloud.to_image()


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
    [
        Output("radar-graph", "figure"),
        Output("similarity-score", "children"),
        Output("radar-graph", "style"),
        Output("no-data-message", "style"),
    ],
    [Input("analyze-button", "n_clicks"), Input("threshold-slider", "value")],
    [State("cv-text", "value"), State("job-description", "value")],
)
def update_radar_graph(n_clicks, threshold, cv_text, job_description):
    """Update radar graph and similarity score when the analyze button is clicked."""
    if n_clicks > 0 and cv_text and job_description:
        if "http" in job_description:
            job_description = extract_text_from_url(job_description)
        cv_keywords = extract_keywords(cv_text)
        job_keywords = extract_keywords(job_description)
        common_keywords = cv_keywords & job_keywords
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=[common_keywords[keyword] for keyword in common_keywords],
                theta=list(common_keywords.keys()),
                fill="toself",
                name="CV",
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[job_keywords[keyword] for keyword in common_keywords],
                theta=list(common_keywords.keys()),
                fill="toself",
                name="Job Description",
            )
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            legend=dict(orientation="h"),
        )

        # Function to calculate the match percentage between the CV text and the job description
        def calculate_match_percentage(text, jd):
            vectorizer = CountVectorizer().fit_transform([text, jd])
            vectors = vectorizer.toarray()
            cosine_sim = cosine_similarity(vectors)
            match_percentage = cosine_sim[0, 1] * 100  # Convert to percentage
            return match_percentage

        similarity_score = calculate_match_percentage(cv_text, job_description)
        similarity_score_text = f"{similarity_score:.0f}%"

        # Use the threshold value from the slider to set the color
        similarity_score_color = "green" if similarity_score >= threshold else "red"
        similarity_score_html = html.H4(
            similarity_score_text,
            style={
                "color": similarity_score_color,
                "font-family": "Arial",
                "font-size": "128px",
                "text-align": "center",
            },
        )

        wordcloud_img = generate_wordcloud(job_description)
        img_bytes = BytesIO()
        wordcloud_img.save(img_bytes, format="PNG")

        # If data available, hide no-data-message and show the graph
        return fig, similarity_score_html, {"display": "block"}, {"display": "none"}

    return (
        go.Figure(),
        html.H4(
            "Awaiting Analysis run",
            style={
                "color": "black",
                "font-family": "Arial",
                "font-size": "20px",
                "text-align": "center",
            },
        ),
        {"display": "none"},
        {
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "fontSize": "20px",
            "height": "100%",
        },
    )


@app.callback(
    [Output("analyze-button", "disabled"), Output("clear-button", "disabled")],
    [Input("cv-text", "value"), Input("job-description", "value")],
)
def update_buttons(cv_text, job_description):
    empty_fields = not bool(cv_text and job_description)
    return empty_fields, empty_fields


def handle_analysis_run(n_clicks):
    if n_clicks is None:
        return (
            None,
            {"display": "none"},
            html.Div(
                "Awaiting analysis run",
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "fontSize": "20px",
                    "height": "550px",
                },
            ),
        )
    return None


def handle_extraction(text):
    if text is not None and "http" in text:
        text = extract_text_from_url(text)
    return text


def handle_wordcloud_generation(wordcloud_img):
    img_bytes = BytesIO()
    wordcloud_img.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()
    wordcloud_img_b64 = base64.b64encode(img_bytes).decode()
    src = "data:image/png;base64,{}".format(wordcloud_img_b64)
    return src, {"display": "block"}, ""


@app.callback(
    [
        Output("word-cloud", "src"),
        Output("word-cloud", "style"),
        Output("word-cloud-placeholder", "children"),
    ],
    Input("analyze-button", "n_clicks"),
    State("cv-text", "value"),
)
def update_word_cloud(n_clicks, cv_text):
    run_status = handle_analysis_run(n_clicks)
    if run_status is not None:
        return run_status
    try:
        cv_text = handle_extraction(cv_text)
        if cv_text:
            wordcloud_img = generate_wordcloud(cv_text)
            return handle_wordcloud_generation(wordcloud_img)
    except Exception as e:
        print(f"An error occurred: {e}")
    return handle_analysis_run(None)


@app.callback(
    [
        Output("word-cloud-jd", "src"),
        Output("word-cloud-jd", "style"),
        Output("word-cloud-jd-placeholder", "children"),
    ],
    Input("analyze-button", "n_clicks"),
    State("job-description", "value"),
)
def update_word_cloud_jd(n_clicks, job_description):
    run_status = handle_analysis_run(n_clicks)
    if run_status is not None:
        return run_status
    try:
        job_description = handle_extraction(job_description)
        if job_description:
            wordcloud_img = generate_wordcloud_jd(job_description)
            return handle_wordcloud_generation(wordcloud_img)
    except Exception as e:
        print(f"An error occurred: {e}")
    return handle_analysis_run(None)


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
