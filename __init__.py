import os
from cudatext import *
import cudatext_cmd as cmds

DATADIR = os.path.dirname(__file__)+os.sep+'emojis'
ICONSIZE = 32 #original: 64x64
FORMSIZEX = 300
FORMSIZEY = 400
COLORLIST = 0xFFFFFF
COLORSEL = 0xE0A0A0

files = os.listdir(DATADIR)
files = [f[:-4] for f in files if f.endswith('.png')]
files = sorted(files)
print('Emojis found:', len(files))

img = image_proc(0, IMAGE_CREATE, value=0)

def unicode_(self, file_):
    try:
        f = open(os.path.dirname(os.path.realpath(__file__)) + '/' + file_)
    except OSError as err:
        msg_box("OS error: {0}".format(err), MB_OK)
        raise
    
    import json
    data_ = json.load(f)
    list_ = ''
    emojis_ = []
    for i in data_:
        code_ = ' (' + i['code'] + ')' if i['code'] != '' else ''
        keywords_ = "\t" + i['keywords'] if i['keywords'] != '' else ''
        list_ = list_ + i['emoji'] + ' ' + i['name'] + code_ + keywords_ + "\n"
        emojis_.append(i['emoji'])
    f.close()
    
    res_ = dlg_menu(DMENU_LIST_ALT, list_, 0, 'List of emojis', CLIP_RIGHT)
    
    import cudatext_cmd as cmds
    ed.cmd(cmds.cCommand_TextInsert, text=str(emojis_[res_]))

class Command:
    filter = ''

    def update_filter(self):
        global files
        dlg_proc(self.h_dlg, DLG_CTL_PROP_SET, name='filter', prop={'cap': 'Filter: '+self.filter})

        listbox_proc(self.h_list, LISTBOX_DELETE_ALL)

        for (i, item) in enumerate(files):
            if self.filter in item:
                listbox_proc(self.h_list, LISTBOX_ADD, index=-1, text=item)

        listbox_proc(self.h_list, LISTBOX_SET_TOP, index=0)
        listbox_proc(self.h_list, LISTBOX_SET_SEL, index=0)


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
            item = listbox_proc(self.h_list, LISTBOX_GET_ITEM, index=index_sel)
            if not item: return
            item_text = item[0]

            dlg_proc(self.h_dlg, DLG_HIDE)

            text = ':'+item_text+':'
            #insert at all carets
            ed.cmd(cmds.cCommand_TextInsert, text=text)


    def callback_listbox_drawitem(self, id_dlg, id_ctl, data='', info=''):
        global files
        global img

        id_canvas = data['canvas']
        index = data['index']
        rect = data['rect']
        index_sel = listbox_proc(self.h_list, LISTBOX_GET_SEL)
        item_text = listbox_proc(self.h_list, LISTBOX_GET_ITEM, index=index)[0]

        if index==index_sel:
            back_color = COLORSEL
        else:
            back_color = COLORLIST

        canvas_proc(id_canvas, CANVAS_SET_BRUSH, color=back_color, style=BRUSH_SOLID)
        canvas_proc(id_canvas, CANVAS_RECT_FILL, x=rect[0], y=rect[1], x2=rect[2], y2=rect[3])

        size = canvas_proc(id_canvas, CANVAS_GET_TEXT_SIZE, text=item_text)
        canvas_proc(id_canvas, CANVAS_TEXT,
            text = item_text,
            x = rect[0] + ICONSIZE+6,
            y = (rect[1]+rect[3]-size[1])//2 )

        image_proc(img, IMAGE_LOAD, value=DATADIR+os.sep+item_text+'.png')
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
        dlg_proc(h, DLG_CTL_FOCUS, index=n)

        listbox_proc(self.h_list, LISTBOX_SET_ITEM_H, index=ICONSIZE)
        listbox_proc(self.h_list, LISTBOX_SET_DRAWN, index=1)

        return h


    def __init__(self):
        self.h_dlg = self.init_dlg()
        self.update_filter()

    def dialog(self):
        dlg_proc(self.h_dlg, DLG_SHOW_MODAL)

    def unicode_en(self):
        unicode_(self, 'data_en.json')
    
    def unicode_ru(self):
        unicode_(self, 'data_ru.json')
