import os
import json
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Official mod database map from the historical repository list
COMMUNITY_MODS = {
    "Blair.zip": {"name": "Blair", "type": "skin"},
    "Chomusuke.zip": {"name": "Chomusuke", "type": "skin"},
    "ChomusukeLegendary.zip": {"name": "Chomusuke Legendary", "type": "skin"},
    "DokiDokiChomusukeClub.zip": {"name": "Doki Doki Chomusuke Club", "type": "skin"},
    "Elizabeth III.zip": {"name": "Elizabeth III", "type": "skin"},
    "Ferris.zip": {"name": "Ferris Font Patch", "type": "utility_font"},
    "FileNotFound.zip": {"name": "FileNotFound", "type": "skin"},
    "FileNotFoundTSP.zip": {"name": "FileNotFound (TheSwiftPhantom)", "type": "skin"},
    "Ichigo.zip": {"name": "Ichigo Mod Manager", "type": "manager"},
    "Kaguya.zip": {"name": "Kaguya", "type": "skin"},
    "Komi.zip": {"name": "Komi", "type": "skin"},
    "TabbyGoodies": {"name": "Tabby Cat Goodies Pack", "type": "data_patch"},
    "TabbyPets": {"name": "Tabby Cat Pets Pack", "type": "data_patch"},
    "tabby_bundle.js": {"name": "Tabby_Bundle Fix Script", "type": "patch_script"}
}

def clean_and_upgrade_v3(target_directory):
    """Rewrites old configurations to ensure modern Chrome security compatibility."""
    manifest_path = os.path.join(target_directory, "manifest.json")
    if not os.path.exists(manifest_path):
        return True
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data["manifest_version"] = 3
        if "background" in data and "scripts" in data["background"]:
            scripts = data["background"]["scripts"]
            data["background"] = {"service_worker": scripts if isinstance(scripts, list) else scripts}
            
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed upgrading manifest configurations: {e}")
        return False

def inject_universal_font(target_directory, raw_font_path):
    """Converts and links any chosen font file layout directly into the system CSS stylesheet templates."""
    font_filename = os.path.basename(raw_font_path)
    _, ext = os.path.splitext(font_filename)
    
    format_mapping = {".ttf": "truetype", ".otf": "opentype", ".woff": "woff", ".woff2": "woff2"}
    font_format = format_mapping.get(ext.lower(), "truetype")
    internal_asset_name = f"ferris_font_asset{ext.lower()}"
    
    try:
        shutil.copy(raw_font_path, os.path.join(target_directory, internal_asset_name))
    except Exception as e:
        messagebox.showerror("Error", f"Could not move font file: {e}")
        return False

    font_css_payload = f"""
    @font-face {{
        font-family: 'TabbyStudioCustom';
        src: url('{internal_asset_name}') format('{font_format}');
    }}
    body, html, *, .tabby-text, text {{
        font-family: 'TabbyStudioCustom' !important;
    }}
    """
    
    for root_dir, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith(".css"):
                try:
                    with open(os.path.join(root_dir, file), "a", encoding="utf-8") as f:
                        f.write(font_css_payload)
                except:
                    pass
    return True

def execute_mod_pipeline():
    # 1. Choose Mod Archive File
    archive_source = filedialog.askopenfilename(
        title="1. Select Any Tabby Mod File (.zip, .js, or folder)",
        filetypes=[("Tabby Mod Files", "*.zip *.js"), ("All Files", "*.*")]
    )
    if not archive_source: return
    
    filename = os.path.basename(archive_source)
    mod_info = COMMUNITY_MODS.get(filename, {"name": "Custom Unlisted Mod", "type": "skin"})
    
    # 2. Select Font Option (Optional for skins, mandatory for Ferris font rules)
    apply_custom_font = messagebox.askyesno("Font Customization", f"Would you like to inject a custom text font into this {mod_info['name']} mod structure?")
    font_source_path = ""
    if apply_custom_font:
        font_source_path = filedialog.askopenfilename(
            title="Select Font File (.ttf, .otf, .woff, .woff2)",
            filetypes=[("Universal Font Formats", "*.ttf *.otf *.woff *.woff2")]
        )
        if not font_source_path: return

    # 3. Select Target Project Destination Workspace
    output_destination = filedialog.askdirectory(title="2. Select Destination Folder to Unpack Mod Assets")
    if not output_destination: return
    
    working_project_dir = os.path.join(output_destination, mod_info["name"].replace(" ", "_"))
    os.makedirs(working_project_dir, exist_ok=True)

    # Processing Sequence
    try:
        if filename.endswith(".zip"):
            with zipfile.ZipFile(archive_source, 'r') as zip_ref:
                zip_ref.extractall(working_project_dir)
        else:
            shutil.copy(archive_source, os.path.join(working_project_dir, filename))
    except Exception as e:
        messagebox.showerror("Extraction Error", f"Failed unpacking selected file elements: {e}")
        return

    # Configuration and upgrades
    pipeline_success = clean_and_upgrade_v3(working_project_dir)
    if pipeline_success and apply_custom_font:
        pipeline_success = inject_universal_font(working_project_dir, font_source_path)

    if pipeline_success:
        messagebox.showinfo(
            "Purrrr Complete!", 
            f"Successfully organized and updated: {mod_info['name']}\n\n"
            f"Location:\n{working_project_dir}\n\n"
            f"Next Steps:\n"
            f"1. Open chrome://extensions/\n"
            f"2. Toggle 'Developer mode' ON.\n"
            f"3. Click 'Load unpacked' and choose this folder."
        )

# Main Application Window Initialization
app = tk.Tk()
app.title("purrrr")
app.geometry("500x280")
app.eval('tk::PlaceWindow . center')

tk.Label(app, text="🐾 purrrr - Tabby Cat Mod Toolkit 🐾", font=("Arial", 14, "bold")).pack(pady=15)
tk.Label(app, text="Automatically patching Ferris, Ichigo, Chomusuke, and community skins.", font=("Arial", 9), fg="#666666").pack(pady=2)
tk.Label(app, text="Fixes old file errors by updating layouts directly to Manifest V3.", font=("Arial", 9), fg="#666666").pack(pady=2)

# Build out Interactive Database Directory Grid Matrix
frame = tk.LabelFrame(app, text=" Supported Mod Repositories ", padx=10, pady=5)
frame.pack(pady=10, fill="x", padx=20)

combo_list = [f"{v['name']} ({k})" for k, v in COMMUNITY_MODS.items()]
repo_selector = ttk.Combobox(frame, values=combo_list, width=55, state="disabled")
repo_selector.pack(pady=5)
repo_selector.set("System Ready: Select any file above to process instantly.")

launch_action_btn = tk.Button(
    app, text="🐱 Load Mod File & Begin Custom Patch", 
    command=execute_mod_pipeline, 
    bg="#107c41", fg="white", 
    font=("Arial", 10, "bold"), padx=20, pady=8
)
launch_action_btn.pack(pady=15)

app.mainloop()
