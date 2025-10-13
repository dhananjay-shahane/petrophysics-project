import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from dash_split_pane import DashSplitPane
import spacy
from tabulate import tabulate
from Project_Manager import *
from email_script import *


object_store = {}
initial_suggestions = [
    "Add well WellA",
    "List all wells",
    "Show logs for WellA",
    "Set depth range 1000-2000",
    "Display zones for WellB",
    "Export data to CSV"
]

def store_object(name, obj):
    """Stores an object with a given name."""
    object_store[name] = obj

def get_object(name):
    """Retrieves an object by name."""
    return object_store.get(name, None)
# ✅ Initial Variables for Right Sidebar
initial_sidebar_values = {
"Well Name": "Well-A1",
"Depth Range": "1000m - 3000m",
"Formation": "Sandstone",
"Operator": "XYZ Corp"
}
def initialize():
    """Runs once at the start of the app."""
    print("Initializing objects...")

    pm = ProjectManager()
    current_project = pm.get_project_path()
    print(current_project)
    db = DatabaseQuery()
    db.Load_Wells()
    wells = db.wells
    store_object("wells",wells)
    
    
# Load NLP model
nlp = spacy.load("en_core_web_md")  # Use 'md' for better similarity checking

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Colors and Styles
BACKGROUND_COLOR = "#121212"
TEXT_COLOR = "#E0E0E0"
ACCENT_COLOR = "#00BFFF"
BORDER_STYLE = "1px solid #444"

# Available Commands
COMMANDS = ["add well", "remove well", "list wells", "current project"]

# Define layout with resizable sidebar
# Layout
app.layout = dbc.Container([
    dcc.Store(id="history-store", data=[]),  # Store command history
    dcc.Store(id="sidebar-store", data=initial_sidebar_values),
    dcc.Store(id="suggestions-store", data=initial_suggestions),
    # Outer SplitPane: Left Sidebar & Main + Right Sidebar
    DashSplitPane(
        id="outer-split-pane",
        split="vertical",
        size="20%",  # Initial Left Sidebar Size
        children=[
            # ✅ Left Sidebar
            html.Div([
                html.H4("Command History"),
                html.Div(id="command-history", style={
                    "height": "100vh",
                    "overflowY": "auto",
                    "padding": "10px",
                    "backgroundColor": "#1E1E1E",
                    "color": "#E0E0E0",
                    "minWidth": "200px"
                }),
            ], style={"display": "flex", "flexDirection": "column", "width": "100%"}),

            # ✅ Inner SplitPane: Main Content & Right Sidebar
            DashSplitPane(
                id="inner-split-pane",
                split="vertical",
                size="80%",  # Initial Main Content Size
                children=[
                    # ✅ Main Content
                    html.Div([
                        html.H2("Well Database Command Interface"),
                        dcc.Textarea(id="command-input", placeholder="Enter command...",
                                     style={"width": "100%", "height": 100}),
                        dbc.Button("Execute", id="execute-btn", color="info", className="mt-2"),
                        html.Hr(),
                        html.H5("Response:"),
                        html.Div(id="response-output",
                                 style={"whiteSpace": "pre-wrap", "border": "1px solid #444", "padding": "10px"}),

                        # ✅ Suggestion Output
                        html.Div(id="suggestion-output", style={"marginTop": "10px", "color": "#FFA500"}),
                    ], style={"flex": 1, "padding": "20px"}),

                    # ✅ Right Sidebar
                    html.Div([
                        html.H4("Status"),
                        html.Div(id="status", style={
                            "height": "100vh",
                            "overflowY": "auto",
                            "padding": "10px",
                            "backgroundColor": "#ADD8E6",
                            "color": "#E0E0E0",
                            "minWidth": "200px"
                        }),
                    ], style={"display": "flex", "flexDirection": "column", "width": "100%"}),
                ],
            )
        ],
    )
], fluid=True)
# NLP Command Processing

def parse_doc(doc):
    lines = doc.text.strip().split("\n")  # Split text into lines
    
    if not lines:
        return None, {}

    command = lines[0].strip()  # First line as command
    variables = {}

    for line in lines[1:]:  # Process remaining lines for variables
        if ":" in line:
            key, value = map(str.strip, line.split(":", 1))  # Split at first ':'
            variables[key] = value

    return command, variables

