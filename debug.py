import main
import tkinter
import tkinter.messagebox
import tkinter.filedialog

mode = '自动' #自动，手动
stop_place = []
run_flag = False

def about_ui(*temp):
    about_page = tkinter.Toplevel(ui_page)
    about_page.geometry('300x100')
    about_page.title('关于')

    about_text = tkinter.Text(about_page)
    about_text.pack()

    about_text.configure(state='normal')
    about_text.delete('1.0',tkinter.END)
    about_text.insert(tkinter.END,'CRP调试器 v.1.4\nby dzknb\n\n提示：双击代码可以设置断点')
    about_text.configure(state='disabled')

def open_file(*temp):
    file_path = tkinter.filedialog.askopenfilename(title="打开文件",filetypes=[("CRP语言文件", "*.crp"),("文本文件","*.txt"),("所有文件", "*.*")])
    try:
        f = open(file_path,'r',encoding='utf-8')
        file_code = f.read().split('\n')
        ui_text_run.delete('1.0',tkinter.END)
        for i in file_code:
            ui_text_run.insert('end',str(i)+'\n')
    except:
        tkinter.messagebox.showerror('打开','文件读取失败')

def set_stop(event):
    line = int(float(event.widget.index("current")))
    stop_place.append(line)
    ui_text_run.tag_add("stopplace", f"{line}.0", f"{line}.end")

def updata(*temp):
    ui_flag_entry.configure(state='normal')
    ui_flag_entry_data = f" Line: {str(main.run_index + 1):<10}Mode: {mode:<10}"
    ui_flag_entry.delete('0',tkinter.END)
    ui_flag_entry.insert(tkinter.END,ui_flag_entry_data)
    ui_flag_entry.configure(state='readonly')

    ui_text.see(tkinter.END)

    goto_list_entry.configure(state='normal')
    goto_list_entry.delete('0',tkinter.END)
    for last_got_data in main.last_label:

        goto_list_entry.insert(tkinter.END,str(last_got_data + 1) + ' ')
    goto_list_entry.configure(state='readonly')

def updata_click(*temp):
    
    line = int(float(ui_text_run.index("current")))

    ui_flag_entry.configure(state='normal')
    ui_flag_entry_data = f" Line: {str(line):<10}Mode: {str(mode):<4}"
    ui_flag_entry.delete('0',tkinter.END)
    ui_flag_entry.insert(tkinter.END,ui_flag_entry_data)
    ui_text.see(tkinter.END)

    ui_flag_entry.configure(state='readonly')

def debug_hook_nextline(data):
    ui_page.update() #刷新ui界面
    if run_flag == False: #识别退出
        raise RuntimeError
    main.run_index += 1

def force_exit_run(*temp):#强行退出运行
    global run_flag

    ui_text.configure(state='normal')
    if run_flag == True:
        ui_text.insert(tkinter.END,'\n用户强制退出\n')
        run_flag = False

    ui_text.configure(state='disabled')

def debug_hook_return(message, data=''):
    global run_flag

    ui_text.configure(state='normal')
    if message == 'first run end':
        ui_text.insert(tkinter.END,'\n预加载完成\n')
        for line in data: #预处理后代码显示
            ui_text_run.insert(tkinter.END,(line+'\n'))
        for stop_line in stop_place: #添加断点标签
            
            ui_text_run.tag_add("stopplace", f"{stop_line}.0", f"{stop_line}.end")
        
    elif message == 'end':
        run_flag = False

    elif message == 'error':
        ui_text.insert(tkinter.END,'\n发生错误\n')
        tkinter.messagebox.showerror('运行错误',data)
        run_flag = False
        raise RuntimeError     

    elif message == 'flag_error':
        ui_text.insert(tkinter.END,'跳转到错误处理标签\n')
    
    ui_text.configure(state='disabled')

def debug_hook_runline(command, command_data):
    global run_flag

    ui_text_run.tag_remove("highlight",'1.0',tkinter.END)
    ui_text_run.tag_add("highlight", f"{main.run_index + 1}.0", f"{main.run_index + 1}.end")
    ui_text_run.see(float(main.run_index))

    ui_text_value.configure(state='normal')
    ui_text_value.delete('1.0',tkinter.END)
    updata()
    
    for data_key in command_data:
        if str(data_key) in main.value.keys(): #参数是变量
            ui_text_value.insert(tkinter.END,str(data_key)+':\n')
            ui_text_value.insert(tkinter.END,'  '+str(main.value[data_key])+'\n')
        elif str(data_key) == '':#空
            pass
        elif str(data_key)[0] == '_':
            ui_text_value.insert(tkinter.END,str(data_key)+':\n')
            ui_text_value.insert(tkinter.END,'  不存在\n')

    ui_text_value.configure(state='disabled')

    if mode == '自动':
        if (main.run_index + 1) in stop_place:
            
            if not tkinter.messagebox.askokcancel('自动运行','继续运行？'):
                raise RuntimeError
    else:
        
        if not tkinter.messagebox.askokcancel('手动运行','继续运行？'):
            raise RuntimeError

main.debug_flag = True
main.debug_hook = [debug_hook_return, debug_hook_runline, debug_hook_nextline]

def debug_print(data,end=''):
    ui_text.configure(state='normal')
    ui_text.insert(tkinter.END,str(data) + str(end))
    ui_text.configure(state='disabled')

input_data = ''
def debug_input(data=''):
    def get_input():
        global input_data

        input_data = input_entry.get()
        input_page.destroy()

    debug_print(data)
    input_page = tkinter.Toplevel(ui_page)
    input_page.title('输入')
    input_page.geometry('250x100')

    input_label = tkinter.Label(input_page,text='输入内容')
    input_label.pack()

    input_entry = tkinter.Entry(input_page)
    input_entry.pack()

    input_button = tkinter.Button(input_page,text='确定',command=get_input)
    input_button.pack()

    ui_page.wait_window(input_page)
    
    return input_data

