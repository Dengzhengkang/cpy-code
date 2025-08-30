
value = {'_None':['Type:None',''],'_Error':['Type:String','']} #[<type>,<value>],_Error:错误类型
last_label = [0] #上一次的got位置
error_label = ''
error_flag = False
include_pack = ['']
label = {'~start':0}
run_index = 0

debug_flag = False #调试
debug_hook = [] #钩子列表 0:返回状态 1:返回执行命令，2:执行下一行
#代码编写区↓
code =\
'''
new _a
mov _a "123"
idx _a '1'123
'''
#转义符 ^n:换行 ^s:空格 ^d:分隔
# 二进制处理没做完！gui出问题，err处理加～返回默认逻辑

class translatr: #处理转译
    @staticmethod #可要可不要，目的省去self（python自动省去）
    def to_in(data):
        return str(data).replace(' ','^s').replace(';','^d')
    
    @staticmethod
    def to_out(data):
        return str(data).replace('^s',' ').replace('^d',';').replace('^n','\n')
    
def end():#输出调试信息
    if debug_flag == True:
        debug_hook[0]('end')
    else:
        print('\n-----------------')
        print(label)
        print(value)
        print(last_label)
        
def run(code):
    global run_index
    global error_flag
    global error_label

    run_index = 0

    def load_pack(name):
        try:
            with open('./pack/' + str(name)[1:] + '.crp','r',encoding='utf-8') as pack:
                return pack.readlines()

        except:
            return 'Error'

    def run_error(errtype,message): #message是调试专属
        global run_index
        value['_Error'][1] = str(errtype)

        if error_flag == True: #开启err
            if debug_flag == True: #调试
                debug_hook[0]('flag_error',[type,message])

            run_index = error_label
            value['_Error'][1] = '"' +str(type) +'"'
            return
        
        elif debug_flag == True: #调试
            debug_hook[0]('error',[type,message])

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
            first_char = str(data)[0]
            end_char = str(data)[-1]

            if first_char == '_':
                return 'Type:Value'
            elif first_char == '{' and end_char == '}':
                return 'Type:List'
            elif first_char == "'" and end_char == "'":
                return 'Type:Int'
            elif first_char == '"' and end_char == '"':
                return 'Type:String'
            elif first_char == '<' and end_char == '>':
                return 'Type:Float'
            elif first_char == '[' and end_char == ']':
                return 'Type:Byte'
            elif first_char == '~':
                return 'Type:Label'
            elif first_char == '*':
                return 'Type:Pack'
            else:
                return 'Type:None'
            
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
                run_error('FormatError','nwe format error')
                continue
            else:
                
                for create_value in line.split(' ')[1:]:
                    
                    if return_type(create_value) != 'Type:Value':
                        run_error('TypeError','new argu type not value')
                        continue
                    else:
                        if create_value in value.keys():
                            run_error('ValueExist','new value exist')
                            continue
                        else:
                            value[create_value] = ['Type:None','']
        
        elif command == 'imp':#imp <包>
            if len(line) == 1:
                run_error('FormatError','imp format error')
                continue
            else:
                for imp_pack in line.split(' ')[1:]:
                    imp_pack_name = ''
                    if return_type(imp_pack) == 'Type:Value':#<包>为值
                        if return_type(value[imp_pack]) == 'Type:Pack':
                            imp_pack_name = value[imp_pack]
                        else:
                            run_error('TypeError','imp argu type not pack')
                            continue
                    else:
                        if return_type(imp_pack) == 'Type:Pack':
                            imp_pack_name = imp_pack
                        else:
                            run_error('TypeError','imp agru type not pack')
                            continue
                    
                    if imp_pack_name in include_pack:#已经导入包
                        pass
                    else:
                        return_load = load_pack(imp_pack_name)
                        if return_load == 'Error':
                            run_error('LoadError','imp pack load error')
                            
                        else:
                            for pack_line in return_load[1:]:
                                code += pack_line
                        include_pack.append(imp_pack_name)
                    

    code = code.split('\n')
    if debug_flag == True:
        debug_hook[0]('first run end',data=code)


    while run_index < len(code):

        #print(run_index)

        line = code[run_index]
        command = line.split(' ',1)[0]
        command_data = line.split(' ')[1:]

        if debug_flag == True and run_index != 0 and line != '': #调试
            debug_hook[1](command,command_data)

        if line == '' or (line[0] in [';','~','\n']) or (command in ['new','imp']):#跳过执行
            run_index += 1
            continue
        
        if command == 'mov': #mov <变量> <值>
            if len(command_data) != 2:
                run_error('FormatError','mov format error')
                continue

            else:
                if command_data[0] == '~':
                    error_flag = False
                elif not command_data[0] in value.keys():#判断变量
                    run_error('ValueError','mov argu1 not value')
                    continue

                else:
                    if return_type(command_data[1]) == 'Type:Value': #<值>为变量
                        if not command_data[1] in value.keys():
                            run_error('ValueExist','mov argu2 not exist value')
                            continue
                        else:
                            value[command_data[0]] = value[command_data[1]]
                    else:
                        value[command_data[0]][0] = return_type(command_data[1])
                        value[command_data[0]][1] = command_data[1]
    
        elif command == 'typ': #typ <变量> <类型>;int str list float
            if len(command_data) != 2:
                run_error('FormatError','typ format error')
                continue
            else:
                
                if not command_data[0] in value.keys():
                    run_error('ValueError','typ argu1 not exist value')
                    continue
                else:
                    if command_data[1] == 'Type:String':

                        value[command_data[0]][1] = '"' + str(value[command_data[0]][1])[1:-1] +'"'
                        value[command_data[0]][0] = 'Type:String'

                    elif command_data[1] == 'Type:Int':    
                        typ_to_int = 0
                        if value[command_data[0]][0] == 'Type:Byte': #二进制操作
                            try:
                                byte_flag = int(value[command_data[0]][1][1:-1].split(';')[0]) #符号标志
                                byte_data = int(value[command_data[0]][1][1:-1].split(';')[1])

                                byte_data = str(int(str(byte_data),2))

                                if byte_flag ==  1:
                                    byte_data = '-' + byte_data
            
                            except:
                                run_error('TypeError','typ change error')
                            else:
                                byte_data = "'" + str(byte_data) + "'"
                                value[command_data[0]] = ['Type:Int',byte_data]

                        else:
                            try:
                                typ_to_int = int(str(value[command_data[0]][1])[1:-1])
                            except:
                                run_error('TypeError','typ change error')
                                continue
                            else:
                                value[command_data[0]][1] = "'" + str(typ_to_int) + "'"
                                value[command_data[0]][0] = 'Type:Int'

                    elif command_data[1] == 'Type:Byte': #转化为TypeByte
                        typ_to_byte = ''
                        typ_to_flag = ''

                        if value[command_data[0]][0] == 'Type:Int':
                            try:
                                typ_to_byte = int(value[command_data[0]][1][1:-1])
                                if typ_to_byte < 0:
                                    typ_to_flag = '1'
                                else:
                                    typ_to_flag = '0'
                                    
                                typ_to_byte = abs(typ_to_byte)
                                typ_to_byte = bin(typ_to_byte)[2:]
                                typ_to_byte = '[' + typ_to_flag + ';' + typ_to_byte +']'
                            except:

                                run_error('TypeError','typ change error')
                                continue

                            else:
                                value[command_data[0]] = ['Type:Byte',typ_to_byte]
                        
                        
                        elif value[command_data[0]][0] == 'Type:Strint': #计划中
                            pass
                        else:
                            run_error('TypeError','typ change error')
                            continue


                    elif command_data[1] == 'Type:List':
                        to_list_data = ['Type:List','{']
                         

                        for list_data in str(value[command_data[0]][1]).split(';'):

                            to_list_data[1] += str(list_data) + ';'
                            
                        to_list_data[1] = str(to_list_data[1])[0:-1] #去除结尾的;
                        to_list_data[1] += '}' #添加list结尾
                            
                        value[command_data[0]] = to_list_data

                    elif command_data[1] == 'Type:Float':
                        to_float_data = ''

                        if value[command_data[0]][0] == 'Type:String' or value[command_data[0]][0] == 'Type:Int':
                            try:
                                to_float_data = float(str(value[command_data[0]][1])[1:-1])
                            except:
                                run_error('TypeError','typ change error')
                                continue
                            else:
                                value[command_data[0]] = ['Type:Float',('<'+ str(to_float_data) + '>')]
                        else:
                            run_error('TypeError','typ change error')
                            continue
                
                    else:
                        #print('\n',line,'\n\n\n')
                        #print('\n',command_data[0],'\n')
                        run_error('ArguError','typ type error')
                        continue        
        
        elif command == 'got':#got <标签> (<是否记录[False]>)
            #print('got')
            if not len(command_data) >= 1:
                run_error('FormatError','got format error')
                continue
            else:
            
                if command_data[0] == '~': #返回上一次got
                    if not len(last_label) > 0:
                        run_error('LabelError','got last_label not exist')
                        continue
                    else:
                        run_index = int(last_label[-1])
                        last_label.pop()

                elif not command_data[0] in label.keys():
                    run_error('LabelError','got label not exist')
                    continue

                else:
                    if len(command_data) == 2 and command_data[1] == 'False':
                        pass #静默跳转不记录
                    else:
                        last_label.append(run_index)

                    run_index = int(label[command_data[0]]) - 1


        elif command == 'ifs': #ifs <值1> <值2>
            if len(command_data) != 2:
                run_error('FormatError','ifs format error')
                continue

            else:
                ifs_data_0 = ['Type:None','']
                ifs_data_1 = ['Type:None','']
                if return_type(command_data[0]) == 'Type:Value':#<值1>为变量                    ========错误该到这===
                    if not command_data[0] in value.keys():
                        run_error('ValueError','ifs argu1 not exist')
                        continue

                    else:
                        ifs_data_0[0] = return_type(value[command_data[0]][1])
                        ifs_data_0[1] = value[command_data[0]][1]
                else:
                    ifs_data_0[0] = return_type(command_data[0])
                    ifs_data_0[1] = command_data[0]

                if return_type(command_data[1]) == 'Type:Value':#<值2>为变量
                    if not command_data[1] in value.keys():
                        run_error('ValueError','ifs argu2 not exist')
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

                elif ifs_data_0[0] == ifs_data_1[0] and ifs_data_0[0] == 'Type:Float':
                    if not float(str(ifs_data_0[1])[1:-1]) < float(str(ifs_data_1[1])[1:-1]):
                        run_index += 1
                else:
                    #print(ifs_data_0[0],ifs_data_1[0])
                    run_error('TypeError','ifs argu type')
                    continue

        elif command == 'ifb': #ifb <值1> <值2>
            if len(command_data) != 2:
                run_error('FormatError','ifb format error')
                continue

            else:
                ifb_data_0 = ['Type:None','']
                ifb_data_1 = ['Type:None','']
                if return_type(command_data[0]) == 'Type:Value':#<值1>为变量
                    if not command_data[0] in value.keys():
                        run_error('ValueError','ifb argu1 not exist')
                        continue

                    else:
                        ifb_data_0[0] = return_type(value[command_data[0]][1])
                        ifb_data_0[1] = value[command_data[0]][1]
                else:
                    ifb_data_0[0] = return_type(command_data[0])
                    ifb_data_0[1] = command_data[0]

                if return_type(command_data[1]) == 'Type:Value':#<值2>为变量
                    if not command_data[1] in value.keys():
                        run_error('ValueError','ifb argu2 not exist')
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
                elif ifb_data_0[0] == ifb_data_1[0] and ifb_data_0[0] == 'Type:Float':
                    if not float(str(ifb_data_0[1])[1:-1]) > float(str(ifb_data_1[1])[1:-1]):
                        run_index += 1
                else:
                    run_error('TypeError','ifb argu type')
                    continue

        elif command == 'cmp': #cmp <值1> <值2>
            if len(command_data) != 2:
                run_error('FormatError','cmp format error')
                continue

            else:
                cmp_data_0 = ['Type:None','']
                cmp_data_1 = ['Type:None','']
                if return_type(command_data[0]) == 'Type:Value':#<值1>为变量
                    if not command_data[0] in value.keys():
                        run_error('ValueError','cmp argu1 not exist')
                        continue

                    cmp_data_0[0] = return_type(value[command_data[0]][1])
                    cmp_data_0[1] = value[command_data[0]][1]
                else:
                    cmp_data_0[0] = return_type(command_data[2])
                    cmp_data_0[1] = command_data[2]

                if return_type(command_data[1]) == 'Type:Value':#<值2>为变量
                    if not command_data[1] in value.keys():
                        run_error('ValueError','cmp argu2 not exist')
                        continue

                    cmp_data_1[0] = return_type(value[command_data[1]][1])
                    cmp_data_1[1] = value[command_data[1]][1]
                else:
                    cmp_data_1[0] = return_type(command_data[1])
                    cmp_data_1[1] = command_data[1]

                #print(cmp_data_0,cmp_data_1,'\n')

                if cmp_data_0 != cmp_data_1: 
                    run_index += 1 #不一样跳过下一行


        elif command == 'add': #add <变量> <值>
            if len(command_data) != 2:
                run_error('FormatError','add format error')
                continue

            else:
   
                if not command_data[0] in value.keys():
                    run_error('ValueError','add value not exist value')
                    continue
        
                else:
                    if return_type(command_data[1]) == 'Type:Value': #<值>为变量
                        if return_type(value[command_data[0]][1]) != return_type(value[command_data[1]][1]):
                            run_error('TypeError','add type not same')
                            continue

                        else:
                            if value[command_data[1]][0] == 'Type:Int':
                                    
                                value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) + int(value[command_data[1]][1][1:-1])) + "'"
                                
                            elif value[command_data[1]][0] == 'Type:Float':
                                value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) + float(value[command_data[1]][1][1:-1])) + '>'
                                            
                            elif value[command_data[1]][0] == 'Type:String':
                                value[command_data[0]][1] = '"' + str(value[command_data[0]][1][1:-1] + value[command_data[1]][1][1:-1]) + '"'
                        
                            else:
                                run_error('TypeError','add value type error')
                                continue

                    else:
                        if return_type(value[command_data[0]][1]) != return_type(command_data[1]):
                            run_error('TypeError','add type not same')
                            continue
                        else:
                            if return_type(command_data[1]) == 'Type:Int':
                                value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) + int(str(command_data[1])[1:-1])) + "'"
                            elif return_type(command_data[1]) == 'Type:Float':
                                value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) + float(command_data[1][1:-1])) + '>'
                                
                            elif return_type(command_data[1]) == 'Type:String':
                                value[command_data[0]][1] = '"' + str(value[command_data[0]][1])[1:-1] + str(command_data[1][1:-1]) + '"'
                            
                            else:
                                run_error('TypeError','add value type error')
                                continue

        elif command == 'sub': #sub <变量> <值>
            if len(command_data) != 2:
                run_error('FormatError','sub format error')
                continue
            else:
              
                if not command_data[0] in value.keys():
                    run_error('ValueError','sub value not exist value')
                    continue
    
                else:
                    if return_type(command_data[1]) == 'Type:Value': #<值>为变量
                        if return_type(value[command_data[0]][1]) != return_type(value[command_data[1]][1]):
                            run_error('TypeError','sub type not same')
                            continue
    
                        else:
                            if value[command_data[1]][0] == 'Type:Int':
                                    
                                value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) - int(value[command_data[1]][1][1:-1])) + "'"
                                
                            elif value[command_data[1]][0] == 'Type:Float':
                                value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) - float(value[command_data[1]][1][1:-1])) + '>'
                                                
                            else:
                                run_error('TypeError','sub value type error')
                                continue
                        
                    else:
                        if return_type(value[command_data[0]][1]) != return_type(command_data[1]):
                            run_error('TypeError','sub type not same')
                            continue
                        else:
                            if return_type(command_data[1]) == 'Type:Int':
                                value[command_data[0]][1] = "'" + str(int(value[command_data[0]][1][1:-1]) - int(str(command_data[1])[1:-1])) + "'"
                            elif return_type(command_data[1]) == 'Type:Float':
                                value[command_data[0]][1] = '<' + str(float(value[command_data[0]][1][1:-1]) - float(command_data[1][1:-1])) + '>'
                                
                            elif return_type(command_data[1]) == 'Type:String':
                                value[command_data[0]][1] = '"' + str(value[command_data[0]][1])[1:-1] - str(command_data[1][1:-1]) + '"'
                            else:
                                run_error('TypeError','sub value type error')
                                continue

        elif command == 'mul': #mul <值1> <值2>
            if len(command_data) != 2:
                run_error('FormatError','mul format error')
                continue
            else:
                if not command_data[0] in value.keys():
                    run_error('ValueError','mul argu1 not exist value')
                    continue

                else:
                    mul_data_0 = ['Type:None','']
                    mul_data_1 = ['Type:None','']
                    
                    mul_data_0 = value[command_data[0]]

                    if return_type(command_data[1]) == 'Type:Value': #值2为变量
                        if not command_data[1] in value.keys():
                            run_error('ValueError','mul argu2 not exist')
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
                            run_error('TypeError','mul argu2 type')
                            continue
                    else:
                        run_error('TypeError','mul agru1 type')
                        continue

        elif command == 'div': #div <值1> <值2>
            if len(command_data) != 2:
                run_error('FormatError','div format error')
                continue

            else:
                if not command_data[0] in value.keys():
                    run_error('ValueError','div argu1 not exist value')
                    continue
                
                else:
                    div_data_0 = ['Type:None','']
                    div_data_1 = ['Type:None','']
                    
                    div_data_0 = value[command_data[0]]

                    if return_type(command_data[1]) == 'Type:Value': #值2为变量
                        if not command_data[1] in value.keys():
                            run_error('ValueError','div argu2 not exist')
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
                            run_error('Type:Error','div argu2 type')
                            continue
                    else:
                        run_error('TypeError','div argu1 type')
                        continue

        elif command == 'cal': #cal <返回值> <命令> <参数> ; #in,#out,#read,#write,#type,#len,#split,#range
            if not len(command_data) >= 2:
                run_error('FormatError','cal format error')
                continue

            else:
          
                if not command_data[0] in value.keys():
                    run_error('ValueError','cal return not exist value')
                    continue
                else:
                    if command_data[1] == '#in': #<返回> #in 
                        
                        value[command_data[0]][0] = 'Type:String'
                        value[command_data[0]][1] = translatr.to_in('"' +str(input()) + '"')
                

                    elif command_data[1] == '#out': #<无> #out <值>
                        print_data = ''
                        if return_type(command_data[2]) == 'Type:Value':
                        
                            if not command_data[2] in value.keys():
                                run_error('ValueError','cal #out value not exist')
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
                    
                        len_data = ['Type:None','']
                        if return_type(command_data[2]) == 'Type:Value':#<值>为变量
                            if not command_data[2] in value.keys():
                                run_error('ValueError','cal #len value not exist')
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
                                run_error('TypeError','cal #len float type error')
                                continue
                            else:
                                len_data = len_data.split('.')[1]
                                value[command_data[0]] = ['Type:Int',("'" + str(len(len_data)) + "'")]
                                    
                        else:
                            run_error('TypeError','cal #len value type')
                            continue
              
                    elif command_data[1] == '#type':#<返回> #type <值>
                        if return_type(command_data[2]) == 'Type:Value':#值为变量
                            value[command_data[0]][0] = 'Type:String'
                            value[command_data[0]][1] = str(value[command_data[2]][0])
                        else:
                            value[command_data[0]][0] = 'Type:String'
                            value[command_data[0]][1] = str(return_type(command_data[2]))
        
                    elif command_data[1] == '#range': #<返回> #range <值> <起始索引> <末尾索引>
                        range_data = ''
                        start_index = 0
                        end_index = 0
                        range_data_len = 0

                        if return_type(command_data[2]) == 'Type:Value': #<值>为变量
                            if not command_data[2] in value.keys():
                                run_error('ValueError','cal #range value not exist')
                                continue

                            else:
                                if value[command_data[2]][0] == 'Type:String' or value[command_data[2]][0] == 'Type:List':
                                    range_data = value[command_data[2]]
                                else:
                                    run_error('TypeError','cal #range value type error')
                                    continue
                        else:
                            range_data = [return_type(command_data[2]),command_data[2]]

                        if range_data[0] == 'Type:String':
                            range_data_len = len(str(range_data[1])[1:-1])
                        
                        elif range_data[0] == 'Type:List':
                            range_data_len = len(str(range_data[1])[1:-1].split(';'))              

                        if return_type(command_data[3]) == 'Type:Value': #<起始索引>为变量
                            if not command_data[3] in value.keys():
                                run_error('ValueError','cal #range start not exist')
                                continue

                            start_index = int(str(value[command_data[3]][1])[1:-1])
                        else:
                            start_index = int(command_data[3][1:-1])
                        
                        if return_type(command_data[4]) == 'Type:Value': #<末尾索引>为变量
                            if not command_data[4] in value.keys():
                                run_error('ValueError','cal #range start not exist')
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
                            run_error('IndexError','cal #range index over')
                            continue

                    elif command_data[1] == '#python':# <返回> #python <值(命令)>
                        python_command = ''
                        if return_type(command_data[2]) == 'Type:Value': #<值(命令)>为变量
                            if command_data[2] in value.keys(): 
                                python_command = value[command_data[2]][1]
                            else:
                                run_error('ValueError','cal #python value not exist')
                        else:
                            python_command = command_data[2]

                        if return_type(python_command) == 'Type:String':
                            python_command = translatr.to_out(python_command[1:-1])
                            try:
                            
                                exec(python_command,globals(),locals())
                            
                            except Exception as error_message:
                                value[command_data[0]] = ['Type:None',str(error_message)]
                            
                        else:
                            run_error('TypeError','cal #python value type')


                    else:
                        run_error('ArguError','cal unkown command') 
                        continue

        elif command == 'bym': #bym <变量(byte()> <值> (<符号位移位>[False])
            if not len(command_data) >= 2:
                run_error('FormatError','bym format error')
                continue
                
            if not command_data[0] in value.keys():
                run_error('ValueError','bym value not exist value')
                continue
            else:
                if value[command_data[0]][0] == 'Type:Byte':
                    #    [0;0000001]
                    #idx -1 ... 210
                    bym_move = 0
                    bym_byte_data = ''
                    bym_flag = value[command_data[0]][1][1:-1].split(';')[0]
                    bym_byte_data = value[command_data[0]][1][1:-1].split(';')[1]
                    
                    if len(command_data) == 3 and command_data[2] == 'False': #符号位不参与
                        pass
                    else:
                        bym_byte_data = bym_flag + bym_byte_data 

                    if return_type(command_data[1]) == 'Type:Value':#<值>为变量
                        if command_data[1] not in value.keys():
                            run_error('ValueError','bym value not exist value')
                            continue
                        
                        else:
                            bym_move = int(value[command_data[1]][1][1:-1])
                    
                    else:
                        bym_move = int(command_data[1][1:-1])
                        
                    if bym_move < 0:# 向左移位
                        bym_byte_data = bym_byte_data << abs(int(bym_move))
                    else:
                        bym_byte_data = bym_byte_data >> int(bym_move)

                    print(bin(abs(bym_byte_data)))
                    

                else:
                    run_error('TypeError','bym value type error')
                    continue
        
        elif command == 'psh': #psh <变量(list)> <值>
            if len(command_data) != 2:
                run_error('FormatError','psh format error')
                continue

            else:
                if not command_data[0] in value.keys():
                    run_error('ValueError','psh value not exist value')
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
                        run_error('TypeError','psh value type error')

        elif command == 'pop': #pop <变量(list)> <索引>
            if len(command_data) != 2:
                run_error('FormatError','pop format error')
                continue
            else:
            
                if not command_data[0] in value.keys():
                    run_error('ValueError','pop value not exist value')
                    continue

                else:
                    if value[command_data[0]][0] == 'Type:List':
                                            
                        pop_data = str(value[command_data[0]][1])[1:-1].split(';')
                        pop_len = len(pop_data)
                        if int(command_data[1][1:-1]) >= pop_len:
                            run_error('IndexError','pop index over')
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
                        run_error('Type:Error','pop value type error')
                        continue
                

        elif command == 'idx': #idx <变量> <索引>
            if len(command_data) != 2:
                run_error('FormatError','idx format error')
                continue
            else:
                if command_data[0] not in value.keys():
                    run_error('ValueError','idx value not exist value')
                    continue
                else:             
                    idx_data_list = ['Type:None','']
                    if value[command_data[0]][0] == 'Type:List':
                        idx_data_list[1] = str(value[command_data[0]][1])[1:-1].split(';')
                        
                    
                    elif value[command_data[0]][0] == 'Type:String':
                        idx_data_list[1] = str(value[command_data[0]][1])[1:-1]

                    else:
                        run_error('TypeError','idx value type error')
                        continue
                        
                    idx_data_idx = ['Type:Int','']    

                    if return_type(command_data[1]) == 'Type:Value': #<索引>为变量
                        if value[command_data[1]][0] == 'Type:Int':
                            idx_data_idx[1] = int(str(value[command_data[1]][1])[1:-1])
            
                        else:
                            run_error('TypeError','idx index type error')
                            continue
                    else:
                        try:
                            idx_data_idx[1] = int(str(command_data[1])[1:-1])  
                        except:
                            run_error('ArguError','idx index type error')

                    if idx_data_idx[1] >= len(idx_data_list[1]):
                        run_error('IndexError','idx index over')
                        continue
                    else:
                        idx_data_idx[0] = return_type(idx_data_idx[1])
                        
                        idx_data = idx_data_list[1][int(idx_data_idx[1])]
                        value[command_data[0]] = [return_type(idx_data),idx_data]

        elif command == 'err':# err <标签>
            if len(command_data) != 1:
                run_error('FormatError','err format error')
                continue
            else:
                if command_data[0] == '~':
                    error_flag = False
                    error_label = 0

                elif command_data[0] in label.keys():
                    error_flag = True
                    error_label = label[command_data[0]]
                else:
                    run_error('ValueError','err label not exist')
                    continue
   
        elif command == 'put': #put <错误类型> <错误>
            if len(command_data) != 2:
                run_error('FormatError','put format error')
                continue

            else:
                run_error(translatr.to_out(command_data[0][1:-1]),translatr.to_out(command_data[1][1:-1]))
                continue

        else:
            #print(command)
            run_error('CommandError','unknowError')
            continue

        #print(value)
        if debug_flag == True: #调试模式
            debug_hook[2](run_index)
        else:
            run_index += 1
     
    #print(code)    
    end()

if __name__ == '__main__': #main.py直接运行
    run(code)