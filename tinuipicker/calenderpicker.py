from datetime import datetime
import calendar
from tkinter.font import Font

from tinui import BasicTinUI
from tinui.TinUI import TinUIString


class TinUICalendarPicker:
    DAY_MODE_TAG = "day_mode"
    MONTH_MODE_TAG = "month_mode"

    def __init__(self, tinui:BasicTinUI, pos, font=("微软雅黑", 10), command=None, now=datetime.today(), anchor='nw', **kwargs):
        self.self = tinui
        self.scale_value = tinui.scale_value
        self.pos = pos
        self.font = Font(font=font)
        self.segoe_font = Font(family="{Segoe Fluent Icons}", size=self.font.cget("size")-2)
        self.font_width = self.font.measure('30')
        self.cell_size = self.scale_value(15) + self.font_width # 每个日期单元格的大小，考虑字体宽度
        self.month_cell_size = self.cell_size * 7 / 4 # 每个月份单元格的大小
        self.width = self.cell_size * 7 + self.scale_value(20)
        self.height = self.cell_size * 8 + self.scale_value(20) # 1行月份控制 + 1行星期 + 6行日期 + padding
        self.command = command
        self.anchor = anchor
        self.month_select_mode = False # 月份选择模式

        self.cfg = {
            "fg": kwargs.get("fg", "#1b1b1b"),
            "bg": kwargs.get("bg", "#fbfbfb"),
            "outline": kwargs.get("outline", "#ececec"),
            "activefg": kwargs.get("activefg", "#1b1b1b"),
            "activebg": kwargs.get("activebg", "#f6f6f6"),
            "onbg": kwargs.get("onbg", "#3748d9"),
            "onfg": kwargs.get("onfg", "#eaecfb"),
            "buttonfg": kwargs.get("buttonfg", "#1a1a1a"),
            "buttonbg": kwargs.get("buttonbg", "#f9f9f9"),
            "buttonactivefg": kwargs.get("buttonactivefg", "#1a1a1a"),
            "buttonactivebg": kwargs.get("buttonactivebg", "#f3f3f3"),
            "buttononfg": kwargs.get("buttononfg", "#5d5d5d"),
            "buttononbg": kwargs.get("buttononbg", "#f5f5f5"),
        }

        self.res_year, self.res_month, self.res_day = str(now.year), str(now.month).zfill(2), str(now.day).zfill(2)
        # 当前展示的年月
        self.view_year = now.year
        self.view_month = now.month

        self._build_trigger()
        self._setup_picker_ui()

    def _build_trigger(self):
        temp_text = f"{self.res_year}-{self.res_month}-{self.res_day}"
        txtest = self.self.create_text(self.pos, text=temp_text, font=self.font)
        bbox = self.self.bbox(txtest)
        self.self.delete(txtest)
        tw, th = bbox[2]-bbox[0] + 10, bbox[3]-bbox[1] + 10
        x, y = self.pos

        self.out_line = self.self.create_polygon(
            (x, y, x+tw, y, x+tw, y+th, x, y+th),
            fill=self.cfg['outline'], outline=self.cfg['outline'], width=self.self.TINUI_RADIUS_SMALL
        )
        self.back = self.self.create_polygon(
            (x+1, y+1, x+tw-1, y+1, x+tw-1, y+th-1, x+1, y+th-1),
            fill=self.cfg['bg'], outline=self.cfg['bg'], width=self.self.TINUI_RADIUS_SMALL
        )
        self.main_text = self.self.create_text(
            (x + tw/2, y + th/2), text=temp_text, fill=self.cfg['fg'], font=self.font
        )

        uid = f"calendarpicker-{id(self)}"
        self.uid = TinUIString(uid)
        for i in (self.out_line, self.back, self.main_text):
            self.self.addtag_withtag(uid, i)

        self.self.tag_bind(uid, "<Enter>", lambda _: self.self.itemconfig(self.back, fill=self.cfg['activebg'], outline=self.cfg['activebg']))
        self.self.tag_bind(uid, "<Leave>", lambda _: self.self.itemconfig(self.back, fill=self.cfg['bg'], outline=self.cfg['bg']))
        self.self.tag_bind(uid, "<Button-1>", self.show)

        self.self._BasicTinUI__auto_anchor(uid, self.pos, self.anchor)
        self.uid.layout = lambda x1, y1, x2, y2, _=False: self.self._BasicTinUI__auto_layout(
            uid, (x1, y1, x2, y2), self.anchor
        )

    def _setup_picker_ui(self):
        self.picker, self.bar = self.self._BasicTinUI__ui_toplevel(
            self.width, self.height, "#01FF11", lambda _: self.picker.withdraw()
        )
        self.picker.bind("<Escape>", lambda _: self.picker.withdraw())
        self.picker.bind("<FocusOut>", lambda _: self.picker.withdraw())

        # 绘制背景框
        self.bar._BasicTinUI__ui_polygon(((13, 13), (self.width - 13, self.height - 11)), fill=self.cfg['bg'], outline=self.cfg['bg'], width=17)
        self.bar.lower(self.bar._BasicTinUI__ui_polygon(((12, 12), (self.width - 12, self.height - 10)), fill=self.cfg['outline'], outline=self.cfg['outline'], width=17))

        # 存放当前网格元素的引用，便于刷新时清除
        self.day_elements = []
        self.month_elements = []
        self.selected_back = None

        self._build_calendar_ui()

        self.maxx = self.self.winfo_screenwidth()
        self.maxy = self.self.winfo_screenheight()

    def _build_calendar_ui(self):
        offset_x = self.scale_value(10)
        offset_y = self.scale_value(10)

        # 年月显示
        # 考虑可以使用模板字符串作为参数设置具体显示格式
        self.title_text = self.bar.add_button2((offset_x,offset_y+self.cell_size//2), minwidth=self.cell_size*4, text=f"{self.view_year}-{self.view_month}", fg=self.cfg['buttonfg'], bg=self.cfg['buttonbg'], line=self.cfg['buttonbg'], activefg=self.cfg['buttonactivefg'], activebg=self.cfg['buttonactivebg'], activeline=self.cfg['buttonactivebg'], onfg=self.cfg['buttononfg'], onbg=self.cfg['buttononbg'], online=self.cfg['buttononbg'], font=self.font, command=self._toggle_month_select, anchor='w')[0]
        self.bar.move(self.title_text, -self.cell_size*2, 0)
        self.bar.itemconfig(self.title_text, anchor='w')

        # 右上角按钮 (上一月、下一月)
        btn_y = offset_y + self.cell_size//2
        prev_btn_x = offset_x + self.cell_size * 5.5
        next_btn_x = offset_x + self.cell_size * 6.5

        self.bar.add_button2((prev_btn_x,btn_y), icon='\uF090', text='', fg=self.cfg['buttonfg'], bg=self.cfg['buttonbg'], line=self.cfg['buttonbg'], activefg=self.cfg['buttonactivefg'], activebg=self.cfg['buttonactivebg'], activeline=self.cfg['buttonactivebg'], onfg=self.cfg['buttononfg'], onbg=self.cfg['buttononbg'], online=self.cfg['buttononbg'], font=self.segoe_font, command=self._prev_month, anchor='center')
        self.bar.add_button2((next_btn_x,btn_y), icon='\uF08E', text='', fg=self.cfg['buttonfg'], bg=self.cfg['buttonbg'], line=self.cfg['buttonbg'], activefg=self.cfg['buttonactivefg'], activebg=self.cfg['buttonactivebg'], activeline=self.cfg['buttonactivebg'], onfg=self.cfg['buttononfg'], onbg=self.cfg['buttononbg'], online=self.cfg['buttononbg'], font=self.segoe_font, command=self._next_month, anchor='center')

        # 分割线
        self.bar.add_separate((offset_x, offset_y+self.cell_size+self.scale_value(2)), width=self.cell_size*7, fg=self.cfg['outline'])

        if self.month_select_mode:
            self._build_month_select_ui()
        else:
            self._build_day_select_ui()

    def _build_day_select_ui(self):
        self.bar.itemconfig(self.title_text, text=f"{self.view_year}-{self.view_month}") # 后续同样考虑可设置模板字符串

        offset_x = self.scale_value(10)
        offset_y = self.scale_value(10)

        # 星期简称栏
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        week_y = offset_y + self.cell_size + self.scale_value(5)
        for i, day in enumerate(weekdays):
            self.bar.create_text(
                (offset_x + self.cell_size * i + self.cell_size/2, week_y + self.cell_size/2),
                text=day, fill=self.cfg['fg'], font=self.font, tags=self.DAY_MODE_TAG
            )

        # 日期网格
        self.grid_start_y = week_y + self.cell_size
        self._draw_days(offset_x)

    def _toggle_month_select(self, _):
        if self.month_select_mode:
            # 不支持在月份选择模式下重新回到日期选择
            return
        self.month_select_mode = True
        self._redraw_calendar()

    def _redraw_calendar(self):
        if self.month_select_mode:
            self.bar.delete(self.DAY_MODE_TAG)
            self._build_month_select_ui()
        else:
            self.bar.delete(self.MONTH_MODE_TAG)
            self._build_day_select_ui()

    def _build_month_select_ui(self):
        self.bar.itemconfig(self.title_text, text=f"{self.view_year}") # 后续同样考虑可设置模板字符串

        offset_x = self.scale_value(10)
        offset_y = self.scale_value(10)

        # 月份网格 (3行 x 4列)
        self.month_grid_start_y = offset_y + self.cell_size * 7 / 4
        self._draw_months(offset_x)

    def _draw_months(self, offset_x):
        for elements in self.month_elements:
            for item in elements['items']:
                self.bar.delete(item)
        self.month_elements.clear()

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_radius = self.month_cell_size / 2

        for idx, month in enumerate(months):
            row = idx // 4
            col = idx % 4
            self._create_month_cell(row, col, idx + 1, month, offset_x, month_radius)

    def _create_month_cell(self, row, col, month, month_text, offset_x, month_radius):
        cx = offset_x + self.month_cell_size * col + self.month_cell_size / 2
        cy = self.month_grid_start_y + self.month_cell_size * row + self.month_cell_size / 2

        back = self.bar.create_oval(
            cx - month_radius, cy - month_radius, cx + month_radius, cy + month_radius,
            fill=self.cfg['buttonbg'], outline=self.cfg['buttonbg'], width=self.scale_value(1), tags=self.MONTH_MODE_TAG
        )
        text = self.bar.create_text((cx, cy), text=month_text, fill=self.cfg['buttonfg'], font=self.font, tags=self.MONTH_MODE_TAG)

        is_selected = (month == self.view_month)
        if is_selected:
            self.bar.itemconfig(back, fill=self.cfg['onbg'])
            self.bar.itemconfig(text, fill=self.cfg['onfg'])

        data = {'items': (back, text), 'back': back, 'text': text, 'month': month, 'is_sel': is_selected}
        for item in (back, text):
            self.bar.tag_bind(item, "<Enter>", lambda _, d=data: self._on_month_enter(d))
            self.bar.tag_bind(item, "<Leave>", lambda _, d=data: self._on_month_leave(d))
            self.bar.tag_bind(item, "<Button-1>", lambda _, d=data: self._on_month_click(d))

        self.month_elements.append(data)

    def _on_month_enter(self, data):
        if not data['is_sel']:
            self.bar.itemconfig(data['back'], fill=self.cfg['buttonactivebg'])

    def _on_month_leave(self, data):
        if not data['is_sel']:
            self.bar.itemconfig(data['back'], fill=self.cfg['buttonbg'])

    def _on_month_click(self, data):
        self.view_month = data['month']
        self.month_select_mode = False
        self._redraw_calendar()

    def _prev_year(self, _):
        self.view_year -= 1
        self._redraw_calendar()

    def _next_year(self, _):
        self.view_year += 1
        self._redraw_calendar()

    def _draw_days(self, offset_x):
        # 清除旧的日期元素
        for elements in self.day_elements:
            for item in elements['items']:
                self.bar.delete(item)
        self.day_elements.clear()
        self.selected_back = None

        # 获取当月日历信息
        cal = calendar.Calendar(firstweekday=0) # 0 = Monday
        month_days = cal.monthdayscalendar(self.view_year, self.view_month)

        row = 0
        for week in month_days:
            col = 0
            for day in week:
                if day != 0:
                    self._create_day_cell(row, col, day, offset_x)
                col += 1
            row += 1

    def _create_day_cell(self, row, col, day, offset_x):
        cx = offset_x + self.cell_size * col + self.cell_size/2
        cy = self.grid_start_y + self.cell_size * row + self.cell_size/2
        r = self.cell_size/2

        # 圆形背景
        back = self.bar.create_oval(cx - r, cy - r, cx + r, cy + r, fill=self.cfg['buttonbg'], outline=self.cfg['buttonbg'], width=self.scale_value(1), tags=self.DAY_MODE_TAG)
        # 文本
        text = self.bar.create_text((cx, cy), text=str(day), fill=self.cfg['buttonfg'], font=self.font, tags=self.DAY_MODE_TAG)

        items = (back, text)

        # 判断是否为选中状态
        is_selected = (str(day) == self.res_day and self.view_year == int(self.res_year) and self.view_month == int(self.res_month))

        if is_selected:
            self.bar.itemconfig(back, fill=self.cfg['onbg'])
            self.bar.itemconfig(text, fill=self.cfg['onfg'])
            self.selected_back = back

        # 绑定事件
        data = {'items': items, 'back': back, 'text': text, 'day': str(day), 'is_sel': is_selected}
        for item in items:
            self.bar.tag_bind(item, "<Enter>", lambda _, d=data: self._on_day_enter(d))
            self.bar.tag_bind(item, "<Leave>", lambda _, d=data: self._on_day_leave(d))
            self.bar.tag_bind(item, "<Button-1>", lambda _, d=data: self._on_day_click(d))
        self.day_elements.append(data)

    def _on_day_enter(self, data):
        if not data['is_sel']:
            self.bar.itemconfig(data['back'], fill=self.cfg['buttonactivebg'])

    def _on_day_leave(self, data):
        if not data['is_sel']:
            self.bar.itemconfig(data['back'], fill=self.cfg['buttonbg'])

    def _on_day_click(self, data):
        # 取消之前选中的状态
        if self.selected_back:
            # 找到之前选中的data
            for d in self.day_elements:
                if d['back'] == self.selected_back:
                    d['is_sel'] = False
                    self.bar.itemconfig(d['back'], fill=self.cfg['buttonbg'])
                    self.bar.itemconfig(d['text'], fill=self.cfg['buttonfg'])
                    break

        # 设置新选中状态
        data['is_sel'] = True
        self.bar.itemconfig(data['back'], fill=self.cfg['onbg'])
        self.bar.itemconfig(data['text'], fill=self.cfg['onfg'])
        self.selected_back = data['back']

        # 更新选择结果
        self.res_year = str(self.view_year)
        self.res_month = str(self.view_month).zfill(2)
        self.res_day = data['day'].zfill(2)

        self._confirm()

    def _prev_month(self, _):
        if self.month_select_mode:
            self.view_year -= 1
        else:
            if self.view_month == 1:
                self.view_year -= 1
                self.view_month = 12
            else:
                self.view_month -= 1
        self._redraw_calendar()

    def _next_month(self, _):
        if self.month_select_mode:
            self.view_year += 1
        else:
            if self.view_month == 12:
                self.view_year += 1
                self.view_month = 1
            else:
                self.view_month += 1
        self._redraw_calendar()


    def _update_title_and_days(self):
        self.bar.itemconfig(self.title_text, text=f"{self.view_year}-{self.view_month}") # 后续同样考虑可设置模板字符串
        self._draw_days(self.scale_value(10))

    def show(self, event):
        # 计算显示位置
        bbox = self.self.bbox(self.out_line)
        sx, sy = event.x_root - (event.x - bbox[0]), event.y_root - (event.y - bbox[3])

        if sx + self.width > self.maxx:
            sx = self.maxx - self.width
        if sy + self.height > self.maxy:
            sy = self.maxy - self.height

        self.picker.geometry(f"{int(self.width)}x{int(self.height)}+{int(sx)-3}+{int(sy)}")
        self.picker.attributes("-alpha", 0)
        self.picker.deiconify()
        self.picker.focus_set()

        for i in range(1, 11):
            self.picker.after(i*20, lambda a=i/10: self.picker.attributes("-alpha", a))

    def _confirm(self):
        full_date = f"{self.res_year}-{self.res_month}-{self.res_day}"
        self.self.itemconfig(self.main_text, text=full_date)
        if self.command:
            self.command(full_date)
        self.picker.withdraw()

    def set_date(self, year:int, month:int, day:int):
        self.res_year = str(year)
        self.res_month = str(month).zfill(2)
        self.res_day = str(day).zfill(2)
        self.view_year = year
        self.view_month = month

        full_date = f"{self.res_year}-{self.res_month}-{self.res_day}"
        self.self.itemconfig(self.main_text, text=full_date)
        if hasattr(self, 'title_text'):
            self._redraw_calendar()


if __name__ == "__main__":
    from tkinter import Tk
    from tinui import ExpandPanel, HorizonPanel
    # import ctypes
    # ctypes.windll.shcore.SetProcessDpiAwareness(2) # 高DPI适配
    # scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    root = Tk()
    root.geometry('400x400')

    ui = BasicTinUI(root)
    # ui.set_scale(scale_factor)
    ui.pack(fill='both', expand=True)

    tdp = TinUICalendarPicker(ui, (10,10), font=("微软雅黑", 12), command=print, anchor='center')

    rp = ExpandPanel(ui)
    hp = HorizonPanel(ui)
    rp.set_child(hp)
    hp.add_child(tdp.uid, 150)

    ep = ExpandPanel(ui)
    hp.add_child(ep, weight=1)
    # ep.set_child(tdp.uid)

    def update(e):
        rp.update_layout(5,5,e.width-5,e.height-5)
    ui.bind('<Configure>',update)

    root.mainloop()