#重定义输入/输出
main.print = debug_print
main.input = debug_input

def run(*temp):
    global stop_place,ui_text_run,run_flag

    ui_text.configure(state='normal')
    ui_text.delete('1.0',tkinter.END)
    main.value = {'_None':['Type:None',''],'_Error':['Type:String','']} #[<type>,<value>]
    main.last_label = [0] #上一次的got位置
    main.error_label = ''
    main.error_flag = False
    main.include_pack = ['']
    main.label = {'~start':0}
    main.run_index=0

    code_notadd = ui_text_run.get('1.0',tkinter.END)
    code_notadd = code_notadd.rstrip('\n') #删除末尾多的一行
    ui_text_run.delete('1.0',tkinter.END)
    
    run_flag = True

    ui_text.insert(tkinter.END,'开始执行\n')

    try:
        main.run(code=code_notadd)
    except RuntimeError:
        pass

    ui_text.configure(state='normal')
    ui_text.insert(tkinter.END,'\n运行结束\n')
    
    run_flag = False
    ui_text_run.delete('1.0',tkinter.END)
    ui_text.configure(state='disabled')

    stop_place = []

    ui_text_run.tag_remove('stopplace','1.0',tkinter.END)
    ui_text_run.tag_remove('hightlight','1.0',tkinter.END)

    ui_text_run.insert(tkinter.END,code_notadd) #有bug,f5自己会加行

def turn_mode(*temp):
    global mode
    if mode == '自动':
        mode = '手动'
    else:
        mode = '自动'

    updata_click()

jump_data = 0
def jump_line(*temp):
    def get_jump(*temp):
        global jump_data

        jump_data = jump_entry.get()
        jump_line_page.destroy()

    jump_line_page = tkinter.Toplevel()
    jump_line_page.title('跳转')
    jump_line_page.geometry('250x100')
        
    jump_line_label = tkinter.Label(jump_line_page,text='输入跳转行数')
    jump_line_label.pack()

    jump_entry = tkinter.Entry(jump_line_page)
    jump_entry.pack()

    jump_button = tkinter.Button(jump_line_page,text='确定',command=get_jump)
    jump_button.pack()

    ui_page.wait_window(jump_line_page)
    ui_text_run.see(float(int(jump_data)))    

def new_file(*temp):
    ui_text_run.delete('1.0',tkinter.END)
    ui_text.delete('1.0',tkinter.END)
    goto_list_entry.delete('0',tkinter.END)

ui_page = tkinter.Tk()
ui_page.title('crp 编辑器')
ui_page.geometry('830x515')

ui_menu_bar = tkinter.Menu(ui_page)

ui_file_menu = tkinter.Menu(ui_page,tearoff=False)
ui_file_menu.add_command(label='新建',command = new_file)
ui_file_menu.add_command(label='打开',command=open_file)
ui_file_menu.add_command(label='保存')

ui_menu_bar.add_cascade(label='文件',menu=ui_file_menu)

code_debug_bar = tkinter.Menu(ui_page,tearoff=False)
code_debug_bar.add_command(label='查找')
code_debug_bar.add_command(label='跳转',command=jump_line)

ui_debug_menu = tkinter.Menu(ui_page,tearoff=False)
ui_debug_menu.add_command(label='开始运行[F5]',command=run)
ui_debug_menu.add_command(label='强制停止[F4]',command=force_exit_run)
ui_debug_menu.add_command(label='模式切换[F12]',command=turn_mode)

ui_menu_bar.add_cascade(label='编辑',menu=code_debug_bar)
ui_menu_bar.add_cascade(label='调试',menu=ui_debug_menu)
ui_menu_bar.add_command(label='关于',command=about_ui)

ui_page.config(menu=ui_menu_bar)

ui_label1 = tkinter.Label(ui_page, text='信息')
ui_label1.place(x=510, y=300)

ui_text = tkinter.Text(ui_page, width=30,height=8)
ui_text.place(x=510, y=325)

ui_text_run = tkinter.Text(ui_page, width=50,height=23)
ui_text_run.place(x=3, y=0)
ui_text_run.tag_configure("highlight", background="yellow", foreground="black")
ui_text_run.tag_configure("stopplace", background="blue", foreground="white")
ui_text_run.tag_raise("stopplace")
ui_text_run.tag_raise("highlight")

ui_text_value = tkinter.Text(ui_page,height=6,width=30)
ui_text_value.place(x=510,y=0)

ui_flag_entry = tkinter.Entry(ui_page)
ui_flag_entry.pack(side=tkinter.BOTTOM,fill=tkinter.X)

goto_list_label = tkinter.Label(ui_page,text='跳转记录')
goto_list_label.place(x=510,y=145)

goto_list_entry = tkinter.Entry(ui_page,width=30)
goto_list_entry.place(x=510,y=170)

scrollbar = tkinter.Scrollbar(ui_page,command=ui_text_run.yview)
scrollbar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
ui_text_run.config(yscrollcommand = scrollbar.set)

ui_text_run.bind("<Double-Button-1>",set_stop)
ui_text_run.bind("<Button-1>",updata_click)
ui_text_run.bind("<F12>",turn_mode)

#临时
code =\
"""
;测试代码，可以删除
imp *math
mov _math_abs_argu '-1'
got ~math_abs
cal _None #out _math_abs_return
"""
for line in code.split('\n'):
    ui_text_run.insert(tkinter.END,(line+'\n'))


ui_text_run.bind("<F5>",run)
ui_text_run.bind("<F4>",force_exit_run)


tkinter.mainloop()