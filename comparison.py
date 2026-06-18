from __future__ import annotations

import os
import dash
from dash import html, dcc, Input, Output
from ase.io import read as ase_read
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.analysis.graphs import StructureGraph

import crystal_toolkit.components as ctc
from crystal_toolkit.settings import SETTINGS

app = dash.Dash(assets_folder=SETTINGS.ASSETS_PATH)

# 1. Define your folder paths pointing directly to the pw_scf.in files
STRUCTURE_PATHS = {
    "Disp 1.00 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.00/final_geo/pw_scf.in",
    "Disp 1.20 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.20/final_geo/pw_scf.in",
}


# 2. Parse using ASE and convert to Pymatgen structures in memory
loaded_structures = {}
for name, path in STRUCTURE_PATHS.items():
    if os.path.exists(path):
        ase_atoms = ase_read(path, format="espresso-in")
        loaded_structures[name] = AseAtomsAdaptor.get_structure(ase_atoms)
    else:
        print(f"Warning: Path not found {path}. Generating fallback dummy structure.")
        from pymatgen.core import Lattice
        loaded_structures[name] = Structure(Lattice.cubic(4.0), ["Li", "F"], [[0,0,0], [0.5,0.5,0.5]])

init_struct = list(loaded_structures.values())[0]
init_graph = StructureGraph.from_empty_graph(init_struct)

# 3. Instantiate the view panels for Structure Row 1 and Row 2
custom_scene_settings_x = {"showBonds": False, "showPolyhedra": False, "cameraAxis": "x"}
custom_scene_settings_y = {"showBonds": False, "showPolyhedra": False, "cameraAxis": "y"}
custom_scene_settings_z = {"showBonds": False, "showPolyhedra": False, "cameraAxis": "z"}

comp_1x = ctc.StructureMoleculeComponent(init_graph, id="struct_1x", scene_settings=custom_scene_settings_x)
comp_1y = ctc.StructureMoleculeComponent(init_graph, id="struct_1y", scene_settings=custom_scene_settings_y)
comp_1z = ctc.StructureMoleculeComponent(init_graph, id="struct_1z", scene_settings=custom_scene_settings_z)

comp_2x = ctc.StructureMoleculeComponent(init_graph, id="struct_2x", scene_settings=custom_scene_settings_x)
comp_2y = ctc.StructureMoleculeComponent(init_graph, id="struct_2y", scene_settings=custom_scene_settings_y)
comp_2z = ctc.StructureMoleculeComponent(init_graph, id="struct_2z", scene_settings=custom_scene_settings_z)


# 5. Row UI Builder Helper
def make_structure_row(row_title, comp_x, comp_y, comp_z):
    return html.Div([
        html.H2(row_title, id=f"{comp_x.id()}_title", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div([
            html.Div([
                html.H4("X Orientation", id=f"{comp_x.id()}_x_title", style={"textAlign": "center"}),
                comp_x.layout()
            ], id=f"{comp_x.id()}_x_col", style={"flex": "1", "padding": "10px"}),
            html.Div([
                html.H4("Y Orientation", style={"textAlign": "center"}),
                comp_y.layout()
            ], id=f"{comp_x.id()}_y_col", style={"flex": "1", "padding": "10px"}),
            html.Div([
                html.H4("Z Orientation", style={"textAlign": "center"}),
                comp_z.layout()
            ], id=f"{comp_x.id()}_z_col", style={"flex": "1", "padding": "10px"}),
        ], style={"display": "flex", "flexDirection": "row", "width": "90vw"})
    ], id=f"{comp_x.id()}_row_container", style={"display": "none"})


# 6. Build App Layout Context Wrapper
layout = html.Div(
    [
        html.H1("Multi-Structure Orientation Comparison Toolkit", style={"fontFamily": "sans-serif"}),

        html.Div([
            html.Label("Select exactly two structures to compare:", style={"fontWeight": "bold", "marginBottom": "5px"}),
            dcc.Checklist(
                id="structure-selector",
                options=[{"label": name, "value": name} for name in loaded_structures.keys()],
                value=list(loaded_structures.keys())[:2],
                labelStyle={"display": "block", "margin": "5px"}
            ),
            html.Label("Orientation options:", style={"fontWeight": "bold", "marginTop": "15px", "marginBottom": "5px", "display": "block"}),
            dcc.Checklist(
                id="compare-orientations-checkbox",
                options=[{"label": "Compare three orientations (X, Y, Z)", "value": "compare"}],
                value=["compare"],
                labelStyle={"display": "block", "margin": "5px"}
            ),
            html.Div(id="warning-message", style={"color": "red", "fontWeight": "bold", "marginTop": "5px"})
        ], style={"padding": "20px", "border": "1px solid #ccc", "borderRadius": "5px", "marginBottom": "20px"}),

        make_structure_row("Structure 1", comp_1x, comp_1y, comp_1z),
        make_structure_row("Structure 2", comp_2x, comp_2y, comp_2z),
    ],
    style={"margin": "2em auto", "display": "flex", "flexDirection": "column", "alignItems": "center", "fontFamily": "sans-serif"},
)

ctc.register_crystal_toolkit(app, layout=layout)


# 7. Dynamic multi-state view update callback
@app.callback(
    Output("warning-message", "children"),
    Output(f"{comp_1x.id()}_row_container", "style"),
    Output(f"{comp_1x.id()}_title", "children"),
    Output(comp_1x.id(), "data"),
    Output(comp_1y.id(), "data"),
    Output(comp_1z.id(), "data"),
    Output(f"{comp_2x.id()}_row_container", "style"),
    Output(f"{comp_2x.id()}_title", "children"),
    Output(comp_2x.id(), "data"),
    Output(comp_2y.id(), "data"),
    Output(comp_2z.id(), "data"),
    Input("structure-selector", "value")
)
def update_displayed_structures(selected_names):
    hidden_style = {"display": "none"}
    visible_style = {"display": "block"}

    if not selected_names or len(selected_names) != 2:
        return "Please select exactly 2 structures.", hidden_style, "", dash.no_update, dash.no_update, dash.no_update, hidden_style, "", dash.no_update, dash.no_update, dash.no_update

    name1, name2 = selected_names[0], selected_names[1]
    struct1, struct2 = loaded_structures[name1], loaded_structures[name2]

    g1 = StructureGraph.from_empty_graph(struct1)
    g2 = StructureGraph.from_empty_graph(struct2)

    return (
        "",
        visible_style, f"Comparison Target: {name1}", g1, g1, g1,
        visible_style, f"Comparison Target: {name2}", g2, g2, g2
    )


@app.callback(
    Output(f"{comp_1x.id()}_y_col", "style"),
    Output(f"{comp_1x.id()}_z_col", "style"),
    Output(f"{comp_1x.id()}_x_title", "children"),
    Output(f"{comp_2x.id()}_y_col", "style"),
    Output(f"{comp_2x.id()}_z_col", "style"),
    Output(f"{comp_2x.id()}_x_title", "children"),
    Input("compare-orientations-checkbox", "value")
)
def toggle_orientations(checkbox_value):
    if checkbox_value and "compare" in checkbox_value:
        show_col = {"flex": "1", "padding": "10px"}
        return show_col, show_col, "X Orientation", show_col, show_col, "X Orientation"
    else:
        hide_col = {"display": "none"}
        return hide_col, hide_col, "Interactive View", hide_col, hide_col, "Interactive View"


if __name__ == "__main__":
    app.run(debug=True, port=8050)