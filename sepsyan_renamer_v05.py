# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Sepsyan Renamer",
    "author": "Septyan Roche",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "ctrl + shift + R",
    "description": "multiple rename object",
    "category": "sepsyan"}
    
    
import bpy
from bpy.props import BoolProperty,StringProperty,EnumProperty, IntProperty
from bpy.utils import register_class, unregister_class

class SR_props(bpy.types.PropertyGroup):
    DT_min : bpy.props.FloatProperty(name="min", description="nilai minimum influence", default=0.1, min=0.0, max=1.0)
    LR : BoolProperty(name='L/R', default=False, description='tambahkan Left/Right di belakang nama bone')
    rename_data : BoolProperty(name='Rename Data', default=True, description='rename data juga')
    prefix : StringProperty(name='prefix',default='', description='kata depan')
    del_prefix : BoolProperty(name='del pr_', default = False, description='hapus kata depan')
    sufix : StringProperty(name='sufix',default='', description='kata belakang')
    find : StringProperty(name='find',default='', description='find word to replace with')
    replace : StringProperty(name='replace',default='', description='replace word with')
    option : EnumProperty(name='option',
        items= [('prefix_sufix','Prefix - Sufix','prefix_sufix'),('find_replace','Find - Replace','find_replace'), ('numbering','Numbering','numbering'), ('trim','Trim','trim')],
        default = 'prefix_sufix')
    numbering : BoolProperty(name='numbering', default=False, description='Give numbering to suffix')
    number_clean : BoolProperty(name='clean', default=False, description='Clear original name')
    number_start : IntProperty(name='num_start', default=0, min=0, description='Number start with this')
    number_padding : IntProperty(name='num_pad', default=2, min=1, description='Number padding')
    trim : BoolProperty(name='trim', default=False, description='Trim by each character')
    trim_start : IntProperty(name='trim_start', default=0, min=0, description='Trim prefix')
    trim_end : IntProperty(name='trim_end', default=0, min=0, description='Trim suffix')
    
    localview : BoolProperty(name='localview', default=False)

class preview(bpy.types.PropertyGroup):
    name : StringProperty()
    
def localview(status):
    if status == True:
        bpy.ops.view3d.localview()
        bpy.context.scene.SR.localview = True
    elif status == False:
        #bpy.ops.view3d.localview()
        bpy.context.scene.SR.localview = False
    
class selectRenameOB(bpy.types.Operator):
    bl_idname = "object.renamer_select"
    bl_label = "select"
    bl_options = {'REGISTER','UNDO'}
    ob : StringProperty()
    type : StringProperty()
    selected = []
    
    def execute(self, context):
        SR = context.scene.SR
        localview(False)
       # try:
        if self.type=='obj':
            for o in context.selected_objects:
                self.selected.append(o.name)
            bpy.ops.object.select_all(action='DESELECT')

            bpy.data.objects[self.ob].select_set(True)
            #bpy.context.scene.objects.active = bpy.data.objects[self.ob]
            #bpy.ops.view3d.view_selected(use_all_regions=1)
            localview(True)
            for b in self.selected:
                context.scene.objects[b].select_set(True)
            print (self.ob)
        if self.type=='bone':
            bpy.ops.pose.select_all(action='DESELECT')

            bpy.data.objects[context.active_object.name].data.bones[self.ob].select_set(True)
            #bpy.context.scene.objects.active = bpy.data.objects[self.ob]
            bpy.ops.view3d.view_selected(use_all_regions=1)
            print (self.ob)
#        except:
#            self.report({'ERROR'}, 'ngga ada di viewport')
            
        return {'FINISHED'}
    
    def cancel(self, context):
        SR = context.scene.SR
        if SR.localview == True:
            bpy.ops.view3d.localview()
            SR.localview = False
        return {'CANCELLED'}


def main(self,context):
    aob = context.active_object
    SR = context.scene.SR
        
    if aob.type not in {'EMPTY'} and aob.mode == 'OBJECT':
            
        for i, ob in enumerate(context.selected_editable_objects):
            print("'%s'" % ob.name, end=",")
            
            if SR.numbering == True:
                ob.name = ob.name + str(i+SR.number_start).zfill(SR.number_padding)
            
            if SR.prefix != '' or SR.sufix !='':
                if ob.name.startswith(SR.prefix):
                    ob.name = ob.name
                else:
                    ob.name = SR.prefix + ob.name + SR.sufix
                       
                if SR.del_prefix:
                    ob.name = ob.name.replace(SR.prefix, '')
            if (SR.find !='' or SR.replace !=''):
                ob.name = ob.name.replace(SR.find,SR.replace)
                
            if SR.rename_data:
                ob.data.name = ob.name
                    
        
    if aob.mode == 'POSE':
        for i,pbo in enumerate(context.selected_pose_bones):
            print("'%s'" % pbo.name, end=",")
                
            if SR.numbering == True:
                if SR.number_clean:
                    pbo.name = str(i+ SR.number_start).zfill(SR.number_padding)
                else:
                    pbo.name = pbo.name + str(i+ SR.number_start).zfill(SR.number_padding)
            if SR.prefix != '':
                pbo.name = SR.prefix + pbo.name
            if SR.sufix !='':
                pbo.name = pbo.name + SR.sufix
            if SR.trim:
                if SR.trim_end > 0:
                    pbo.name = pbo.name[SR.trim_start:SR.trim_end]
                else:
                    pbo.name = pbo.name[SR.trim_start:]
                        
            if (SR.find !='' or SR.replace !=''):
                pbo.name = pbo.name.replace(SR.find,SR.replace)   
            if SR.LR:
                if pbo.name.endswith(SR.side):
                    pbo.name = pbo.name
                else:
                    pbo.name = pbo.name.replace('.L','').replace('.R','').replace('.001','') + SR.side
                
                    

