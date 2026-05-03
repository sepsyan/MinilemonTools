import bpy
import mathutils
import os
import json
import datetime

def output_preview():
    today = datetime.datetime.now()
    formatted_date = today.strftime("%Y.%m.%d")
    asset_name = os.path.basename(bpy.data.filepath).split('.')[0]
    output_preview = f'//..\\_Preview\\{formatted_date}\\{asset_name}\\{asset_name}'
    os.makedirs(os.path.dirname(bpy.path.abspath(output_preview)), exist_ok=True)
    return output_preview

def create_objects():
    emp = "e_root"
    cam_name = 'e_cam'
    empty = bpy.data.objects.get(emp)
    if not empty:
        empty = bpy.data.objects.new(emp, None)
        empty.location = (0,0,0)
        bpy.context.scene.collection.objects.link(empty)

    if cam_name not in bpy.data.objects:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = cam_name
    else:
        cam = bpy.data.objects[cam_name ]
        
    cam.parent = empty
    bpy.context.scene.camera = cam

    collection = [obj for obj in bpy.context.scene.objects if obj.hide_viewport == False]

    objects = [obj for obj in collection if obj.type == 'MESH']


    coords = []
    for obj in objects:
        for corner in obj.bound_box:
            coords.append(obj.matrix_world @ mathutils.Vector(corner))

    min_corner = mathutils.Vector((min([v.x for v in coords]),
                                   min([v.y for v in coords]),
                                   min([v.z for v in coords])))
    max_corner = mathutils.Vector((max([v.x for v in coords]),
                                   max([v.y for v in coords]),
                                   max([v.z for v in coords])))

    center = (min_corner + max_corner) / 2


    empty.location = center
    size = max(max_corner.y, max_corner.x)
    cam.location = mathutils.Vector((0, 0, -size*3.5))


    constraint = cam.constraints.get('Track To')
    if not constraint:
        constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    return empty, cam

def create_frames():
    empty, cam = create_objects()
    frames = {
        1: (-90,0,0),          
        2: (-90,0,45),          
        3: (-90,0,90),          
        4: (-90,0,135),          
        5: (-90,0,180),          
        6: (-90,0,225),          
        7: (-90,0,270),           
        8: (135,0,0),          
        9: (45,0,0), 
        10: (-135,0,0), 
        11: (-45,0,0), 
    }

    for f, rot in frames.items():
        empty.rotation_euler = [r*(3.14159/180) for r in rot]
        empty.keyframe_insert(data_path="rotation_euler", frame=f)
    return empty.animation_data

def view_cam():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                


  
overlays = ['show_floor','show_text',
            'show_cursor','show_stats',
            'show_annotation','show_camera_guides',
            'show_extras','show_bones',
            'show_relationship_lines','show_object_origins',
            'show_outline_selected','show_face_orientation',
            'show_axis_x','show_axis_y','show_axis_z',
            'show_wireframes']
shadings = ['color_type', 'show_object_outline', 'background_type']   
renders = ['resolution_x', 'resolution_y', 'resolution_percentage', 'filepath']
scenes = ['frame_start','frame_end']
image_settings = ['file_format']   
      
def save_viewport_settings():
    save_path = os.path.join(bpy.app.tempdir, "viewport_settings.json")
    data = {}
                
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    overlay = space.overlay
                    shading = space.shading
                    
                    data['overlay'] = {p.identifier: getattr(overlay, p.identifier)
                                    for p in overlay.bl_rna.properties if p.identifier in overlays}
                    data['shading'] = {p.identifier: getattr(shading, p.identifier)
                                    for p in shading.bl_rna.properties if p.identifier in shadings}
                    data['shading']['background_color'] = tuple(shading.background_color)
    scene = bpy.context.scene
    render = scene.render
    image_setting = render.image_settings
    data['render'] = {p.identifier: getattr(render, p.identifier)
                    for p in render.bl_rna.properties if p.identifier in renders}
    data['scene'] = {p.identifier: getattr(scene, p.identifier)
                    for p in scene.bl_rna.properties if p.identifier in scenes}
    data['image_settings'] = {p.identifier:getattr(image_setting, p.identifier)
                    for p in image_setting.bl_rna.properties if p.identifier in image_settings}
    
    with open(save_path, "w") as f:
        json.dump(data, f, indent=4)
    print("Viewport settings saved to:", save_path)


