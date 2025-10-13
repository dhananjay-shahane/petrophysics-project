import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import spacy
from dash.dependencies import ALL  # ✅ FIXED: Import ALL

# Load NLP model (use `en_core_web_md` for better similarity)
try:
    nlp = spacy.load("en_core_web_md")
except ModuleNotFoundError:
    nlp = None

# Define valid commands
COMMANDS = ["Add well X", "Remove well X", "List wells", "Current project"]

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define colors and styles
BACKGROUND_COLOR = "#121212"
TEXT_COLOR = "#E0E0E0"
ACCENT_COLOR = "#00BFFF"
BORDER_STYLE = "1px solid #444"

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("Command History"),
            html.Div(id="command-history", style={"height": "400px", "overflowY": "auto", "border": BORDER_STYLE, 
                                                  "padding": "10px", "backgroundColor": "#1E1E1E", "color": TEXT_COLOR}),
        ], width=3, style={"borderRight": BORDER_STYLE, "padding": "15px"}),

        dbc.Col([
            html.H2("Well Database Command Interface", style={"color": ACCENT_COLOR, "borderBottom": BORDER_STYLE, "paddingBottom": "10px"}),

            dcc.Textarea(id="command-input", placeholder="Enter command...",
                         style={"width": "100%", "height": 100, "backgroundColor": "#1E1E1E", "color": TEXT_COLOR, "border": BORDER_STYLE}),
            dbc.Button("Execute", id="execute-btn", color="info", className="mt-2"),
            
            html.Hr(style={"borderColor": "#444"}),

            html.H5("Response:", className="text-light"),
            html.Div(id="response-output", style={"whiteSpace": "pre-wrap", "border": BORDER_STYLE, "padding": "10px", 
                                                  "backgroundColor": "#1E1E1E", "color": TEXT_COLOR}),
            
            html.H5("Suggestions:", className="text-light"),
            html.Div(id="suggestions-output", style={"marginTop": "10px"}),

            dcc.Store(id="history-store", data=[]),  # Store previous commands
            dcc.Store(id="selected-suggestion", data=""),  # Track last clicked suggestion
        ], width=9, style={"padding": "15px"}),
    ])
], fluid=True)

# Function to find similar command suggestions
def get_suggestions(command):
    if not nlp:
        return []

    doc = nlp(command.lower())
    best_match = sorted(COMMANDS, key=lambda cmd: nlp(cmd).similarity(doc), reverse=True)
    
    return best_match[:3]  # Return top 3 matches

# Command processing logic
def process_command(command):
    if not command:
        return "Please enter a command.", []

    doc = nlp(command.lower())
    tokens = [token.text for token in doc]

    if "list" in tokens and "wells" in tokens:
        return "Listing all wells in the database.", []
    elif "remove" in tokens and "well" in tokens:
        return "Well removed successfully.", []
    elif "current" in tokens and "project" in tokens:
        return "Current project: Example_Project", []
    else:
        suggestions = get_suggestions(command)
        return "Command not recognized.", suggestions

# Callback to handle command execution
@app.callback(
    [Output("response-output", "children"),
     Output("suggestions-output", "children"),
     Output("history-store", "data"),
     Output("command-history", "children")],
    Input("execute-btn", "n_clicks"),
    State("command-input", "value"),
    State("history-store", "data"),
    prevent_initial_call=True
)
def execute_command(n_clicks, command, history):
    response, suggestions = process_command(command)

    # Update command history
    history.append(command)
    history_display = [html.Div(cmd, style={"borderBottom": "1px solid #444", "padding": "5px", "color": ACCENT_COLOR}) for cmd in history]

    # Display clickable suggestions
    suggestion_links = [
        html.Button(suggestion, id={"type": "suggestion", "index": i}, n_clicks=0,
                    style={"cursor": "pointer", "color": "#FF4500", "border": "none", "background": "none", "textDecoration": "underline"})
        for i, suggestion in enumerate(suggestions)
    ]

    return response, suggestion_links, history, history_display

# Callback to handle suggestion clicks
@app.callback(
    Output("command-input", "value"),
    Input({"type": "suggestion", "index": ALL}, "n_clicks"),
    State({"type": "suggestion", "index": ALL}, "children"),
    State("selected-suggestion", "data"),
    prevent_initial_call=True
)
def suggestion_clicked(n_clicks, children, last_selected):
    if not n_clicks or all(click is None or click == 0 for click in n_clicks):
        return dash.no_update

    # Find the index of the clicked suggestion
    clicked_index = next((i for i, click in enumerate(n_clicks) if click), None)

    if clicked_index is not None and children[clicked_index] != last_selected:
        return children[clicked_index]  # Update the input with the clicked suggestion

    return dash.no_update  # If the same suggestion is clicked again, no update

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