class updateOp(bpy.types.Operator):
    '''update rename'''
    bl_idname = 'object.renamer_update'
    bl_label = ''
    bl_options = {'REGISTER','UNDO'}
    def execute(self, context):
        main(self, context)
        return {'FINISHED'}   
             
class renamerOp(bpy.types.Operator):
    """rename multiple object"""
    bl_idname = "object.renamer"
    bl_label = "sepsyan renamer v0.5"
    bl_options = {'REGISTER','UNDO'}
    dialog_width =  300
    #( value, name, description )
    side_set = [('.L','L','L'),('.R','R','R')]
    side : EnumProperty(name='side', items=side_set)
    sure_set = [('add','add','add word first and last'),('replace','replace','replace word with')]
    sure : EnumProperty(name='sure', items=sure_set, default='add')
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        SR = context.scene.SR
       
        if context.active_object.mode == 'OBJECT':
            
            #row.prop(SR, 'sure',expand=1)
            row.prop(SR, 'rename_data')
            #row.prop(SR, 'del_prefix')
            row = col.row()
            row.prop(SR, 'option', expand=True)
            if SR.option == 'prefix_sufix':
                row = col.row(align=1)
                row.label(text='PREFIX')
                rt = row.row()
                rt.alignment = 'RIGHT'
                rt.label(text='SUFFIX')
                # gagal sharing variabel antar operator
                #row.operator("object.renamer_clear").clear_type= 'pre'
                row = col.row(align=1)
                #if (self.sure== 'add'):
                row.prop(SR, 'prefix',text='')
                row.prop(SR, 'sufix',text='')
                col.separator()
                row = col.row()
                
            if SR.option == 'find_replace':
                row = col.row(align=1)
                row.label(text='FIND')
                rt = row.row()
                rt.alignment = 'RIGHT'
                rt.label(text='REPLACE')
                #if (self.sure== 'replace'):
                row = col.row(align=1)
                row.prop(SR, 'find',text='')
                row.prop(SR, 'replace',text='')
                col.separator()
                row = col.row()
               
            if SR.option == 'numbering':
                row = col.row(align=1)
                row.prop(SR, 'numbering',text='Enable Numbering')
                if SR.numbering:
                    row = col.row(align=1)
                    row.label(text='START')
                    rt = row.row()
                    rt.alignment = 'RIGHT'
                    rt.label(text='PADDING')
                    row = col.row(align=1)
                    row.prop(SR, 'number_start',text='')
                    row.prop(SR, 'number_padding',text='')
                    col.separator()
                    
            if SR.option == 'trim':
                row = col.row(align=1)
                row.prop(SR, 'trim',text='Enable Trim')
                if SR.trim:
                    row = col.row(align=1)
                    row.label(text='START')
                    rt = row.row()
                    rt.alignment = 'RIGHT'
                    rt.label(text='END')
                    row = col.row(align=1)
                    row.prop(SR, 'trim_start',text='')
                    row.prop(SR, 'trim_end',text='')
                    col.separator()
                       
            row = col.row(align=1)
            row.operator("object.renamer_clear", text='C L E A R', icon='X')
            row.operator(updateOp.bl_idname, text='UPDATE', icon='FILE_REFRESH')
                    
            row = col.row()
            row.alignment= 'CENTER'
            row.label(text="----- list objects -----")
            
            for i, obj in enumerate(context.selected_objects):
                row= col.row(align=1)
                num = row.row(align=1)
                sel = context.selected_objects
                if len(sel) <= 9:
                    num.scale_x = 0.08
                elif len(sel) <= 99:
                    num.scale_x = 0.1
                elif len(sel) > 99:
                    num.scale_x = 0.13
                    
                #num.alignment = 'CENTER'
                num.label(text='%s' % (i+1))
                sel = row.operator("object.renamer_select", text='', icon='BORDERMOVE')
                sel.ob = obj.name
                sel.type = 'obj'
                icons = 'OUTLINER_OB_' + obj.type
                row.prop(obj, 'name' ,text='', icon=icons)
                
        if context.active_object.mode == 'POSE':
            #rw = row.row()
            #rw.scale_x = 2
            #rw.prop(SR, 'del_prefix')
            #row.prop(SR, 'LR')
            #rw = row.row()
            #rw.scale_x = 0.1
            #rw.prop(SR, 'side', expand=1)
            
            row = col.row()
            row.prop(SR, 'option', expand=True)
            if SR.option == 'prefix_sufix':
                row = col.row(align=1)
                row.label(text='PREFIX | SUFIX')
                # gagal sharing variabel antar operator
                #row.operator("object.renamer_clear").clear_type= 'pre'
                row = col.row(align=1)
                #if (self.sure== 'add'):
                row.prop(SR, 'prefix',text='')
                row.prop(SR, 'sufix',text='')
                col.separator()
                
            if SR.option == 'find_replace':
                row = col.row(align=1)
                row.label(text='FIND | REPLACE')
                #if (self.sure== 'replace'):
                row = col.row(align=1)
                row.prop(SR, 'find',text='')
                row.prop(SR, 'replace',text='')
                col.separator()
                
            if SR.option == 'numbering':
                row = col.row(align=1)
                row.prop(SR, 'numbering',text='Enable Numbering')
                row.prop(SR, 'number_clean',text='Clean')
                if SR.numbering:
                    row = col.row(align=1)
                    row.label(text='START')
                    rt = row.row()
                    rt.alignment = 'RIGHT'
                    rt.label(text='PADDING')
                    row = col.row(align=1)
                    row.prop(SR, 'number_start',text='')
                    row.prop(SR, 'number_padding',text='')
                    col.separator()
                    
            if SR.option == 'trim':
                row = col.row(align=1)
                row.prop(SR, 'trim',text='Enable Trim')
                if SR.trim:
                    row = col.row(align=1)
                    row.label(text='START')
                    rt = row.row()
                    rt.alignment = 'RIGHT'
                    rt.label(text='END')
                    row = col.row(align=1)
                    row.prop(SR, 'trim_start',text='')
                    row.prop(SR, 'trim_end',text='')
                    col.separator()
                        
            row = col.row(align=1)
            row.operator("object.renamer_clear", text='C L E A R', icon='X')    
            row.operator(updateOp.bl_idname, text='UPDATE', icon='FILE_REFRESH')
            row = col.row()
            row.alignment= 'CENTER'
            row.label(text="----- list pose bones -----")
            colom = row.row(align=1)
            
            for i, pbo in enumerate(context.selected_pose_bones):
                row = col.row(align=1)
                num = row.row(align=1)
                sel = context.selected_pose_bones
                num.scale_x = 0.4
                #num.alignment = 'CENTER'
                num.label(text=str(i).zfill(3))
                sel = row.operator("object.renamer_select", text='', icon='BORDERMOVE')
                sel.ob = pbo.name
                sel.type='bone'                
                row.prop(pbo, 'name',text='',icon='BONE_DATA')
        row = col.row()
