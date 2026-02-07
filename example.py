from datetime import datetime
from tkinter import Tk

from tinui import BasicTinUI, ExpandPanel, HorizonPanel
from tinuipicker.datepicker import TinUIDatePicker
from tinuipicker.timepicker import TinUITimePicker
from tinuipicker import pickerlight, pickerdark

root = Tk()
root.geometry('400x400')

ui = BasicTinUI(root)
ui.pack(fill='both', expand=True)

tdp = TinUIDatePicker(ui, (10,10), font=("Segoe UI", 12), now=datetime(2026, 2, 19), command=print, anchor='center', **pickerlight)
tdp.set_date(2016, 10)

ttp = TinUITimePicker(ui, (10,10), font=("Segoe UI", 12), is_24h=False, show_sec=False, now=datetime(1,1,1,6,23,45), command=print, anchor='center', **pickerdark)
ttp.set_time(16,0,19)

rp = ExpandPanel(ui)
hp = HorizonPanel(ui)
rp.set_child(hp)

ep = ExpandPanel(ui, bg='#f3f3f3')
hp.add_child(ep, weight=1)
ep.set_child(tdp.uid)

ep2 = ExpandPanel(ui, bg='#202020')
hp.add_child(ep2, weight=1)
ep2.set_child(ttp.uid)

def update(e):
    rp.update_layout(5,5,e.width-5,e.height-5)
ui.bind('<Configure>',update)

root.mainloop()