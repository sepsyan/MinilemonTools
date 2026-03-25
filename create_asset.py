import bpy
import os

ASSET_PATH = r"M:\MLA\02_Productions\01_Assets"
GITHUB_REPO = "MinilemonTools"


def scene_desc():
    C = bpy.context
    C.render.engine = 'CYCLES'

def clean_scene():
    if bpy.data.filepath == '':
        # bpy.ops.wm.read_factory_settings(use_empty=True)
        for c in bpy.context.scene.collection.children:
            bpy.data.collections.remove(c)
        for o in bpy.data.objects:
            bpy.data.objects.remove(o)
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    # scene_desc()
    
def get_asset_items(self, context):
    ASSET_DIR = ASSET_PATH
    items = []

    if not os.path.exists(ASSET_DIR):
        return items

    for i, name in enumerate(os.listdir(ASSET_DIR)):
        full_path = os.path.join(ASSET_DIR, name)

        if os.path.isdir(full_path): 
            items.append((name, name, "", i))

    return items

def get_or_create_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
    return col

def set_parent(parent, children):
    if children.name not in parent.children:
        parent.children.link(children)

def create_asset_structure(type,asset_name):
    S = bpy.context.window.scene
    parent_name = f"{type.lower()}_{asset_name}"
    parent = get_or_create_collection(parent_name)

    set_parent(S.collection, parent)
    
    
    groups = ["geo", "rig", "proxy"]
    created = {}

    for g in groups:
        name = f"{g}_{asset_name}_grp"
        col = get_or_create_collection(name)
        set_parent(parent, col)

        created[g] = col

    reference = get_or_create_collection('reference')
    preview = get_or_create_collection('preview')
    set_parent(S.collection, reference)
    set_parent(S.collection, preview)
    
    image = get_or_create_collection('ref_image')
    geo = get_or_create_collection('ref_geo')
    set_parent(reference, image)
    set_parent(reference, geo)

    parent.color_tag = 'COLOR_03'
    reference.color_tag = 'COLOR_02'
    preview.color_tag = 'COLOR_01'
    return parent, created

def load_dummy():
    D = bpy.data
    S = bpy.context.scene
    addon_path = os.path.join(bpy.utils.script_path_user(), "addons", GITHUB_REPO )
    dummy_path = os.path.join(addon_path, 'assets','dummy_wayan_scale.blend')
    col = get_or_create_collection('ref_geo')
    col_ref = get_or_create_collection('reference')
    with bpy.data.libraries.load(dummy_path, link=False) as (data_from, data_to):
        data_to.objects = ["dummy_wayan_scale"]
        # for obj in data_to.objects:
        #     if isinstance(obj, str) or obj is None:
        #         obj = bpy.data.objects.get("dummy_wayan_scale")

        #     if obj and isinstance(obj, bpy.types.Object):
                
        #         for c in obj.users_collection:
        #             c.objects.unlink(obj)

        #         col.objects.link(obj)

    for obj in data_to.objects:
        print(obj, type(obj))
        if obj:
            col.objects.link(obj)

    set_parent(bpy.context.scene.collection, col_ref)
    set_parent(col_ref, col)

        # for obj in data_to.objects:
        #     if obj:
        #         if col:
        #             col.objects.link(obj)
                

def create_assets(type, name):
    main_path = os.path.join(ASSET_PATH,type.upper(),f'{type.lower()}_{name}')
    os.makedirs(main_path, exist_ok=True)
    for dir in ('_Crosswalk','_Backups','_Preview','_Render','Model','Rig','Textures'):
        asset_dir = os.path.join(main_path,dir)
        os.makedirs(asset_dir, exist_ok=True)

    create_asset_structure(type, name)

# create_assets('AN','angsaLemon')
# load_dummy()