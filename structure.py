from __future__ import annotations

import base64
import os
import tempfile
import dash
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from ase.io import read as ase_read
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Structure

import crystal_toolkit.components as ctc
from crystal_toolkit.settings import SETTINGS

# 1. Initialize the Dash app with custom styles and fonts
app = dash.Dash(
    assets_folder=SETTINGS.ASSETS_PATH,
    external_stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.4/css/bulma.min.css",
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap"
    ]
)

# 2. Define default Quantum Espresso input file path
DEFAULT_FILE = "pw_scf.in"

# 3. Robust parser logic for Quantum Espresso and other file formats
def load_structure(filepath: str) -> Structure:
    try:
        # First try parsing as Quantum Espresso input using ASE
        atoms = ase_read(filepath, format="espresso-in")
        return AseAtomsAdaptor.get_structure(atoms)
    except Exception as ase_err:
        # Fallback to standard pymatgen parser
        try:
            return Structure.from_file(filepath)
        except Exception as pm_err:
            raise ValueError(
                f"Failed to parse structure file.\n"
                f"Quantum Espresso parser error: {ase_err}\n"
                f"Pymatgen parser error: {pm_err}"
            )

# Load initial structure
if os.path.exists(DEFAULT_FILE):
    try:
        initial_structure = load_structure(DEFAULT_FILE)
    except Exception as e:
        print(f"Warning: Could not load {DEFAULT_FILE}: {e}")
        initial_structure = Structure(
            [[4.2, 0, 0], [0, 4.2, 0], [0, 0, 4.2]],
            ["Na", "K"],
            [[0, 0, 0], [0.5, 0.5, 0.5]]
        )
else:
    initial_structure = Structure(
        [[4.2, 0, 0], [0, 4.2, 0], [0, 0, 4.2]],
        ["Na", "K"],
        [[0, 0, 0], [0.5, 0.5, 0.5]]
    )

# 4. Create the Crystal Toolkit Structure component
structure_component = ctc.StructureMoleculeComponent(initial_structure, id="my_structure")

# 5. Metadata display generator helper
def get_metadata_panel(struct: Structure) -> html.Div:
    if not struct:
        return html.Div("No structure loaded.", style={"color": "#aaaaaa"})

    try:
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
        sga = SpacegroupAnalyzer(struct)
        spg_symbol = sga.get_space_group_symbol()
        spg_num = sga.get_space_group_number()
        spg_text = f"{spg_symbol} (No. {spg_num})"
    except Exception as e:
        spg_text = f"Unavailable (symmetry extraction failed: {e})"

    formula = struct.composition.reduced_formula
    num_sites = len(struct)
    volume = struct.lattice.volume

    a, b, c = struct.lattice.abc
    alpha, beta, gamma = struct.lattice.angles

    return html.Div([
        html.Div([
            html.Span("Chemical Formula: ", style={"fontWeight": "600", "color": "#888888"}),
            html.Span(formula, style={"fontSize": "1.35rem", "fontWeight": "800", "color": "#00d2ff"})
        ], style={"marginBottom": "15px", "borderBottom": "1px solid rgba(255,255,255,0.1)", "paddingBottom": "10px"}),

        html.Div([
            html.Span("Space Group: ", style={"fontWeight": "600", "color": "#888888"}),
            html.Span(spg_text, style={"fontWeight": "600", "color": "#00e676"})
        ], style={"marginBottom": "15px"}),

        html.Div([
            html.Span("Unit Cell Volume: ", style={"fontWeight": "600", "color": "#888888"}),
            html.Span(f"{volume:.3f} Å³", style={"color": "#ffffff", "fontWeight": "600"})
        ], style={"marginBottom": "15px"}),

        html.Div([
            html.Span("Number of Sites: ", style={"fontWeight": "600", "color": "#888888"}),
            html.Span(str(num_sites), style={"color": "#ffffff", "fontWeight": "600"})
        ], style={"marginBottom": "20px"}),

        html.Div([
            html.Div("Lattice Parameters", style={"fontWeight": "600", "color": "#888888", "marginBottom": "8px", "borderBottom": "1px solid rgba(255,255,255,0.1)", "paddingBottom": "5px"}),
            html.Table([
                html.Tr([
                    html.Td("a =", style={"color": "#aaaaaa", "paddingRight": "5px"}),
                    html.Td(f"{a:.4f} Å", style={"color": "#ffffff", "fontWeight": "600"}),
                    html.Td("α =", style={"color": "#aaaaaa", "padding": "0 5px 0 15px"}),
                    html.Td(f"{alpha:.2f}°", style={"color": "#ffffff"})
                ]),
                html.Tr([
                    html.Td("b =", style={"color": "#aaaaaa", "paddingRight": "5px"}),
                    html.Td(f"{b:.4f} Å", style={"color": "#ffffff", "fontWeight": "600"}),
                    html.Td("β =", style={"color": "#aaaaaa", "padding": "0 5px 0 15px"}),
                    html.Td(f"{beta:.2f}°", style={"color": "#ffffff"})
                ]),
                html.Tr([
                    html.Td("c =", style={"color": "#aaaaaa", "paddingRight": "5px"}),
                    html.Td(f"{c:.4f} Å", style={"color": "#ffffff", "fontWeight": "600"}),
                    html.Td("γ =", style={"color": "#aaaaaa", "padding": "0 5px 0 15px"}),
                    html.Td(f"{gamma:.2f}°", style={"color": "#ffffff"})
                ])
            ], style={"width": "100%", "fontSize": "0.95rem"})
        ])
    ])

