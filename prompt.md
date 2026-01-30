```python
def add_picker(
        self,
        pos: tuple,
        height=250,
        fg="#1b1b1b",
        bg="#fbfbfb",
        outline="#ececec",
        activefg="#1b1b1b",
        activebg="#f6f6f6",
        onfg="#eaecfb",
        onbg="#3748d9",
        buttonfg="#1a1a1a",
        buttonbg="#f9f9f9",
        buttonactivefg="#1a1a1a",
        buttonactivebg="#f3f3f3",
        buttononfg="#5d5d5d",
        buttononbg="#f5f5f5",
        font=("微软雅黑", 10),
        text=(
            ("year", 60),
            ("season", 100),
        ),
        data=(("2022", "2023", "2024"), ("spring", "summer", "autumn", "winter")),
        tran="#01FF11",
        anchor="nw",
        command=None,
    ):  # 绘制滚动选值框
    def _mouseenter(event):
        self.itemconfig(back, fill=activebg, outline=activebg)
        for i in texts:
            self.itemconfig(i, fill=activefg)

    def _mouseleave(event):
        self.itemconfig(back, fill=bg, outline=bg)
        for i in texts:
            self.itemconfig(i, fill=fg)

    def set_it(e):  # 确定选择
        results = []  # 结果列表
        for ipicker in pickerbars:
            num = pickerbars.index(ipicker)
            if ipicker.newres == "":  # 没有选择
                picker.withdraw()
                return
            ipicker.res = ipicker.newres
            tx = texts[num]
            self.itemconfig(tx, text=ipicker.res)
            results.append(ipicker.res)
        picker.withdraw()
        if command != None:
            command(results)

    def cancel(e):  # 取消选择
        for ipicker in pickerbars:
            if ipicker.res == "":
                pass
        picker.withdraw()
        # 以后或许回考虑元素选择复原，也不一定，或许不更改交互选项更方便

    def pick_in_mouse(e, t):
        box = e.widget
        if box.choices[t][-1] == True:  # 已被选中
            return
        box.itemconfig(box.choices[t][2], fill=buttonactivebg)
        box.itemconfig(box.choices[t][1], fill=activefg)

    def pick_out_mouse(e, t):
        box = e.widget
        if box.choices[t][-1] == True:  # 已被选中
            box.itemconfig(box.choices[t][2], fill=onbg)
            box.itemconfig(box.choices[t][1], fill=onfg)
        else:
            box.itemconfig(box.choices[t][2], fill=bg)
            box.itemconfig(box.choices[t][1], fill=fg)

    def pick_sel_it(e, t):
        box = e.widget
        box.itemconfig(box.choices[t][2], fill=onbg)
        box.itemconfig(box.choices[t][1], fill=onfg)
        box.choices[t][-1] = True
        for i in box.choices.keys():
            if i == t:
                continue
            box.choices[i][-1] = False
            pick_out_mouse(e, i)
        box.newres = box.choices[t][0]

    def readyshow():  # 计算显示位置
        allpos = bar.bbox("all")
        # 菜单尺寸
        winw = allpos[2] - allpos[0] + 5
        winh = allpos[3] - allpos[1] + 5
        # 屏幕尺寸
        maxx = self.winfo_screenwidth()
        maxy = self.winfo_screenheight()
        wind.data = (maxx, maxy, winw, winh)

    def show(event):  # 显示的起始位置
        # 初始位置
        maxx, maxy, winw, winh = wind.data
        bbox = self.bbox(uid)
        scx, scy = event.x_root, event.y_root  # 屏幕坐标
        dx, dy = (
            round(
                self.canvasx(
                    event.x,
                )
                - bbox[0]
            ),
            round(self.canvasy(event.y) - bbox[3]),
        )  # 画布坐标差值
        sx, sy = scx - dx, scy - dy
        if sx + winw > maxx:
            x = sx - winw
        else:
            x = sx
        if sy + winh > maxy:
            y = sy - winh
        else:
            y = sy
        picker.geometry(f"{winw + 15}x{winh + 15}+{x - 3}+{y}")
        picker.attributes("-alpha", 0)
        picker.deiconify()
        it = 0
        for i in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1):
            picker.after(it * 20, lambda alpha=i: __show(alpha))
            it += 1

    def unshow(event):
        picker.withdraw()

    def __show(alpha):
        picker.attributes("-alpha", alpha)
        picker.update_idletasks()
        if alpha == 1:
            picker.focus_set()

    def _loaddata(box, items, mw):
        def __set_y_view(event):
            box.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # mw: 元素宽度
        for i in items:
            end = box.bbox("all")
            end = 5 if end == None else end[-1]
            text = box.create_text(
                (5, end + 7),
                text=i,
                fill=fg,
                font=font,
                anchor="nw",
                tags="textcid",
            )
            bbox = box.bbox(text)  # 获取文本宽度
            back = box.create_rectangle(
                (3, bbox[1] - 4, 3 + mw, bbox[3] + 4), width=0, fill=bg
            )
            box.tkraise(text)
            box.choices[text] = [
                i,
                text,
                back,
                False,
            ]  # 用文本id代表键，避免选项文本重复带来的逻辑错误
            for item_id in (text, back):
                box.tag_bind(
                    item_id,
                    "<Enter>",
                    lambda event, text=text: pick_in_mouse(event, text),
                )
                box.tag_bind(
                    item_id,
                    "<Leave>",
                    lambda event, text=text: pick_out_mouse(event, text),
                )
                box.tag_bind(
                    item_id,
                    "<Button-1>",
                    lambda event, text=text: pick_sel_it(event, text),
                )
        bbox = box.bbox("all")
        box.config(scrollregion=bbox)
        box.bind("<MouseWheel>", __set_y_view)

    out_line = self.create_polygon(
        (*pos, *pos), fill=outline, outline=outline, width=9
    )
    uid = TinUIString(f"picker-{out_line}")
    self.addtag_withtag(uid, out_line)
    back = self.create_polygon((*pos, *pos), fill=bg, outline=bg, width=9, tags=uid)
    end_x = pos[0] + 9
    y = pos[1] + 9
    texts = []  # 文本元素
    # 测试文本高度
    txtest = self.create_text(pos, text=text[0][0], fill=fg, font=font)
    bbox = self.bbox(txtest)
    self.delete(txtest)
    uidheight = bbox[3] - bbox[1]
    uidcontent = f"{uid}content"
    for i in text:
        t, w = i  # 文本，宽度
        tx = self.create_text(
            (end_x, y),
            anchor="w",
            text=t,
            fill=fg,
            font=font,
            tags=(uid, uidcontent),
        )
        texts.append(tx)
        end_x += w
        if text.index(i) + 1 == len(text):  # 最后一个省略分隔符
            _outline = outline
            outline = ""
        self.create_line(
            (end_x - 3, pos[1], end_x - 3, pos[1] + uidheight),
            fill=outline,
            tags=(uid, uidcontent),
        )
    outline = _outline
    del _outline
    width = end_x - pos[0] + 9  # 窗口宽度
    cds = self.bbox(uidcontent)
    coords = (cds[0], cds[1], cds[2], cds[1], cds[2], cds[3], cds[0], cds[3])
    self.coords(out_line, coords)
    coords = (
        cds[0] + 1,
        cds[1] + 1,
        cds[2] - 1,
        cds[1] + 1,
        cds[2] - 1,
        cds[3] - 1,
        cds[0] + 1,
        cds[3] - 1,
    )
    self.coords(back, coords)
    self.tag_bind(uid, "<Enter>", _mouseenter)
    self.tag_bind(uid, "<Leave>", _mouseleave)
    self.tag_bind(uid, "<Button-1>", show)
    wind = TinUINum()  # 记录数据
    picker, bar = self.__ui_toplevel(width, height, tran, unshow)
    bar.__ui_polygon(
        ((13, 13), (width - 13, height - 11)), fill=bg, outline=bg, width=17
    )
    bar.lower(
        bar.__ui_polygon(
            ((12, 12), (width - 12, height - 10)),
            fill=outline,
            outline=outline,
            width=17,
        )
    )
    __count = 0
    end_x = 8
    y = 9
    pickerbars = []  # 选择UI列表
    for i in data:
        barw = text[__count][1]  # 本选择列表元素宽度
        pickbar = BasicTinUI(picker, bg=bg)
        pickbar.place(x=end_x, y=y, width=barw, height=height - 50)
        pickbar.newres = ""  # 待选
        pickbar.res = ""  # 选择结果
        # pickbar.all_keys=[]#[a-id,b-id,...]
        pickbar.choices = {}  #'a-id':[a,a_text,a_back,is_sel:bool]
        _loaddata(pickbar, i, barw)
        pickerbars.append(pickbar)
        __count += 1
        end_x += barw + 3
    # ok button
    okpos = ((5 + (width - 9) / 2) / 2, height - 22)
    ok = bar.add_button2(
        okpos,
        text="\ue73e",
        font="{Segoe Fluent Icons} 12",
        fg=buttonfg,
        bg=buttonbg,
        line="",
        activefg=buttonactivefg,
        activebg=buttonactivebg,
        activeline=outline,
        onfg=buttononfg,
        onbg=buttononbg,
        online=buttononbg,
        anchor="center",
        command=set_it,
    )
    bar.coords(
        ok[1],
        (
            9,
            height - 35,
            (width - 9) / 2 - 5,
            height - 35,
            (width - 9) / 2 - 5,
            height - 9,
            9,
            height - 9,
        ),
    )
    bar.coords(
        ok[2],
        (
            8,
            height - 34,
            (width - 9) / 2 - 4,
            height - 34,
            (width - 9) / 2 - 4,
            height - 8,
            8,
            height - 8,
        ),
    )
    # cancel button
    nopos = (((width - 9) / 2 + width - 4) / 2, height - 22)
    no = bar.add_button2(
        nopos,
        text="\ue711",
        font="{Segoe Fluent Icons} 12",
        fg=buttonfg,
        bg=buttonbg,
        line="",
        activefg=buttonactivefg,
        activebg=buttonactivebg,
        activeline=outline,
        onfg=buttononfg,
        onbg=buttononbg,
        online=buttononbg,
        anchor="center",
        command=cancel,
    )
    bar.coords(
        no[1],
        (
            (width - 9) / 2 + 5,
            height - 35,
            width - 9,
            height - 35,
            width - 9,
            height - 9,
            (width - 9) / 2 + 5,
            height - 9,
        ),
    )
    bar.coords(
        no[2],
        (
            (width - 9) / 2 + 4,
            height - 34,
            width - 8,
            height - 34,
            width - 8,
            height - 8,
            ((width - 9) / 2 + 4, height - 8),
        ),
    )
    readyshow()
    del end_x, y, coords, __count, okpos, nopos
    self.__auto_anchor(uid, pos, anchor)
    uid.layout = lambda x1, y1, x2, y2, expand=False: self.__auto_layout(
        uid, (x1, y1, x2, y2), anchor
    )
    return picker, bar, texts, pickerbars, uid
```