def process_command(command):
    """Process the command using NLP and provide suggestions if not recognized."""
    
    doc = nlp(command.lower())
    command, variables = parse_doc(doc)
    
    # Recognized Commands
    if "list" in command and "wells" in command:
        # db = DatabaseQuery()
        # db.Load_Wells()
        # wells = db.wells
        wells = get_object("wells")
        well_names = ", ".join(well.well_name for well in wells)
        # attributes = ["well_name"]
        # Convert objects to list of lists
        data = [[well.well_name] for well in wells]
        # Generate table
        # Example data
        headers = ["Well", "Location", "Depth"]
        table = tabulate(data, headers=headers, tablefmt="grid")
        return table, []
    # Recognized Commands
    if "list" in command and "datasets" in command:
        wells = get_object("wells")
        well_names = ", ".join(well.well_name for well in wells)
        # attributes = ["well_name"]
        # Convert objects to list of lists
        data = [[well.well_name] for well in wells]
        # Generate table
        # Example data
        headers = ["Well", "Location", "Depth"]
        table = tabulate(data, headers=headers, tablefmt="grid")
        return table, []
    elif "remove" in command and "well" in command:
        return "Well removed successfully.", []
    elif "current" in command and "project" in command:
        pm = ProjectManager()
        current_project = pm.get_project_path()
        print(current_project)
        return "Current project: " + str(current_project), []
    elif "set" in doc.text and "project" in command:
        
        pm = ProjectManager()
        print(variables)
        if "project" in variables:
            current_project = pm.open_project_path("C:/Petrocene_Projects/"+ variables["project"])
            print(current_project)
            db = DatabaseQuery()
            db.Load_Wells()
            wells = db.wells
            store_object("wells",wells)
            return "Project set: "+ current_project, []
        else:
            return "Provide project to set"
    elif "set" in doc.text and "well" in command:           # Set current well
        print(variables)
        # Save selected items from list2 to settings
        sel_well_names = variables["well"]
        selected_wells = [variables["well"].upper()]
        settings = QSettings('Petrocene','PetroceneApp')
        settings.setValue('selected_wells', json.dumps(selected_wells))
        print("Selected items saved!",selected_wells)
        
    elif "get" in doc.text and "well" in command:           # Set current well
        print(variables)
        db=DatabaseQuery()
        settings = QSettings('Petrocene','PetroceneApp')
        selected_wells = settings.value("selected_wells", None)
        selected_well_names = json.loads(settings.value('selected_wells', '[]')) # Need to fix this error after aa well file is deleted
        print(selected_well_names)
        
    elif "create" in doc.text and "project" in command:
        pm = ProjectManager()
        print(variables)
        if "project" in variables:
            current_project = pm.create_project("C:/Petrocene_Projects",variables["project"])
            print(current_project)
            db = DatabaseQuery()
            db.Load_Wells()
            wells = db.wells
            store_object("wells",wells)
            return "Created New Project set: "+ current_project, []
        else:
            return "Project not created"
    elif "import" in command and "las file" in command:
        pm = ProjectManager()
        print(variables)
        if "las" in variables:
            las_file_path = variables["las"]
            print("LAS FILE PATH: " + las_file_path)
            
            db = DatabaseQuery()
            impex= DataIMPEX()
            impex.import_Single_LAS_File(las_file_path)
            db.Load_Wells()
            wells = db.wells
            store_object("wells",wells)
            return "imported las file: "+ las_file_path, []
        else:
            return "Project not created"
    elif "current" in command and "project" in command:
        pm = ProjectManager()
        current_project = pm.get_project_path()
        print(current_project)
        return "Current project: " + str(current_project), []
    
    # If command not found, suggest closest match
    suggestions = [cmd for cmd in COMMANDS if nlp(cmd).similarity(doc) > 0.6]

    if suggestions:
        return "Command not recognized.", suggestions
    else:
        return "Command not recognized. Try 'Add well X', 'Remove well X', or 'List wells'.", []


# Unified Callback for Execution and Suggestion Clicks
@app.callback(
    [
        Output("response-output", "children"),
        Output("suggestion-output", "children"),
        Output("history-store", "data"),
        Output("command-history", "children"),
        Output("command-input", "value"),
        Output("status", "children")  # ✅ Added status output
    ],
    [
        Input("execute-btn", "n_clicks"),
        Input({"type": "suggestion", "index": dash.ALL}, "n_clicks")
    ],
    [
        State("command-input", "value"),
        State("history-store", "data"),
        State({"type": "suggestion", "index": dash.ALL}, "children"),
        State("sidebar-store", "data")  # ✅ Added sidebar data state
    ],
    prevent_initial_call=True
)
def handle_command(execute_click, suggestion_clicks, command, history, suggestions, sidebar_data):
    trigger = ctx.triggered_id  # ✅ Identify what triggered the function

    status_content = "Ready"  # Default status

    # ✅ Display clickable suggestions
    suggestion_links = [
        html.Button(
            suggestion,
            id={"type": "suggestion", "index": i},
            n_clicks=0,
            style={
                "cursor": "pointer",
                "color": "#FF4500",
                "border": "none",
                "background": "none",
                "textDecoration": "underline",
                "marginRight": "10px"
            }
        )
        for i, suggestion in enumerate(suggestions)
    ]
    
    if trigger == "execute-btn":
        # ✅ Execute the entered command
        response = process_command(command)
        updated_history = history + [command] if history else [command]
        command_history_display = [html.Li(cmd) for cmd in updated_history]

        # ✅ Update status with sidebar data (if available)
        if sidebar_data:
            status_content = html.Ul([html.Li(f"{key}: {value}") for key, value in sidebar_data.items()])
        else:
            status_content = "No sidebar data available"
        # Display clickable suggestions
        suggestion_links = [
        html.Button(suggestion, id={"type": "suggestion", "index": i}, n_clicks=0,
                    style={"cursor": "pointer", "color": "#FF4500", "border": "none", "background": "none", "textDecoration": "underline"})
        for i, suggestion in enumerate(suggestions)
        ]
        # print(suggestion_links)
        return response, suggestion_links, updated_history, command_history_display, "", status_content
        
 
    elif isinstance(trigger, dict) and trigger.get("type") == "suggestion":
        index = trigger["index"]
        suggestion_text = suggestions[index] if index < len(suggestions) else "Invalid Suggestion"
        response = f"Using Suggestion: {suggestion_text}"

        return response, suggestion_links, history, dash.no_update, "", status_content

    # ✅ Ensure function always returns exactly 6 values
    return "Awaiting input...", "", history, dash.no_update, "", status_content

def generate_html_table(headers, data):
    table_html = "<table border='1'><tr>"
    table_html += "".join(f"<th>{col}</th>" for col in headers) + "</tr>"

    for row in data:
        table_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

    table_html += "</table>"
    return table_html

def update_sidebar(data):
    # Create a formatted list of variable values for the right sidebar
    if not data:  # Handles case where data is missing
        return "No data available"
    return html.Ul([html.Li(f"{key}: {value}") for key, value in data.items()])
# Initialize objects before running the Dash app
initialize()
if __name__ == "__main__":
    app.run_server(debug=True)
