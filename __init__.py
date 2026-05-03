bl_info = {
    "name": "MiniLemon Tools Updater",
    "version": (1, 1, 1),
    "blender": (4, 5, 0),
    "category": "MiniLemon",
}


import bpy
import importlib
import urllib.request
import json
import zipfile
import tempfile
import os
import shutil
from bpy.utils import register_class, unregister_class
from . import create_asset
from . import create_preview
importlib.reload(create_asset)
importlib.reload(create_preview)

GITHUB_USER = "sepsyan"
GITHUB_REPO = "MinilemonTools"

API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"


def get_latest():
    try:
        with urllib.request.urlopen(API_URL) as res:
            return json.loads(res.read().decode())
    except:
        return None


def parse_version(tag):
    return tuple(map(int, tag.replace("v", "").split(".")))


def update_addon(zip_url):
    tmp_zip = os.path.join(tempfile.gettempdir(), "addon.zip")
    extract_dir = os.path.join(tempfile.gettempdir(), "addon_extract")

  
    urllib.request.urlretrieve(zip_url, tmp_zip)

    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    
    inner = os.listdir(extract_dir)[0]
    new_path = os.path.join(extract_dir, inner)

    addon_path = os.path.join(bpy.utils.script_path_user(), "addons", GITHUB_REPO )

    
    for item in os.listdir(new_path):
        src = os.path.join(new_path, item)
        dst = os.path.join(addon_path, item)

        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    data = get_latest()
    ver = ".".join(map(str, parse_version(data.get('tag_name', (0,0,0)))))
    return f"Addon updated to version v{ver}, Please Restart Blender"

def check_update():
    data = get_latest()
    if not data:
        return

    latest_version = parse_version(data["tag_name"])
    zip_url = data["zipball_url"]

    if latest_version > bl_info["version"]:
        print("Update found:", latest_version)
        return update_addon(zip_url)

class update_minilemontools_op(bpy.types.Operator):
    '''Click untuk update tools'''
    bl_idname = "update.minilemontools"
    bl_label = "Update Tools"

    def execute(self, context):
        update = check_update()
        # self.report({'INFO'}, update)
        return {'FINISHED'}

class create_asset_op(bpy.types.Operator):
    '''Click untuk membuat asset baru'''
    bl_idname = "asset.create"
    bl_label = "Asset Create"
    def execute(self, context):
        props = context.scene.mlt_props
        asset_enum = props.asset_enum
        asset_text = props.asset_text
        main_path = os.path.join(create_asset.ASSET_PATH,asset_enum.upper(),f'{asset_enum.lower()}_{asset_text}')
        if os.path.isdir(main_path):
            self.report({'ERROR'}, f"Asset {asset_enum.lower()}_{asset_text} sudah ada, gunakan nama lain")
        else:
            create_asset.create_assets(asset_enum, asset_text)
        
        return {'FINISHED'}

class clean_scene_op(bpy.types.Operator):
    '''Bersihin semua file bawaan blender\nKalo blendernya belum di-save.'''
    bl_idname = "asset.clean"
    bl_label = "Clear Scene"

    def execute(self, context):
        
        bpy.app.timers.register(create_asset.clean_scene, first_interval=0.1)
        self.report({'INFO'}, "Resetting scene...")
        
        return {'FINISHED'}

class append_dummy_op(bpy.types.Operator):
    '''Append dummy wayan for scale'''
    bl_idname = "asset.append_dummy"
    bl_label = "Append Dummy"

    def execute(self, context):
        create_asset.load_dummy()
        return {'FINISHED'}

class render_preview_op(bpy.types.Operator):
    '''Render preview'''
    bl_idname = "asset.render_preview"
    bl_label = "Render Preview"

    def execute(self, context):
        if bpy.data.filepath:
            create_preview.execute()
        else:
            self.report({'ERROR'}, "Blendernya di-save dulu ya")
        return {'FINISHED'}

class open_folder_preview_op(bpy.types.Operator):
    '''Open Render preview Folder'''
    bl_idname = "asset.render_preview_folder"
    bl_label = "Open Folder Preview"

    def execute(self, context):
        if bpy.data.filepath:
            create_preview.open_folder()
        else:
            self.report({'ERROR'}, "Blendernya di-save dulu ya")
        return {'FINISHED'}

    
class MinilemonTools_PT_panel(bpy.types.Panel):
    ver = ".".join(map(str, bl_info.get("version", (0,0,0))))
    bl_label = f"Mini Lemon Tools v{ver}"
    bl_idname = "MinilemonTools_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MLA'

    def draw(self, context):
        layout = self.layout
        layout.operator(update_minilemontools_op.bl_idname, text="Check Update", icon='FILE_REFRESH')
        

class MLT_AssetCreation_PT_panel(bpy.types.Panel):
    '''Panel buat bikin asset'''
    bl_label = f"Asset Creation"
    bl_idname = "MLT_AsetCreation_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MLA'

    def draw(self, context):
        layout = self.layout
        props = context.scene.mlt_props
        layout.operator(clean_scene_op.bl_idname, icon='TRASH')
        layout.separator()
        row = layout.row(align=True)
        row.scale_x = 0.2
        row.prop(props, 'asset_enum',text='')
        row.scale_x = 0.7
        row.prop(props, 'asset_text',text='')
        layout.operator(create_asset_op.bl_idname, icon='ASSET_MANAGER')
        layout.separator()
        layout.operator(append_dummy_op.bl_idname, icon='OUTLINER_OB_ARMATURE')

class MLT_Preview_PT_panel(bpy.types.Panel):
    '''Panel buat bikin preview'''
    bl_label = f"Preview"
    bl_idname = "MLT_Preview_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MLA'

    def draw(self, context):
        layout = self.layout
        layout.operator(render_preview_op.bl_idname, icon='RESTRICT_RENDER_OFF')
        layout.operator(open_folder_preview_op.bl_idname, icon='FILE_FOLDER_LARGE')


class MLT_Props(bpy.types.PropertyGroup):
    asset_enum: bpy.props.EnumProperty(name="Type",description="Select asset type",items=create_asset.get_asset_items)
    asset_text: bpy.props.StringProperty(name="Asset Name",default="", description='Format nama harus camelCase, huruf kecil diawal, kalo ada spasi langsung pake huruf kapital.')

classes = (
    MLT_Props,
    update_minilemontools_op,
    create_asset_op,
    clean_scene_op,
    append_dummy_op,
    render_preview_op,
    open_folder_preview_op,
    MinilemonTools_PT_panel,
    MLT_AssetCreation_PT_panel,
    MLT_Preview_PT_panel,
)

def register():
    for cls in classes:
        register_class(cls)
    # check_update()
    bpy.types.Scene.mlt_props = bpy.props.PointerProperty(type=MLT_Props)

def unregister():
    del bpy.types.Scene.mlt_props
    for cls in reversed(classes):
        unregister_class(cls)
    pass