def restore_viewport_settings():
    save_path = os.path.join(bpy.app.tempdir, "viewport_settings.json")
    if not os.path.exists(save_path):
        print("No saved settings found.")
        return

    with open(save_path, "r") as f:
        data = json.load(f)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    overlay = space.overlay
                    shading = space.shading

                    for prop in overlay.bl_rna.properties:
                        if prop.identifier in overlays:
                            pname = prop.identifier
                            setattr(overlay, pname, data['overlay'][pname])
                                
                    for prop in shading.bl_rna.properties:
                        if prop.identifier in shadings:
                            pname = prop.identifier
                            setattr(shading, pname, data['shading'][pname])    
    
    scene = bpy.context.scene
    render = scene.render
    image_setting = render.image_settings
    
    for prop in scene.bl_rna.properties:
        if prop.identifier in scenes:
            pname = prop.identifier
            setattr(scene, pname, data['scene'][pname])
    
    for prop in render.bl_rna.properties:
        if prop.identifier in renders:
            pname = prop.identifier
            setattr(render, pname, data['render'][pname])
    
    for prop in image_setting.bl_rna.properties:
        if prop.identifier in image_settings:
            pname = prop.identifier
            setattr(image_setting, pname, data['image_settings'][pname])
            
    print("Viewport settings restored.")


def save_viewport_view():
    save_view_path = os.path.join(bpy.app.tempdir, "viewport_view.json")

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_3d = area.spaces.active.region_3d
            data = {
                "location": list(region_3d.view_location),
                "rotation": list(region_3d.view_rotation),
                "distance": region_3d.view_distance
            }
            with open(save_view_path, "w") as f:
                json.dump(data, f, indent=4)
            print("Viewport view saved:", save_view_path)
            break

def restore_viewport_view():
    save_view_path = os.path.join(bpy.app.tempdir, "viewport_view.json")

    if not os.path.exists(save_view_path):
        print("No saved viewport view found.")
        return

    with open(save_view_path, "r") as f:
        data = json.load(f)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_3d = area.spaces.active.region_3d
            region_3d.view_location = data["location"]
            region_3d.view_rotation = data["rotation"]
            region_3d.view_distance = data["distance"]
            print("Viewport view restored.")
            break
            
def create_visual(wire=True):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    overlay = space.overlay
                    shading = space.shading
                    
                    for prop in overlay.bl_rna.properties:
                        if not prop.is_readonly:

                            if prop.identifier in overlays:
                                pname = prop.identifier

                                setattr(overlay, pname, False)

                    shading.show_object_outline = False
                    shading.background_type = 'VIEWPORT'
                    shading.background_color = [0.022,0.022,0.022]
                    if wire:
                        overlay.show_wireframes = True
                        shading.color_type = 'RANDOM'
                    else:
                        overlay.show_wireframes = False
                        shading.color_type = 'OBJECT'
                        
    bpy.ops.object.select_all(action='DESELECT')
    
def create_output(wire=True):
    s = bpy.context.scene
    r = s.render
    r.resolution_x = 2048
    r.resolution_y = 2048
    r.resolution_percentage = 100
    s.frame_start = 1
    s.frame_end = 11
    
    
    if wire:
        output_path = f"{output_preview()}_wire_##"
    else:
        output_path = f"{output_preview()}_##"
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = 'JPEG'



def serialize_collection(col):
    return {
        "collection name": col.name,
        "objects": {'mesh' : {
                    obj.name :{
                            'type': obj.type,
                            'vertices':len(obj.data.vertices),
                            'polygons': len(obj.data.polygons)
                            } 
                    for obj in col.objects
                    if obj.type == 'MESH'
                    },
                    'others' : {
                    obj.name :{
                            'type': obj.type
                            }
                    for obj in col.objects
                    if obj.type != 'MESH'
                    }
                    },
        "children": [serialize_collection(child) for child in col.children]
    }

def save_collections_hierarchy():
    save_json_path = bpy.path.abspath(f'{output_preview()}_collections_hierarchy.json')

    root = bpy.context.scene.collection
    data = serialize_collection(root)
    data['blender version'] = ".".join(map(str, bpy.app.version))
    data['filepath'] = bpy.data.filepath
    
    with open(save_json_path, "w") as f:
        json.dump(data, f, indent=4)
    print("Collections hierarchy saved to:", save_json_path)

def open_folder():
    if bpy.data.filepath:
        dir = os.path.dirname(os.path.dirname(output_preview()))
        folder_path = bpy.path.abspath(dir)
        print('folder path',  dir, folder_path)
        if os.path.isdir(folder_path):
            os.startfile(folder_path)

def capture(wire=True):
    empty, cam = create_objects()
    create_frames()
    create_visual(wire=wire)
    create_output(wire=wire)
    save_viewport_view()
    view_cam()
    bpy.ops.render.opengl(animation=True)
    bpy.data.objects.remove(empty)
    bpy.data.objects.remove(cam)
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    restore_viewport_view()

def execute():
    if bpy.data.filepath:
        save_collections_hierarchy()
        save_viewport_settings()
        capture(True)
        capture(False)
        restore_viewport_settings()