# 6. Build the Application Layout
layout = html.Div(
    [
        # Left Sidebar (Controls & Metadata)
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Twente Visualizer", className="title is-3", style={"color": "#00d2ff", "fontFamily": "'Outfit', sans-serif", "fontWeight": "800", "marginBottom": "10px"}),
                        html.P("Crystal Structure Visualizer", style={"color": "#aaaaaa", "fontSize": "0.95rem", "fontWeight": "600", "marginTop": "0px"})
                    ],
                    style={"marginBottom": "25px", "borderBottom": "1px solid rgba(255,255,255,0.1)", "paddingBottom": "15px"}
                ),

                # File Upload Box
                html.Div(
                    [
                        html.H3("Upload Structure File", className="title is-6", style={"color": "#ffffff", "marginBottom": "10px"}),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                [
                                    html.Span("📁 Drag & Drop or Click to Upload", style={"fontSize": "0.9rem", "fontWeight": "600"})
                                ],
                                style={
                                    "border": "2px dashed rgba(0, 210, 255, 0.3)",
                                    "borderRadius": "8px",
                                    "padding": "20px 10px",
                                    "textAlign": "center",
                                    "cursor": "pointer",
                                    "color": "#00d2ff",
                                    "backgroundColor": "rgba(0, 210, 255, 0.05)",
                                    "transition": "all 0.3s ease"
                                }
                            ),
                            multiple=False
                        ),
                        html.Div(id="file-name-display", children=f"Active File: {DEFAULT_FILE}", style={"fontSize": "0.85rem", "color": "#00e676", "marginTop": "8px", "fontWeight": "600"}),
                        html.Div(id="error-message")
                    ],
                    className="box",
                    style={"backgroundColor": "rgba(22, 27, 34, 0.7)", "border": "1px solid rgba(255, 255, 255, 0.1)", "boxShadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)", "marginBottom": "20px"}
                ),

                # Structure Metadata Card
                html.Div(
                    [
                        html.H3("Structure Properties", className="title is-6", style={"color": "#ffffff", "marginBottom": "15px"}),
                        html.Div(id="metadata-container", children=get_metadata_panel(initial_structure))
                    ],
                    className="box",
                    style={"backgroundColor": "rgba(22, 27, 34, 0.7)", "border": "1px solid rgba(255, 255, 255, 0.1)", "boxShadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)", "flex": "1"}
                ),
            ],
            style={
                "width": "360px",
                "padding": "30px 20px",
                "backgroundColor": "#0d1117",
                "borderRight": "1px solid rgba(255, 255, 255, 0.1)",
                "display": "flex",
                "flexDirection": "column",
                "height": "100vh",
                "overflowY": "auto"
            }
        ),

        # Right Main Panel (Crystal Toolkit Visualizer)
        html.Div(
            [
                html.Div(
                    [
                        structure_component.layout()
                    ],
                    style={
                        "backgroundColor": "#161b22",
                        "borderRadius": "12px",
                        "padding": "20px",
                        "border": "1px solid rgba(255, 255, 255, 0.1)",
                        "height": "calc(100vh - 60px)",
                        "boxShadow": "inset 0 0 20px rgba(0,0,0,0.6)",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center"
                    }
                )
            ],
            style={
                "flex": "1",
                "padding": "30px",
                "backgroundColor": "#0d1117",
                "height": "100vh",
                "display": "flex",
                "flexDirection": "column"
            }
        )
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        "minHeight": "100vh",
        "backgroundColor": "#0d1117",
        "fontFamily": "'Outfit', sans-serif"
    }
)

# Register the Crystal Toolkit layout
ctc.register_crystal_toolkit(app, layout=layout)

# 7. Dash Callback for interactive file upload and visualization updates
@app.callback(
    [
        Output(structure_component.id(), "data"),
        Output("error-message", "children"),
        Output("metadata-container", "children"),
        Output("file-name-display", "children")
    ],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True
)
def handle_upload(contents: str | None, filename: str | None):
    if not contents or not filename:
        raise PreventUpdate

    try:
        # Decode base64 contents
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        # Write to temporary file to allow pymatgen/ase file parsers to read it
        with tempfile.NamedTemporaryFile(suffix="_" + filename, delete=False) as tmp:
            tmp.write(decoded)
            tmp.flush()
            tmp_name = tmp.name

        try:
            struct = load_structure(tmp_name)
            if not isinstance(struct, Structure):
                raise ValueError("Parsed file did not resolve to a valid pymatgen Structure object.")

            return struct, "", get_metadata_panel(struct), f"Active File: {filename}"
        finally:
            try:
                os.remove(tmp_name)
            except OSError:
                pass

    except Exception as e:
        error_msg = html.Div(
            f"Error parsing file: {e}",
            className="notification is-danger is-light",
            style={"marginTop": "10px", "padding": "10px", "fontSize": "0.85rem"}
        )
        return dash.no_update, error_msg, dash.no_update, dash.no_update

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8060))
    app.run(debug=False, port=port)
