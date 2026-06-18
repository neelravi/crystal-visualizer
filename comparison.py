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
    "Disp 0.00 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.00/final_geo/pw_scf.in",
    "Disp 0.02 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.02/final_geo/pw_scf.in",
    "Disp 0.04 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.04/final_geo/pw_scf.in",
    "Disp 0.06 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.06/final_geo/pw_scf.in",
    "Disp 0.08 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.08/final_geo/pw_scf.in",
    "Disp 0.10 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.10/final_geo/pw_scf.in",
    "Disp 0.12 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.12/final_geo/pw_scf.in",
    "Disp 0.14 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.14/final_geo/pw_scf.in",
    "Disp 0.16 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.16/final_geo/pw_scf.in",
    "Disp 0.18 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.18/final_geo/pw_scf.in",
    "Disp 0.20 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.20/final_geo/pw_scf.in",
    "Disp 0.30 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.30/final_geo/pw_scf.in",
    "Disp 0.40 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.40/final_geo/pw_scf.in",
    "Disp 0.50 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.50/final_geo/pw_scf.in",
    "Disp 0.60 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.60/final_geo/pw_scf.in",
    "Disp 0.70 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.70/final_geo/pw_scf.in",
    "Disp 0.80 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.80/final_geo/pw_scf.in",
    "Disp 0.90 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_0.90/final_geo/pw_scf.in",
    "Disp 1.00 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.00/final_geo/pw_scf.in",
    "Disp 1.10 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.10/final_geo/pw_scf.in",
    "Disp 1.20 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.20/final_geo/pw_scf.in",
    "Disp 1.30 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.30/final_geo/pw_scf.in",
    "Disp 1.40 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.40/final_geo/pw_scf.in",
    "Disp 1.50 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.50/final_geo/pw_scf.in",
    "Disp 1.60 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.60/final_geo/pw_scf.in",
    "Disp 1.70 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.70/final_geo/pw_scf.in",
    "Disp 1.80 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.80/final_geo/pw_scf.in",
    "Disp 1.90 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_1.90/final_geo/pw_scf.in",
    "Disp 2.00 (PBE0)": "/Volumes/UT-Disk-2/lithium-fluoride/saverio_geom_direction_111_disp_empty_states_40_disp_2.00/final_geo/pw_scf.in",
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
custom_scene_settings = {"showBonds": False, "showPolyhedra": False}

camera_state_x = {
    "position": {"x": 25, "y": 0, "z": 0},
    "quaternion": {"x": 0.5, "y": 0.5, "z": 0.5, "w": 0.5},
    "zoom": 4.0
}
camera_state_y = {
    "position": {"x": 0, "y": 25, "z": 0},
    "quaternion": {"x": 0.5, "y": 0.5, "z": 0.5, "w": -0.5},
    "zoom": 4.0
}
camera_state_z = {
    "position": {"x": 0, "y": 0, "z": 25},
    "quaternion": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "zoom": 4.0
}

comp_1x = ctc.StructureMoleculeComponent(init_graph, id="struct_1x", scene_settings=custom_scene_settings)
comp_1y = ctc.StructureMoleculeComponent(init_graph, id="struct_1y", scene_settings=custom_scene_settings)
comp_1z = ctc.StructureMoleculeComponent(init_graph, id="struct_1z", scene_settings=custom_scene_settings)

comp_2x = ctc.StructureMoleculeComponent(init_graph, id="struct_2x", scene_settings=custom_scene_settings)
comp_2y = ctc.StructureMoleculeComponent(init_graph, id="struct_2y", scene_settings=custom_scene_settings)
comp_2z = ctc.StructureMoleculeComponent(init_graph, id="struct_2z", scene_settings=custom_scene_settings)



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


import json

# Clientside callbacks to force camera state on scene data update
for scene_id, camera_state in [
    ("CTstruct_1x_scene", camera_state_x),
    ("CTstruct_1y_scene", camera_state_y),
    ("CTstruct_1z_scene", camera_state_z),
    ("CTstruct_2x_scene", camera_state_x),
    ("CTstruct_2y_scene", camera_state_y),
    ("CTstruct_2z_scene", camera_state_z),
]:
    app.clientside_callback(
        f"""
        function(data) {{
            if (!data) return window.dash_clientside.no_update;
            
            let attempts = 0;
            const interval = setInterval(() => {{
                attempts++;
                const el = document.getElementById("{scene_id}");
                if (!el && attempts < 50) return;
                
                // Find the 'uj' (Three.js viewer) instance in el's React fiber tree
                const fiberKey = Object.keys(el || {{}}).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
                let uj = null;
                if (fiberKey) {{
                    let fiber = el[fiberKey];
                    while (fiber) {{
                        let hook = fiber.memoizedState;
                        while (hook) {{
                            if (hook.memoizedState && typeof hook.memoizedState === 'object') {{
                                const val = hook.memoizedState.current;
                                if (val && typeof val === 'object' && val.camera && val.controls) {{
                                    uj = val;
                                    break;
                                }}
                            }}
                            hook = hook.next;
                        }}
                        if (uj) break;
                        fiber = fiber.return;
                    }}
                }}
                
                if (uj || attempts >= 50) {{
                    clearInterval(interval);
                    if (uj) {{
                        const camera_state = {json.dumps(camera_state)};
                        
                        // Override setupCamera to ensure it always uses our correct parameters and never resets to Z-view
                        uj.setupCamera = function(e) {{
                            this.camera.position.set(camera_state.position.x, camera_state.position.y, camera_state.position.z);
                            this.camera.quaternion.set(camera_state.quaternion.x, camera_state.quaternion.y, camera_state.quaternion.z, camera_state.quaternion.w);
                            this.camera.zoom = camera_state.zoom;
                            
                            if ("{scene_id}".includes('x_scene')) {{
                                this.camera.up.set(0, 0, 1);
                            }} else if ("{scene_id}".includes('y_scene')) {{
                                this.camera.up.set(1, 0, 0);
                            }} else if ("{scene_id}".includes('z_scene')) {{
                                this.camera.up.set(0, 1, 0);
                            }}
                            this.camera.updateProjectionMatrix();
                            this.controls.target.set(0, 0, 0);
                            this.controls.update();
                            this.renderScene();
                        }};
                        
                        // Call the overridden setupCamera once to apply immediately
                        uj.setupCamera();
                        
                        // Ensure controls are resized correctly once the element is displayed and has non-zero size
                        if (uj.controls && typeof uj.controls.handleResize === 'function') {{
                            uj.controls.handleResize();
                        }}
                        
                        // Add event listeners on pointer down, touch start, and wheel events
                        // to dynamically handle resize when user starts interacting
                        const canvas = el.querySelector("canvas");
                        if (canvas && !canvas._resizeListenerAdded) {{
                            const triggerResize = () => {{
                                if (uj.controls && typeof uj.controls.handleResize === 'function') {{
                                    uj.controls.handleResize();
                                }}
                            }};
                            canvas.addEventListener("pointerdown", triggerResize, {{ passive: true }});
                            canvas.addEventListener("touchstart", triggerResize, {{ passive: true }});
                            canvas.addEventListener("wheel", triggerResize, {{ passive: true }});
                            canvas._resizeListenerAdded = true;
                        }}
                    }}
                }}
            }}, 50);
            
            return window.dash_clientside.no_update;
        }}
        """,
        Output(scene_id, "customCameraState"),
        Input(scene_id, "data")
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, port=port)