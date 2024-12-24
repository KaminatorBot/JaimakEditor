import re

class Argument:
    def __init__(self, name, value, type_arg):
        self.name = name
        self.value = value
        self.type_arg = type_arg

class Command:
    name:str
    static_args:list[Argument]
    more_args:list|bool = False

    @classmethod
    def execute(cls):
        return

VRS_CODE:dict[str,list[Command]|str] = {
    'COMMANDS': [],
    'INIT_CHAR': '~ ',
    'COMMAND_PREFIX': '$'
}

def __clear(command:Command, saved_args:list[Argument]):
    for static_arg,saved_arg in zip(command.static_args, saved_args):
        static_arg.value = saved_arg.value
    
    command.more_args = [] if type(command.more_args) == list else False

def compiler():
    total_re = r'(\-[0-9]+\.[0-9]+|[0-9]+\.[0-9]+|\-[0-9]+|[0-9]+|\'[^\']*\'|(?<!\')\b[a-zA-Z][^\s\']*\b(?!\'))'

    float_re = r"(?<!')\-?[0-9]+\.[0-9]+(?!')"
    int_re = r"(?<!')\-?[0-9]+(?!')"
    text_re = r'(\'[^\']*\'|(?<!\')\b[a-zA-Z][^\s\']*\b(?!\'))'
    command_re = r'\$[a-zA-Z]+'

    command_name = input(VRS_CODE['INIT_CHAR'])
    
    try:
        response:str = re.findall(command_re, command_name)[0]
    except Exception:
        return 'ERR_NOT_COMMAND'
    
    command = None

    for c in VRS_CODE['COMMANDS']:
        if c.name == response.replace('$', ''):
            command = c
            break
    
    if command is None:
        return 'ERR_UNK_COMMAND'

    saved_args = command.static_args.copy()

    args = re.findall(total_re, command_name.replace(command.name, ''))
    ultimate = 0

    if len(args) <= 0 and command.static_args == [] and command.more_args == False:
        command.execute()
        __clear(command, saved_args)
        return 'END_COMP'

    try:
        for i in range(0, len(command.static_args)):
            if i == len(command.static_args)-1:
                ultimate = i
            
            if command.static_args[i].type_arg == 'number':
                try:
                    if re.findall(float_re, args[i]) != []:
                        command.static_args[i].value = float(args[i])
                    elif re.findall(int_re, args[i]) != []:
                        command.static_args[i].value = int(args[i])
                    else:
                        __clear(command, saved_args)
                        return 'ERR_VALUE'
                except Exception:
                    __clear(command, saved_args)
                    return 'ERR_VALUE'
            elif command.static_args[i].type_arg == 'text':
                if re.findall(float_re, args[i]) != []:
                    __clear(command, saved_args)
                    return 'ERR_VALUE'
                elif re.findall(int_re, args[i]) != []:
                    __clear(command, saved_args)
                    return 'ERR_VALUE'
                elif re.findall(text_re, args[i]) != []:
                    command.static_args[i].value = str(args[i]).replace("'", '')
                else:
                    __clear(command, saved_args)
                    return 'ERR_VALUE'
            elif command.static_args[i].type_arg == 'any':
                try:
                    if re.findall(float_re, args[i]) != []:
                        command.static_args[i].value = float(args[i])
                    elif re.findall(int_re, args[i]) != []:
                        command.static_args[i].value = int(args[i])
                    elif re.findall(text_re, args[i]) != []:
                        command.static_args[i].value = args[i].replace("'", '')
                    else:
                        __clear(command, saved_args)
                        return 'ERR_VALUE'
                except:
                    __clear(command, saved_args)
                    return 'ERR_VALUE'
            else:
                __clear(command, saved_args)
                return 'ERR_TYPE_ARG'
    except Exception:
        __clear(command, saved_args)
        return 'UNK_ARGUMENT'

    if type(command.more_args) == list:
        for i in range(ultimate+1, len(args)):
            try:
                if re.findall(float_re, args[i]) != []:
                    command.more_args.append(float(args[i]))
                elif re.findall(int_re, args[i]) != []:
                    command.more_args.append(int(args[i]))
                elif re.findall(text_re, args[i]) != []:
                    command.more_args.append(args[i].replace("'", ''))
                else:
                    __clear(command, saved_args)
                    return 'VALUE_ERROR'
            except:
                __clear(command, saved_args)
                return 'ERR_ARGS_EMPTY'
    command.execute()

    __clear(command, saved_args)
    
    return 'END_COMP'