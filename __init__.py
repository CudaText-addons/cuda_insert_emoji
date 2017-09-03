import os
from cudatext import *
import cudatext_cmd as cmds

DATADIR = os.path.dirname(__file__)+os.sep+'emojis'
PICSIZE = 64
ICONSIZE = 24
FORMSIZEX = 400
FORMSIZEY = 350
COLORLIST = 0xFFFFFF
COLORSEL = 0xE0A0A0

files = os.listdir(DATADIR)
files = [f[:-4] for f in files if f.endswith('.png')]
files = sorted(files)
print('Emojis found:', len(files))

img = image_proc(0, IMAGE_CREATE, value=0)


class Command:
    filter = ''

    def update_filter(self):
        dlg_proc(self.h_dlg, DLG_CTL_PROP_SET, name='filter', prop={'cap': 'Find: '+self.filter})

        global files
        for (i, item) in enumerate(files):
            if item.startswith(self.filter):
                listbox_proc(self.h_list, LISTBOX_SET_SEL, index=i)
                return


    def callback_keydown(self, id_dlg, id_ctl, data='', info=''):
        global files

        #react to text
        if (ord('A') <= id_ctl <= ord('Z')) or \
           (ord('0') <= id_ctl <= ord('9')):
            self.filter += chr(id_ctl).lower()
            self.update_filter()

        #react to BackSp
        if id_ctl==8:
            if self.filter:
                self.filter = self.filter[:-1]
                self.update_filter()

        #react to Enter
        if id_ctl==13:
            index_sel = listbox_proc(self.h_list, LISTBOX_GET_SEL)
            dlg_proc(self.h_dlg, DLG_HIDE)

            text = ':'+files[index_sel]+':'
            #insert at all carets
            ed.cmd(cmds.cCommand_TextInsert, text=text)


    def callback_listbox_drawitem(self, id_dlg, id_ctl, data='', info=''):
        global files
        global img

        id_canvas = data['canvas']
        index = data['index']
        rect = data['rect']
        index_sel = listbox_proc(self.h_list, LISTBOX_GET_SEL)

        if index==index_sel:
            back_color = COLORSEL
        else:
            back_color = COLORLIST

        canvas_proc(id_canvas, CANVAS_SET_BRUSH, color=back_color, style=BRUSH_SOLID)
        canvas_proc(id_canvas, CANVAS_RECT_FILL, x=rect[0], y=rect[1], x2=rect[2], y2=rect[3])

        canvas_proc(id_canvas, CANVAS_TEXT,
            text=files[index],
            x=rect[0] + ICONSIZE+6,
            y=rect[1] + 2 )

        image_proc(img, IMAGE_LOAD, value=DATADIR+os.sep+files[index]+'.png')
        image_proc(img, IMAGE_PAINT_SIZED, value=(id_canvas, rect[0], rect[1], rect[0]+ICONSIZE, rect[1]+ICONSIZE))


    def init_dlg(self):

        h=dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={'cap':'Insert Emoji',
          'w':FORMSIZEX,
          'h':FORMSIZEY,
          'on_key_down': self.callback_keydown,
          'keypreview': True
          })

        n=dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={'name': 'filter',
            'align': ALIGN_TOP,
            'sp_a': 6,
            'cap': '',
            })

        n=dlg_proc(h, DLG_CTL_ADD, 'listbox_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={'name': 'list1',
            'align': ALIGN_CLIENT,
            'sp_a': 6,
            'on_draw_item': self.callback_listbox_drawitem,
            })

        self.h_list = dlg_proc(h, DLG_CTL_HANDLE, index=n)

        global files
        for i in range(len(files)):
            listbox_proc(self.h_list, LISTBOX_ADD, index=-1, text='')
        listbox_proc(self.h_list, LISTBOX_SET_SEL, index=0)
        listbox_proc(self.h_list, LISTBOX_SET_ITEM_H, index=ICONSIZE)
        listbox_proc(self.h_list, LISTBOX_SET_DRAWN, index=1)

        return h


    def __init__(self):
        self.h_dlg = self.init_dlg()
        self.update_filter()

    def dialog(self):
        dlg_proc(self.h_dlg, DLG_SHOW_MODAL)
