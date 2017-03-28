code = {
    'char': 1,
    'double': 2,
    'enum': 3,
    'float': 4,
    'int': 5,
    'long': 6,
    'short': 7,
    'signed': 8,
    'struct': 9,
    'union': 10,
    'unsigned': 11,
    'void': 12,
    'for': 13,
    'do': 14,
    'while': 15,
    'continue': 16,
    'if': 17,
    'else': 18,
    'goto': 19,
    'switch': 20,
    'case': 21,
    'default': 22,
    'return': 23,
    'auto': 24,
    'extern': 25,
    'register': 26,
    'static': 27,
    'const': 28,
    'sizeof': 29,
    'typdef': 30,
    'volatile': 31,
    'break': 32,  # 关键字
    '+': 33,
    '-': 34,
    '*': 35,
    '/': 36,
    '=': 37,
    '|': 38,
    '&': 39,
    '!': 40,
    '>': 41,
    '<': 42,
    '&&': 43,
    '++': 44,
    '--': 45,
    '+=': 46,
    '-=': 47,
    '*=': 48,
    '/=': 49,
    '==': 50,
    '|=': 51,
    '&=': 52,
    '!=': 53,
    '>=': 54,
    '<=': 55,
    '>>=': 56,
    '<<=': 57,
    '||': 58,
    '%': 59,  # 运算符
    '>>': 60,
    '<<': 61,
    ',': 62,
    '(': 63,
    ')': 64,
    '{': 65,
    '}': 66,
    '[': 67,
    ']': 68,
    ';': 69,
    '//': 70,
    '/*': 71,
    '*/': 72,
    ':': 73,
    '.': 74,
    '\\': 75,  # 界符
    'constNum': 76,
    'charRealNum': 77,
    'string': 78,
    'id': 79
}  # 内码表
basic_arithmetic_operator = {
    '+', '-', '*', '=', '|', '&', '>', '<', '!', '%'
}  # 符号表
delimiters = {
    ';', ',', ':', '(', ')', '{', '}', '[', ']', '<', '>', '.', '\\'
}  # 界符表
error_type =['miss', 'more', 'no_code', 'no_type', 'no_keyWord']
error_info = {
    error_type[0]: "错误 %d: 第 %d 行缺少  %s  ;",
    error_type[1]: "错误 %d: 第 %d 行多余  %s  ;",
    error_type[2]: "错误 %d: 第 %d 行不能识别的字符  %s  ;",
    error_type[3]: "错误 %d: 第 %d 行没有 %s 的类型",
    error_type[4]: ""
}  # 错误信息格式列表
modifier = ['const', 'static', 'register', 'auto', 'volatile', 'unsigned']
s_type = ['char', 'int', 'double', 'float', 'short', 'long']
logic_sign = ['>', '<', '==', '!=', '>=', '<=']
last_keyword_code = 32
