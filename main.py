value = {'_None':['Type:None',''],'_Error':['Type:String','']} #[<type>,<value>]
last_label = [0] #上一次的got位置
error_label = ''
include_pack = ['']
error_flag = False

label = {'~start':0}

#代码编写区↓
code =\
'''
imp *gui
mov _gui_new_name "text1"
got ~gui_new

mov _gui_new_name "text2"
mov _gui_new_size "800x200"
got ~gui_new

got ~gui_mainloop
cal _None #out "^nend"
'''
#转义符 ^n:换行 ^s:空格 ^d:分隔

class translatr: #处理转译
    @staticmethod #可要可不要，目的省去self（python自动省去）
    def to_in(data):
        return str(data).replace(' ','^s').replace(';','^d')
    
    @staticmethod#可要可不要，目的省去self（python自动省去）
    def to_out(data):
        return str(data).replace('^s',' ').replace('^d',';').replace('^n','\n')

def end():#输出调试信息

    print('\n-----------------')
    print(label)
    print(value)
    print(last_label)

def run(code):
    global run_index
    global error_flag
    global error_label

    run_index = 0
    data = code.split('\n')

    def load_pack(name):
        try:
            with open('./pack/' + str(name)[1:] + '.imp','r',encoding='utf-8') as pack:
                return pack.readlines()

        except:
            return 'Error'

    def run_error(message):
        global run_index

        if error_flag == True: #开启err
            run_index = error_label
            value['_Error'][1] = '"' +str(message) +'"'
            return
        else:
            print('Error: ' + str(message) + '[' + str(run_index) + ']')
            end()
            exit()
            #print(data[run_index])
            #exit()
        
    def return_type(data):
        if str(data) == '':
            return 'Type:None'
        else:
            if str(data)[0] == '_':
                return 'Type:Value'
            elif str(data)[0] == '{' and str(data)[-1] == '}':
                return 'Type:List'
            elif str(data)[0] == "'" and str(data)[-1] == "'":
                return 'Type:Int'
            elif str(data)[0] == '"' and str(data)[-1] == '"':
                return 'Type:String'
            elif str(data)[0] == '<' and str(data)[-1] == '>':
                return 'Type:Float'
            elif str(data)[0] == '~':
                return 'Type:Label'
            elif str(data)[0] == '*':
                return 'Type:Pack'
            else:
                return 'Type:Unkown'
        

    #预处理new,label,imp
    before_run_line = -1

    while True:
        #print(code)
        before_run_line += 1
        
        if not before_run_line < len(code.split('\n')):
            break
    
        line = code.split('\n')[before_run_line]
        if line == '':
            continue
        elif line[0] == ';':
            continue

        command = line.split(' ')[0]
        
        if return_type(command) == 'Type:Label':#<label>
            label_name = command[0:]
            label[label_name] = before_run_line
        
        elif command == 'new': #new <1> <2> ...
            if len(line) == 1:
                run_error('new fomat')
                continue
            else:
                
                for create_value in line.split(' ')[1:]:
                    
                    if return_type(create_value) != 'Type:Value':
                        run_error('new not value')
                        continue
                    else:
                        if create_value in value.keys():
                            run_error('new value exist')
                            continue
                        else:
                            value[create_value] = ['Type:None','']
        
        elif command == 'imp':#imp <包>
            if len(line) == 1:
                run_error('imp format')
                continue
            else:
                for imp_pack in line.split(' ')[1:]:
                    imp_pack_name = ''
                    if return_type(imp_pack) == 'Type:Value':#<包>为值
                        if return_type(value[imp_pack]) == 'Type:Pack':
                            imp_pack_name = value[imp_pack]
                        else:
                            run_error('imp value not pack')
                            continue
                    else:
                        if return_type(imp_pack) == 'Type:Pack':
                            imp_pack_name = imp_pack
                        else:
                            run_error('imp value not pack')
                            continue
                    
                    if imp_pack_name in include_pack:#已经导入包
                        pass
                    else:
                        return_load = load_pack(imp_pack_name)
                        if return_load == 'Error':
                            run_error('imp load')
                            
                        else:
                            for pack_line in return_load[1:]:
                                code += pack_line
                        include_pack.append(imp_pack_name)
                    
                 
        #before_run_line += 1

    run_index = 0
    error_flag = False
    code = code.split('\n')

    while run_index < len(code):

        #print(run_index)

        line = code[run_index]
        command = line.split(' ',1)[0]
        command_data = line.split(' ')[1:]

        if line == '' or (line[0] in [';','~','\n']) or (command in ['new','imp']):#跳过执行
            run_index += 1
            continue
        
        if command == 'mov': #mov <变量> <值>
            if len(command_data) != 2:
                run_error('mov format')
                continue
            else:
                if return_type(command_data[0]) == 'Type:Value': #判断变量
                    if not command_data[0] in value.keys():
                        run_error('mov value not exist')
                        continue
                    else:

                        if return_type(command_data[1]) == 'Type:Value': #<值>为变量
                            if not command_data[1] in value.keys():
                                run_error('mov value not exist')
                                continue
                            else:
                                value[command_data[0]] = value[command_data[1]]
                        else:
                            value[command_data[0]][0] = return_type(command_data[1])
                            value[command_data[0]][1] = command_data[1]
                

                else:
                    run_error('mov not value')
                    continue

        elif command == 'typ': #typ <类型> <变量> ;int str list float
            if len(command_data) != 2:
                run_error('type format')
                continue
            else:
                if return_type(command_data[1]) != 'Type:Value':
                    run_error('typ value not value')
                    continue

                else:
                    if not command_data[1] in value.keys():
                        run_error('typ value not exist')
                        continue
                    else:
                        if command_data[0] == 'Type:String':
                            value[command_data[1]][1] = '"' + str(value[command_data[1]][1])[1:-1] +'"'
                            value[command_data[1]][0] = 'Type:String'

                        elif command_data[0] == 'Type:Int':
                            str_to_int = 0
                            try:
                                str_to_int = int(str(value[command_data[1]][1])[1:-1])
                            except:
                                run_error('typ can not to int')
                                continue
                            else:
                                value[command_data[1]][1] = "'" + str(str_to_int) + "'"
                                value[command_data[1]][0] = 'Type:Int'

                        elif command_data[0] == 'Type:List':
                            to_list_data = ['Type:List','{']
                         

                            for list_data in str(value[command_data[1]][1]).split(';'):

                                to_list_data[1] += str(list_data) + ';'
                            
                            to_list_data[1] = str(to_list_data[1])[0:-1] #去除结尾的;
                            to_list_data[1] += '}' #添加list结尾
                            
                            value[command_data[1]] = to_list_data

                        elif command_data[0] == 'Type:Float':
                            to_float_data = ''

                            if value[command_data[1]][0] == 'Type:String' or value[command_data[1]][0] == 'Type:Int':
                                try:
                                    to_float_data = float(str(value[command_data[1]][1])[1:-1])
                                except:
                                    run_error('typ can not to float')
                                    continue
                                else:
                                    value[command_data[1]] = ['Type:Float',('<'+ str(to_float_data) + '>')]
                            else:
                                run_error('typ to float type')
                                continue
                
                        else:
                            #print('\n',line,'\n\n\n')
                            #print('\n',command_data[0],'\n')
                            run_error('typ unkown command')
                            continue
            
        
        elif command == 'got':#got <标签> (<是否记录[False]>)
            #print('got')
            if not len(command_data) >= 1:
                run_error('got format')
                continue
            else:
                if command_data[0] == '~': #返回上一次got
                    if not len(last_label) > 0:
                        run_error('got can not find last label')
                        continue
                    else:
                        run_index = int(last_label[-1])
                        last_label.pop()

                elif not command_data[0] in label.keys():
                    run_error('got label not exist')
                    continue
                else:
                    if len(command_data) == 2 and command_data[1] == 'False':
                        pass
                    else:
                        last_label.append(run_index)
                    run_index = int(label[command_data[0]]) - 1
        
        elif command == 'ifs': #ifs <值1> <值2>
            if len(command_data) != 2:
                run_error('ifs format')
                continue

            else:
                ifs_data_0 = ['Type:None','']
                ifs_data_1 = ['Type:None','']
                if return_type(command_data[0]) == 'Type:Value':#<值1>为变量
                    if not command_data[0] in value.keys():
                        run_error('ifs value1 not exist')
                        continue

                    else:
                        ifs_data_0[0] = return_type(value[command_data[0]][1])
                        ifs_data_0[1] = value[command_data[0]][1]
                else:
                    ifs_data_0[0] = return_type(command_data[0])
                    ifs_data_0[1] = command_data[0]

                if return_type(command_data[1]) == 'Type:Value':#<值2>为变量
                    if not command_data[1] in value.keys():
                        run_error('ifs value2 not exist')
                        continue
                    else:
                        ifs_data_1[0] = return_type(value[command_data[1]][1])
                        ifs_data_1[1] = value[command_data[1]][1]
                else:
                    ifs_data_1[0] = return_type(command_data[1])
                    ifs_data_1[1] = command_data[1]
                
                if ifs_data_0[0] == ifs_data_1[0] and ifs_data_0[0] == 'Type:Int':
                    if not int(str(ifs_data_0[1])[1:-1]) < int(str(ifs_data_1[1])[1:-1]):
                        run_index += 1

                else:
                    #print(ifs_data_0[0],ifs_data_1[0])
                    run_error('ifs value type')
                    continue

        elif command == 'ifb': #ifb <值1> <值2>
            if len(command_data) != 2:
                run_error('ifb format')
                continue
            else:
                ifb_data_0 = ['Type:None','']
                ifb_data_1 = ['Type:None','']
                if return_type(command_data[0]) == 'Type:Value':#<值1>为变量
                    if not command_data[0] in value.keys():
                        run_error('ifb value1 not exist')
                        continue
                    else:
                        ifb_data_0[0] = return_type(value[command_data[0]][1])
                        ifb_data_0[1] = value[command_data[0]][1]
                else:
                    ifb_data_0[0] = return_type(command_data[0])
                    ifb_data_0[1] = command_data[0]

                if return_type(command_data[1]) == 'Type:Value':#<值2>为变量
                    if not command_data[1] in value.keys():
                        run_error('ifb value2 not exist')
                        continue
                    else:
                        ifb_data_1[0] = return_type(value[command_data[1]][1])
                        ifb_data_1[1] = value[command_data[1]][1]
                else:
                    ifb_data_1[0] = return_type(command_data[1])
                    ifb_data_1[1] = command_data[1]
                
                if ifb_data_0[0] == ifb_data_1[0] and ifb_data_0[0] == 'Type:Int':
                    if not int(str(ifb_data_0[1])[1:-1]) > int(str(ifb_data_1[1])[1:-1]):
                        run_index += 1
                else:
                    run_error('ifb value type')
                    continue

        elif command == 'cmp': #cmp <值1> <值2>
            if len(command_data) != 2:
                run_error('cmp format')
                continue

            else:
                cmp_data_0 = ['Type:None','']
                cmp_data_1 = ['Type:None','']
                if return_type(command_data[0]) == 'Type:Value':#<值1>为变量
                    if not command_data[0] in value.keys():
                        run_error('cmp value1 not exist')
                        continue

                    cmp_data_0[0] = return_type(value[command_data[0]][1])
                    cmp_data_0[1] = value[command_data[0]][1]
                else:
                    cmp_data_0[0] = return_type(command_data[2])
                    cmp_data_0[1] = command_data[2]

                if return_type(command_data[1]) == 'Type:Value':#<值2>为变量
                    if not command_data[1] in value.keys():
                        run_error('cmp value2 not exist')
                        continue

                    cmp_data_1[0] = return_type(value[command_data[1]][1])
                    cmp_data_1[1] = value[command_data[1]][1]
                else:
                    cmp_data_1[0] = return_type(command_data[1])
                    cmp_data_1[1] = command_data[1]

                #print(cmp_data_0,cmp_data_1,'\n')

                if cmp_data_0 != cmp_data_1:
                    run_index += 1 


        elif command == 'add': #add <变量> <值>
            if len(command_data) != 2:
                run_error('add format')
                continue

            else:
                if not return_type(command_data[0]) == 'Type:Value':
                    run_error('add value not value')
                    continue

                else:
                    if not command_data[0] in value.keys():
                        run_error('add value not exist')
                        continue
                    else:
                        if return_type(command_data[1]) == 'Type:Value': #<值>为变量
                            if return_type(value[command_data[0]][1]) != return_type(value[command_data[1]][1]):
                                run_error('add type not same')
                                continue
                            else:#有问题
                                if return_type(value[command_data[1]][1]) == 'Type:Int':
                                    
                                    value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) + int(value[command_data[1]][1][1:-1])) + "'"
                                
                                elif return_type(value[command_data[1]][1]) == 'Type:Float':
                                    value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) + float(value[command_data[1]][1][1:-1])) + '>'
                            
                                
                                elif return_type(value[command_data[1]][1]) == 'Type:String':
                                    value[command_data[0]][1] = '"' + str(value[command_data[0]][1][1:-1] + value[command_data[1]][1][1:-1]) + '"'
                                else:
                                    run_error('add value type')
                                    continue

                        else:
                            if return_type(command_data[1]) == 'Type:Int':
                                value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) + int(str(command_data[1])[1:-1])) + "'"
                            elif return_type(command_data[1]) == 'Type:Float':
                                value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) + float(command_data[1][1:-1])) + '>'
                            
                            elif return_type(command_data[1]) == 'Type:String':
                                value[command_data[0]][1] = '"' + str(value[command_data[0]][1])[1:-1] + str(command_data[1][1:-1]) + '"'
                            else:
                                run_error('add value type')
                                continue

        elif command == 'sub': #sub <变量> <值>
            if len(command_data) != 2:
                run_error('sub format')
                continue
            else:
                if not return_type(command_data[0]) == 'Type:Value':
                    run_error('sub value not value')
                    continue
                else:
                    if not command_data[0] in value.keys():
                        run_error('sub value not exist')
                        continue
                    else:
                        if return_type(command_data[1]) == 'Type:Value': #<值>为变量
                            if return_type(value[command_data[0]][1]) != return_type(value[command_data[1]][1]):
                                run_error('sub type not same')
                                continue
                            else:#有问题
                                if return_type(value[command_data[1]][1]) == 'Type:Int':
                                    
                                    value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) - int(value[command_data[1]][1][1:-1])) + "'"
                                
                                elif return_type(value[command_data[1]][1]) == 'Type:Float':
                                    value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) - float(value[command_data[1]][1][1:-1])) + '>'
                            
                                
                                elif return_type(value[command_data[1]][1]) == 'Type:String':
                                    value[command_data[0]][1] = '"' + str(value[command_data[0]][1][1:-1] - value[command_data[1]][1][1:-1]) + '"'
                                else:
                                    run_error('sub value type')
                                    continue
                        
                        else:
                            if return_type(command_data[1]) == 'Type:Int':
                                value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) - int(str(command_data[1])[1:-1])) + "'"
                            elif return_type(command_data[1]) == 'Type:Float':
                                value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) - float(command_data[1][1:-1])) + '>'
                            
                            elif return_type(command_data[1]) == 'Type:String':
                                value[command_data[0]][1] = '"' + str(value[command_data[0]][1])[1:-1] - str(command_data[1][1:-1]) + '"'
                            else:
                                run_error('sub value type')
                                continue

        elif command == 'mul': #mul <值1> <值2>
            if len(command_data) != 2:
                run_error('mul format')
                continue
            else:
                if return_type(command_data[0]) != 'Type:Value':
                    run_error('mul value1 not value')
                    continue

                elif not command_data[0] in value.keys():
                    run_error('mul value1 not exist')
                    continue

                else:
                    mul_data_0 = ['Type:None','']
                    mul_data_1 = ['Type:None','']
                    
                    mul_data_0 = value[command_data[0]]

                    if return_type(command_data[1]) == 'Type:Value': #值2为变量
                        if not command_data[1] in value.keys():
                            run_error('mul value2 not exist')
                            continue
                        else:
                            mul_data_1 = value[command_data[1]]
                    else:

                        mul_data_1[0] = return_type(command_data[1])
                        mul_data_1[1] = command_data[1]
                    
                    if mul_data_0[0] == 'Type:Int' or mul_data_0[0] == 'Type:Float':
                        if mul_data_1[0] == 'Type:Int' or mul_data_1[0] == 'Type:Float':

                                value[command_data[0]][0] = 'Type:Float'
                                value[command_data[0]][1] = '<' + str(float(mul_data_0[1][1:-1]) * float(mul_data_1[1][1:-1])) + '>'
                        else:
                            run_error('mul value2 type')
                            continue
                    else:
                        run_error('mul value1 type')
                        continue

        elif command == 'div': #div <值1> <值2>
            if len(command_data) != 2:
                run_error('div format')
                continue

            else:
                if return_type(command_data[0]) != 'Type:Value':
                    run_error('div value1 not value')
                    continue

                elif not command_data[0] in value.keys():
                    run_error('div value1 not exist')
                    continue
                
                else:
                    div_data_0 = ['Type:None','']
                    div_data_1 = ['Type:None','']
                    
                    div_data_0 = value[command_data[0]]

                    if return_type(command_data[1]) == 'Type:Value': #值2为变量
                        if not command_data[1] in value.keys():
                            run_error('div value2 not exist')
                            continue
                        else:
                            div_data_1 = value[command_data[1]]
                    else:

                        div_data_1[0] = return_type(command_data[1])
                        div_data_1[1] = command_data[1]
                    
                    if div_data_0[0] == 'Type:Int' or div_data_0[0] == 'Type:Float':
                        if div_data_1[0] == 'Type:Int' or div_data_1[0] == 'Type:Float':

                            value[command_data[0]][0] = 'Type:Float'
                            value[command_data[0]][1] = '<' + str(float(div_data_0[1][1:-1]) / float(div_data_1[1][1:-1])) + '>'

                        else:
                            run_error('div value2 type')
                            continue
                    else:
                        run_error('div value1 type')
                        continue

        elif command == 'cal': #cal <返回值> <命令> <参数> ; #in,#out,#read,#write,#type,#len,#split
            if not len(command_data) >= 2:
                run_error('cal format')
                continue

            else:
                if return_type(command_data[0]) != 'Type:Value':
                    run_error('cal return not value')
                    continue
                elif not command_data[0] in value.keys():
                    run_error('cal return not exist')
                    continue
                else:
                    if command_data[1] == '#in': #<返回> #in 
                        if return_type(command_data[0]) == 'Type:Value':
                            if not command_data[0] in value.keys():
                                run_error('cal #in return not exist')
                                continue
                            else:
                                value[command_data[0]][0] = 'Type:String'
                                value[command_data[0]][1] = translatr.to_in('"' +str(input()) + '"')
                            
                        else:
                            run_error('cal #in return not value')    
                            continue    

                    elif command_data[1] == '#out': #<无> #out <值>
                        print_data = ''
                        if return_type(command_data[2]) == 'Type:Value':
                        
                            if not command_data[2] in value.keys():
                                run_error('cal #out value not exist')
                                continue
                            else:
                                print_data = str(value[command_data[2]][1])
                        
                        else:
                            print_data = str(command_data[2])

                        if return_type(print_data) in ['Type:String','Type:Int','Type:String','Type:Float']: #这些类型输出删去标志
                            print_data = print_data[1:-1]   
                        print_data = translatr.to_out(print_data)
                        
                        print(print_data,end='')

                    elif command_data[1] == '#split':#<返回> #split <值1(str)> <值2(str)>
                        pass
                            
                    elif command_data[1] == '#len': #<返回> #len <值>
                        if return_type(command_data[0]) == 'Type:Value':
                            if not command_data[0] in value.keys():
                                run_error('cal #len return not exist')
                                continue

                            else:
                                len_data = ['Type:None','']
                                if return_type(command_data[2]) == 'Type:Value':#<值>为变量
                                    if not command_data[2] in value.keys():
                                        run_error('cal #len value not exist')
                                        continue
                                    else:
                                        len_data = [value[command_data[2]][0],str(value[command_data[2]][1])]
                                else:
                                    len_data[1] = str(command_data[2])
                                    len_data[0] = return_type(len_data[1])
                                
                                if len_data[0] == 'Type:List':
                                    value[command_data[0]] = ['Type:Int',("'" +str(len(len_data[1][1:-1].split(';'))) + "'")]  
                                elif len_data[0] == 'Type:String':
                                    value[command_data[0]] = ['Type:Int',("'" + str(len(len_data[1][1:-1])) + "'")]

                                elif len_data[0] == 'Type:Float':#返回小数位数
                                    len_data = str(len_data[1])[1:-1]
                                    
                                    if not '.' in str(len_data):
                                        run_error('float type')
                                        continue
                                    else:
                                        len_data = len_data.split('.')[1]
                                        value[command_data[0]] = ['Type:Int',("'" + str(len(len_data)) + "'")]
                                    
                                else:
                                    run_error('cal #len value type')
                                    continue

                        else:
                            run_error('cal #len return not value')
                            continue
                    
                    elif command_data[1] == '#type':#<返回> #type <值>
                        if return_type(command_data[0]) == 'Type:Value':
                            if not command_data[0] in value.keys():
                                run_error('cal #type return not exist')
                                continue

                            else:
                                if return_type(command_data[2]) == 'Type:Value':#值为变量
                                    value[command_data[0]][0] = 'Type:String'
                                    value[command_data[0]][1] = str(value[command_data[2]][0])
                                else:
                                    value[command_data[0]][0] = 'Type:String'
                                    value[command_data[0]][1] = tr(return_type(command_data[2]))
                        else:
                            run_error('cal #type return not value')
                            continue

                    elif command_data[1] == '#range': #<返回> #range <值> <起始索引> <末尾索引>
                        range_data = ''
                        start_index = 0
                        end_index = 0
                        range_data_len = 0

                        if return_type(command_data[0]) != 'Type:Value':
                            run_error('cal #range return not value')
                            continue

                        if not command_data[0] in value.keys():
                            run_error('cal #range return not exist')
                            continue

                        if return_type(command_data[2]) == 'Type:Value': #<值>为变量
                            if not command_data[2] in value.keys():
                                run_error('cal #range value not exist')
                                continue
                            else:
                                if value[command_data[2]][0] == 'Type:String' or value[command_data[2]][0] == 'Type:List':
                                    range_data = value[command_data[2]]
                                else:
                                    run_error('cal #range value type')
                                    continue
                        else:
                            range_data = [return_type(command_data[2]),command_data[2]]

                        if range_data[0] == 'Type:String':
                            range_data_len = len(str(range_data[1])[1:-1])
                        
                        elif range_data[0] == 'Type:List':
                            range_data_len = len(str(range_data[1])[1:-1].split(';'))
                        

                        if return_type(command_data[3]) == 'Type:Value': #<起始索引>为变量
                            if not command_data[3] in value.keys():
                                run_error('cal #range start not exist')
                                continue

                            start_index = int(str(value[command_data[3]][1])[1:-1])
                        else:
                            start_index = int(command_data[3][1:-1])
                        
                        if return_type(command_data[4]) == 'Type:Value': #<末尾索引>为变量
                            if not command_data[4] in value.keys():
                                run_error('cal #range start not exist')
                                continue
                            
                            end_index = int(str(value[command_data[4]][1])[1:-1])
                        else:
                            end_index = int(command_data[4][1:-1]) 
                        
                        if start_index < end_index and end_index < range_data_len:
                            

                            if range_data[0] == 'Type:List':
                                range_data = str(range_data[1])[1:-1].split(';')[start_index:end_index + 1]
                                range_return_data ='{'
                                for range_add_return_data in range_data:
                                    range_return_data += str(range_add_return_data)
                                    range_return_data += ';'
                                
                                range_return_data = range_return_data[0:-1]
                                range_return_data += '}'

                                value[command_data[0]] = ['Type:List',(range_return_data)]

                            else:

                                range_data = str(range_data[1])[1:-1]
                                
                                value[command_data[0]] = ['Type:Strint',('"' +str(range_data[start_index:end_index + 1]) + '"')]

                        else:
                            #print(start_index,end_index,range_data_len)
                            run_error('cal #range index')
                            continue


                    else:
                        run_error('cal unkown command') 
                        continue
        
        elif command == 'psh': #psh <变量(list)> <值>
            if len(command_data) != 2:
                run_error('psh format')
                continue

            else:
                if return_type(command_data[0]) != 'Type:Value':
                    run_error('psh value not value')
                    continue

                else:
                    if not command_data[0] in value.keys():
                        run_error('psh value not exist')
                        continue

                    else:
                        if value[command_data[0]][0] == 'Type:List':
                            psh_data = value[command_data[0]][1]
                            psh_data = psh_data[0:-1]
                            
                            if psh_data != '{': #list为空
                                psh_data += ';'
                            
                            psh_data += command_data[1]
                            psh_data += '}'

                            value[command_data[0]] = ['Type:List',psh_data]
                        else:
                            run_error('psh value type')

        elif command == 'pop': #pop <变量(list)> <索引>
            if len(command_data) != 2:
                run_error('pop format')
                continue
            else:
                if return_type(command_data[0]) != 'Type:Value':
                    run_error('pop value not value')
                    continue
                else:
                    if not command_data[0] in value.keys():
                        run_error('pop value not exist')
                        continue

                    else:
                        if value[command_data[0]][0] == 'Type:List':
                            
                            
                            pop_data = str(value[command_data[0]][1])[1:-1].split(';')
                            pop_len = len(pop_data)
                            if int(command_data[1][1:-1]) >= pop_len:
                                run_error('pop index over')
                                continue

                            else:
                                
                                pop_data.pop(int(command_data[1][1:-1]))
                                
                                pop_return_list = '{'

                                for pop_list_data in pop_data:
                                    pop_return_list += str(pop_list_data) + ';'
                                
                                pop_return_list = pop_return_list[0:-1]
                                pop_return_list += '}'

                                value[command_data[0]] = ['Type:List',pop_return_list]
                        else:
                            run_error('pop value type')
                            continue
                

        elif command == 'idx': #idx <变量(list)> <索引>
            if len(command_data) != 2:
                run_error('idx format')
                continue
            else:
                if return_type(command_data[0]) != 'Type:Value':
                    run_error('idx value not value')
                    continue
                else:
                    
                    idx_data_list = ['Type:None','']
                    if value[command_data[0]][0] == 'Type:List':
                        idx_data_list[1] = str(value[command_data[0]][1])[1:-1].split(';')
                        
                    elif value[command_data[0]][0] == 'Type:Strint':
                        idx_data_list[1] = str(value[command_data[0]][1])[1:-1]
                    else:
                        run_error('idx value type')
                        continue
                        
                    idx_data_idx = ['Type:Int','']    

                    if return_type(command_data[1]) == 'Type:Value': #<索引>为变量
                        if value[command_data[1]][0] == 'Type:Int':
                            idx_data_idx[1] = int(str(value[command_data[1]][1])[1:-1])
            
                        else:
                            run_error('idx index type')
                            continue
                    else:
                        idx_data_idx[1] = int(str(command_data[1])[1:-1])  
                    if idx_data_idx[1] >= len(idx_data_list[1]):
                        run_error('idx index over')
                        continue
                    else:
                        idx_data_idx[0] = return_type(idx_data_idx[1])
                        
                        idx_data = idx_data_list[1][int(idx_data_idx[1])]
                        value[command_data[0]] = [return_type(idx_data),idx_data]

        elif command == 'err':# err <标签>
            if len(command_data) != 1:
                run_error('err format')
                continue
            else:
                if command_data[0] == '~':
                    error_flag = True
                    error_label = int(last_label[-1])
                elif command_data[0] in label.keys():
                    error_flag = True
                    error_label = label[command_data[0]]
                else:
                    run_error('err label not exist')
                    continue

        elif command == 'rpy': #rpy <返回> <值>
            if len(command_data) != 2:
                run_error('rpy format')
                continue
            else:
                if return_type(command_data[0]) == 'Type:Value':
                    if not command_data[0] in value.keys():
                        run_error('rpy return not exist')
                        continue

                    else:
                        rpy_command = ''
                        if return_type(command_data[1]) == 'Type:Value':#<值>为变量
                            if not command_data[1] in value.keys():
                                run_error('rpy value not exist')
                                continue
                            else:
                                if value[command_data[1]][0] == 'Type:String':
                                    rpy_command = str(value[command_data[1]][1])[1:-1]
                                else:
                                    run_error('rpy value type')
                                    continue
                        else:
                            if return_type(command_data[1]) == 'Type:String':
                                rpy_command = str(command_data[1])[1:-1]
                                
                            else:
                                run_error('rpy value type')
                                continue
                                
                        rpy_command = translatr.to_out(rpy_command)
                        try:
                            exec(rpy_command,globals(),locals())
                        except Exception as error_message:
                            
                            run_error('rpy command')
                            print(error_message)#后期要改，临时
                            continue

                else:
                    run_error('rpy return not value')
                    continue
                    
        elif command == 'put': #put <错误>
            if len(command_data) != 1:
                run_error('put format')
            else:
                run_error(translatr.to_out(command_data[0][1:-1]))
                continue

        else:
            #print(command)
            run_error('unkown command')
            continue

        #print(value)
        run_index += 1
     
    #print(code)
    end()

run(code)