#        row.label(text='Kalo pencet update jangan pencet OK')
        
        
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}
    def check(self, context):
        return True
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width = self.dialog_width)
        if event.type in {'LEFTMOUSE'}:
            return {'FINISHED'}
        #return context.window_manager.invoke_props_dialog(self, self.dialog_width)
        return {'RUNNING_MODAL'}
#    def cancel(self, context):
#        if context.scene.SR.localview == True:
#            bpy.ops.view3d.localview()
#            context.scene.SR.localview = False
#        return  {'CANCELLED'}
    
class clearInput(bpy.types.Operator):
    ''' clear all input search replace | sufix prefix '''
    bl_idname = "object.renamer_clear"
    bl_label = "C L E A R"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        SR = context.scene.SR
        SR.prefix = ""
        SR.sufix = ""
        SR.find = ""
        SR.replace = ""
        SR.number_start = 0
        SR.number_padding = 2
        
        print(SR.prefix)
        return {'FINISHED'}

class VIEW3D_MT_renamer(bpy.types.Menu):
    bl_label = 'Sepsyan Renamer'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(renamerOp.bl_idname)
         
def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_renamer")    
    
addon_keymaps = []


def register():
    register_class(selectRenameOB)
    register_class(renamerOp)
    register_class(clearInput)
    register_class(SR_props)
    register_class(updateOp)
    #bpy.types.VIEW3D_MT_object_specials.prepend(menu_func)
    #register_module(__name__)
    
    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
            
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('object.renamer', 'R', 'PRESS', ctrl=True, shift=True)
        
        
    addon_keymaps.append((km, kmi))
    bpy.types.Scene.SR = bpy.props.PointerProperty(type=SR_props)
    #bpy.types.Scene.SR_preview = bpy.props.CollectionProperty(type=preview)


def unregister():
    unregister_class(selectRenameOB)
    unregister_class(renamerOp)
    unregister_class(clearInput)
    unregister_class(SR_props)
    unregister_class(updateOp)
    bpy.types.VIEW3D_MT_object_specials.remove(menu_func)
    #unregister_module(__name__)
    
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.SR
    
if __name__ == '__main__':
    register()

    
