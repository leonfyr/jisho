from re import fullmatch as fm
from time import time

### GLOBAL VARIABLES
DICT_PATH = "buta014.dic"
ENCODING = "shift_JIS"
TRANS = {
    "？": "?",
    "⋆": "*",
    "＊": "*",
    "【": "[",
    "】": "]",
    "「": "[",
    "」": "]",
    "『": "[",
    "』": "]",
    "＆": "&",
    "｜": "|",
    "！": "!",
    "（": "(",
    "）": ")",
    "《": "<",
    "》": ">",
    "＜": "<",
    "＞": ">",
    "＠": "@",
    "；": ";",
    "＝": "=",
    "“": "\"",
    "”": "\"",
    "‘": "\'",
    "’": "\'",
    "｛": "{",
    "｝": "}",
    "０": "0",
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "０": "0"

}

PI = 3.1415927 # 悄悄藏一个π

KANA = set("あいうえおかがきぎくぐけげこごさざしじすずせぜそぞただちぢつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもやゆよらりるれろわをんー")

ULETTER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LLETTER = set("abcdefghijklmnopqrstuvwxyz")

PUNC = set("?*[-]&|!()<>@;=\"\'{}")

NUM = set("0123456789")

ALLOW = KANA | ULETTER | LLETTER | PUNC | NUM

# x for [aa], q for [nn]
L2K = {
    "x": "あいうえお",
    "k": "かきくけこ",
    "s": "さしすせそ",
    "t": "たちつてと",
    "n": "なにぬねの",
    "h": "はひふへほ",
    "m": "まみむめも",
    "y": "やゆよ",
    "r": "らりるれろ",
    "w": "わを",
    "g": "がぎぐげご",
    "z": "ざじずぜぞ",
    "d": "だぢづでど",
    "b": "ばびぶべぼ",
    "p": "ぱぴぷぺぽ",
    "a": "あかさたなはまやらわがざだばぱ",
    "i": "いきしちにひみりぎじぢびぴ",
    "u": "うくすつぬふむゆるぐずづぶぷ",
    "e": "えけせてねへめよれげぜでべぺ",
    "o": "おこそとのほもよろをごぞどぼぽ",
    "q": "ん"
}

TIME_LIMIT = 20 # 20s

for i in ALLOW:
    TRANS[i] = i

# Read File
with open(DICT_PATH, 'r', encoding = ENCODING) as f:
    file = f.readlines()
dict = [i.strip() for i in file]

# Hash Table
hasht = {}
for i in dict:
    hasht[hash(i)] = i

### END

class JishoSearcher():
    def  __init__(self, lang:str="zh_CN"):
        # Language Setup
        # TODO: i18n support
        self.supported_lang = ["zh_CN"]
        if lang in self.supported_lang:
            self.lang = lang
        else:
            return "#ERR #Language Not Supported!"


    # Raise An Error
    def _error(self, text:str, ex:str="") -> str: # ex: explain
        # TODO: Error Message Stored Exclusively
        # TODO: More specific syntax error
        res = "#ERR #"
        match text:
            case "empty":
                res += "空表达式"
            case "normalizerange":
                res += "非法字符"
            case "syntax":
                res += "不受支持的语法"
            case "noiterator":
                res += "代数式匹配需要至少一个表达式包含全部的字母"
            case "timeout":
                res += "超时"
            case "bracket":
                res += "括号不匹配"

        res += ":" + ex

        return res
    
    # Normalization
    def _normalize(self, expr:str) -> str:
        # Remove brackets with no text in it
        expr = expr.replace("()", "").replace("{}","")
        expr = expr.replace("<>", "").replace("[]", "")

        inbracketround = 0
        inbracketsquare = 0
        inbracketangle = 0
        inbracketcurly = 0
        inbracket = True # square, angle, curly
        normalized = [' ']

        for c in expr:
            inbracket = bool(inbracketsquare + inbracketangle + inbracketcurly)
            if c == ' ' or c == '\n':
                continue
            
            try:
                c = TRANS[c] # Translate
            except KeyError:
                # Some character is not allowed
                return self._error("normalizerange",ex=c)

            ### START BRACKET
            if c == '[':
                if inbracket:
                    return self._error("bracket")
                inbracketsquare += 1
                if normalized[-1] != '*' and normalized[-1] != '?' and normalized[-1] != '}':
                    return self._error("syntax", ex="[]前应有通配符")
                normalized.append(c)
                
            elif c == ']':
                if not bool(inbracketsquare):
                    return self._error("bracket")
                inbracketsquare -= 1
                normalized.append(c)

            elif c == '(':
                if bool(inbracketangle) or bool(inbracketcurly):
                    return self._error("bracket")
                inbracketround += 1
                normalized.append(c)
            elif c == ')':
                if not bool(inbracketround):
                    return self._error("bracket")
                inbracketround -= 1
                normalized.append(c)

            elif c == '<':
                if inbracket:
                    return self._error("bracket")
                inbracketangle += 1
                normalized.append(c)
            elif c == '>':
                if not bool(inbracketangle):
                    return self._error("bracket")
                inbracketangle -= 1
                normalized.append(c)

            elif c == '{':
                if inbracket:
                    return self._error("bracket")
                inbracketcurly += 1
                if normalized[-1] != '*' and normalized[-1] != ']':
                    return self._error("syntax", ex="{}前应有通配符".format(c))
                normalized.append(c)

            elif c == '}':
                if not bool(inbracketcurly):
                    return self._error("bracket")
                inbracketcurly -= 1
                normalized.append(c)

            ### END BRACKET

            elif c.isalpha(): # kana + letters
                if inbracketcurly:
                    if c == 'ー':
                        normalized.append('-')
                    else:
                        return self._error("syntax", ex="{}内不允许字母")
                elif inbracketsquare:
                    normalized.append(c.lower())
                else:
                    normalized.append(c.upper())

            elif c in NUM:
                if inbracketsquare or inbracketangle:
                    return self._error("syntax")
                
                normalized.append(c)

            else: # other characters
                normalized.append(c)

            
        expr = "".join(normalized[1:])
        if inbracketround or inbracketsquare or inbracketangle or inbracketcurly:
            return self._error("bracket")
        
        return expr
        

    def _indict(self, expr:str) -> bool:
        try:
            return (hasht[hash(expr)] == expr)
        except KeyError: # not in the hash table
            return False

    def _permutation(self, expr: str):
        # Permutation of the expression
        if len(expr) == 1:
            return [expr]
        res = []
        for i in range(len(expr)):
            tmp = self._permutation(expr[:i] + expr[i+1:])
            for j in tmp:
                res.append(expr[i] + j)

        res = list(set(res)) # unique
        return res
    
    def _union(self, a:str, b:str) -> str:
        return ''.join(set(a) | set(b))
    
    def _intersection(self, a:str, b:str) -> str:
        return ''.join(set(a) & set(b))
    
    def _complement(self, a:str) -> str:
        return ''.join(set(KANA) - set(a))
    
    def _letter2kanas(self, a:str):
        pass

    def _splitter_re(self, expr, format):
        length = format[0]
        if len(format) == 1:
            if length > 0 and len(expr) != length: # length not match
                return
            elif length < 0 and len(expr) < -length:
                return
            else: # length match, recording the answer
                self._splitter_ans.append(self._splitter_stack + [expr,])
                return
        else:
            if length > 0:
                if len(expr) < length:
                    return
                else:
                    self._splitter_stack.append(expr[:length])
                    self._splitter_re(expr[length:], format[1:])
                    self._splitter_stack.pop()
                    return
            else:
                # why -length
                # -> consider the minimum length
                for i in range(-length, len(expr)+1):
                    self._splitter_stack.append(expr[:i])
                    self._splitter_re(expr[i:], format[1:])
                    self._splitter_stack.pop()

    def _splitter(self, expr, format):  # split the expr according to the format, the length limit is set by `format`
        # 2 means length = 2
        # -2 means length >= 2
        self._splitter_stack = []
        self._splitter_ans = []
        self._splitter_re(expr, format)
        return self._splitter_ans

    ### Handle the brackets
    def _curly(self, expr:str) -> str:
        if expr == "":
            return ""
        else:
            expr = expr.replace('-',',')
            for i in expr.split(','):
                if i == "":
                    continue
                if not i.isdigit() or int(i) < 0 or int(i) > 10:
                    return self._error("syntax", ex=expr)
            return "{" + expr + "}"
        
    
    def _square(self, expr:str):
        if expr == "":
            return ""
        if expr[0] == '(' and expr[-1] == ')':
            level = 1
            for i in range(1, len(expr)-1):
                if expr[i] == '(':
                    level += 1
                elif expr[i] == ')':
                    level -= 1
                if level == 0:
                    break
            if level != 0:
                expr = expr[1:-1]

        # Find &|
        inbracket = 0
        opt = -1
        for i in range(len(expr)):
            if opt == "(":
                inbracket += 1
            elif expr[i] == ")":
                inbracket -= 1
            if inbracket == 0 and (opt == -1 and (expr[i] == '&' or expr[i] == '|')):
                opt = i
                break
            
        if opt != -1: # Found
            left = self._square(expr[:opt])
            right = self._square(expr[opt+1:])
            if left[0] == "#" or right[0] == "#":
                return left if left[0] == "#" else right
            return self._intersection(left, right) if expr[opt] == '&' else self._union(left, right)

        elif expr[0] == '!': #not
            text = self._square(expr[1:])
            if text[0] == "#": # Error
                return text
            else:
                return self._complement(text)

        else: # normal
            expr = expr.replace("aa", 'x').replace("nn",'q')
            res = ""
            try:
                for i in expr:
                    if i in KANA:
                        res = self._union(res, i)
                    else:
                        res = self._union(res, L2K[i])
            except:
                return self._error("syntax", ex=expr)
            
            return res

    def _bracket(self, expr:str):
        # Process the brackets
        # _square + _curly

        # one bracket only
        if expr.count('[') > 1 or expr.count('{') > 1:
            return self._error("syntax", ex=expr)
        
        res = ""
        if expr.count('[') == 1:
            res += '['
            res += self._square(expr[expr.find('[')+1:expr.find(']')])
            res += ']'
        if expr.count('{') == 1:
            res += self._curly(expr[expr.find('{')+1:expr.find('}')])
        
        return res

    ###

    def _ex2re(self, expr:str) -> str:
        if '<' in expr: # rearrange
            words = []
            i = 0
            while i < len(expr):
                if expr[i] == '<': # rearrange
                    j = i+1
                    while j < len(expr) and expr[j] != '>':
                        j += 1
                    words.append(self._permutation(expr[i+1:j].replace('?','.')))
                    i = j + 1
                else: # normal
                    j = i+1
                    while j < len(expr) and expr[j] != '<':
                        j += 1
                    text = self._ex2re(expr[i:j])
                    if text[0] == '#': # ERR
                        return text
                    words.append(text)
                    i = j

            # Combine
            #print(words)
            res = []
            pointer = 0

            if type(words[0]) == list: # first <>
                res.append("")

            while pointer < len(words):
                #print(res)
                if type(words[pointer]) == list: # <>
                    res2 = []
                    for i in res:
                        for j in words[pointer]:
                            res2.append(i+j)
                    res = res2

                elif type(words[pointer]) == str: # normal
                    res2 = []
                    for i in res:
                        res2.append(i+words[pointer])
                    res = res2
                pointer += 1
                    
            return ['|', res]
        
        else: # normal case
            res = ""
            i = 0
            while i < len(expr):
                if expr[i] == '?' or expr[i] == "*":

                    ### READ BRACKET
                    j = i + 1
                    
                    while True:
                        if j == len(expr):
                            break
                        iscurly = False
                        if expr[j] == '{':
                            iscurly = True
                        elif expr[j] == '[':
                            iscurly = False
                        else:
                            break

                        while (iscurly and expr[j] != '}') or (not iscurly and expr[j] != ']'):
                            j += 1
                            if j == len(expr):
                                break
                        j += 1
                    ###

                    if j == i + 1: # No Bracket
                        if expr[i] == '?':
                            res += '.'
                        else:
                            res += '.*'

                    else: # Handle Bracket
                        bracket = self._bracket(expr[i+1:j])
                        if bracket[0] == "#": # Error
                            return bracket
                        
                        if expr[i] == '?':
                            if '{' in bracket:
                                return self._error("syntax", ex=expr[i:j])
                            elif '[' in bracket:
                                res += bracket
                            else:
                                return self._error("syntax", ex=expr[i:j])
                        elif expr[i] == '*': # expr[i] == "*"
                            if '[' in bracket:
                                if '{' in bracket:
                                    res += bracket
                                else:
                                    res += bracket + '*'
                            else:
                                if '{' in bracket:
                                    res += '.' + bracket
                    i = j

                else:
                    res += expr[i]
                    i += 1

            return res

    # Expression -> re
    def _breakup(self, expr:str):
        #print(expr)
        if expr == "": # expr shouldn't be empty
            return self._error("empty")
        
        # Remove the parenthesis
        while expr[0] == '(' and expr[-1] == ')':
            level = 1
            for i in range(1, len(expr)-1):
                if expr[i] == '(':
                    level += 1
                elif expr[i] == ')':
                    level -= 1
                if level == 0:
                    break
            if level != 0:
                expr = expr[1:-1]
        #print(expr)
        # find global &|
        inbracketsquare = 0
        inbracketround = 0
        ands = []
        ors = []
        for i in range(len(expr)):
            if expr[i] == '[':
                inbracketsquare += 1
            elif expr[i] == ']':
                inbracketsquare -= 1
            elif expr[i] == '(':
                inbracketround += 1
            elif expr[i] == ')':
                inbracketround -= 1
            if not bool(inbracketsquare) and not bool(inbracketround):
                if expr[i] == '&':
                    ands.append(i)
                elif expr[i] == '|':
                    ors.append(i)

        #print(ands,ors)

        # OR
        if len(ors) > 0:
            #print(1)
            exprs = []
            last = 0
            for i in ors:
                text = self._breakup(expr[last:i])
                if text[0] == "#": # Error
                    return text
                exprs.append(text)
                last = i+1
            exprs.append(self._breakup(expr[last:]))
            return ['|', exprs]
        
        # AND
        elif len(ands) > 0:
            #print(2)
            exprs = []
            last = 0
            for i in ands:
                text = self._breakup(expr[last:i])
                if text[0] == "#": # Error
                    return text
                exprs.append(text)
                last = i+1
            exprs.append(self._breakup(expr[last:]))
            return ['&', exprs]
        
        # NOT
        elif expr[0] == "!":
            #print(3)
            return ["!", [self._breakup(expr[1:]), ]]
        
        # normal case
        else:
            #print(4)
            return self._ex2re(expr)

    # fullmatch
    def _fm(self, expr, word):
        if type(expr) == str:
            if expr == "@":
                return self._indict(word)
            elif "@" in expr:
                exprs = [] # break down 
                counter = 0
                while counter < len(expr):
                    if expr[counter] == "@":
                        exprs.append("@")
                        counter += 1
                    else:
                        begin = counter
                        while counter < len(expr) and expr[counter] != "@":
                            counter += 1
                        exprs.append(expr[begin:counter])

                format = [-2 if i == "@" else 0 for i in exprs]
                
                split = self._splitter(word, format)
                # print(split)
                if split == []:
                    return False
                
                for i in split:
                    counter = 0
                    flag = True
                    for j in range(len(i)):
                        temp = self._fm(exprs[j], i[j])
                        # print(temp)
                        flag &= temp

                    if flag == True:
                        # print("/")
                        return True
                    
                # print("/")
                return False
                    
                
            else: # normal cases
                return fm(expr, word) != None
        else:
            opt = expr[0]
            exprs = expr[1] # a list of expressions
            if opt == '&':
                for i in exprs:
                    if self._fm(i, word) == False:
                        return False
                return True
            elif opt == '|':
                for i in exprs:
                    if self._fm(i, word) == True:
                        return True
                return False
            elif opt == '!':
                return not self._fm(exprs[0], word)
            

    # Search
    def search(self, expr: str, num:int = 200) -> str:
        # Empty
        if expr == "":
            return self._error("empty")
        
        expr = self._normalize(expr)
        if expr[0] == '#': # ERR
            return expr

        # Process
        #  QAT QAQ
        if ';' in expr:
            exprs = expr.split(";")

            # Delete Empty Expressions
            for i in range(len(exprs)-1, 0, -1):
                if exprs[i] == "":
                    del exprs[i]
            if exprs == []:
                return self._error("empty")
            
            # Register Existed Letters
            self.qat_letters = [0 for i in range(26)]
            # 0 : not exist, -1 : exist
            for i in exprs:
                for j in range(26):
                    if chr(j+65) in i:
                        self.qat_letters[j] = -1

            # Find Length Limitation
            iterator = -1
            for i in range(len(exprs)-1, -1, -1):
                if '=' in exprs[i]: # Fixed Length
                    condition = exprs[i].split('=')
                    # Check format
                    if len(condition) != 2 or \
                        not condition[1].isnumeric() or \
                        len(condition[0]) != 3 or \
                        condition[0][0] != '|'or \
                        condition[0][2] != '|':
                        return self._error("syntax", ex=exprs[i])
                    
                    # Check value
                    if not (0 <= ord(condition[0][1])-ord('A') < 26) or \
                        not (0 < int(condition[1]) < 10):
                        return self._error("syntax", ex=exprs[i])

                    if self.qat_letters[ord(condition[0][1])-ord('A')] != -1: # defined
                        return self._error("syntax", ex=exprs[i])

                    self.qat_letters[ord(condition[0][1])-ord('A')] = int(condition[1])

                    del exprs[i] # Delete the expression
            
            # sort, putting the expression with global &|! last
            
            for i in range(len(exprs)-1, -1, -1):
                # find global &|
                inbracketsquare = 0
                inbracketround = 0
                flag = False
                for j in range(len(expr[i])):
                    if expr[i][j] == '[':
                        inbracketsquare += 1
                    elif expr[i][j] == ']':
                        inbracketsquare -= 1
                    elif expr[i][j] == '(':
                        inbracketround += 1
                    elif expr[i][j] == ')':
                        inbracketround -= 1
                    if not bool(inbracketsquare) and not bool(inbracketround):
                        if expr[i][j] in ['&', '|', '!']:
                            flag = True
                            break
                if flag:
                    exprs.append(exprs[i])
                    del exprs[i]
            
            print(exprs[i])
            return "123"

            letter_num = sum([(i != 0) for i in self.qat_letters]) # number of letters
            
            if letter_num != 0: # QAT
                if iterator == -1: # Cannot find an iterator QAQ
                    # TODO: QAT without iterator
                    return self._error("noiterator")
                
                

            else: # No letters, Special Case (combination of non-qat solutions)
                res = []
                start_time = time()

                # Search for each expression
                for i in range(len(exprs)):
                    expr_re = self._breakup(exprs[i])
                    if expr_re[0] == "#": # Error
                        return expr_re
                    
                    subres = []

                    # Search
                    for j in dict:
                        if self._fm(expr_re, j) == True: # Match
                            subres.append(j)
                            if len(subres) == num:
                                break

                        if time() - start_time > TIME_LIMIT: # timeout
                            return self._error("timeout")
                        
                    # Store
                    res.append(subres)

                # Combine
                answer = []
                for i in range(num):
                    tmp = ""
                    
                    for j in range(len(exprs)):
                        if i < len(res[j]): # Available
                            tmp += res[j][i] + ";"
                        else:
                            tmp = "#" + tmp

                    if tmp[0] == "#" or tmp == "": # No more answers
                        break

                    answer.append(tmp[:-1])

                return answer
                

        #  Normal
        else:
            expr_re = self._breakup(expr)
            if expr_re[0] == "#": # Error
                return expr_re
            
            res = []
            res_len = 0
            start_time = time()
            for i in dict: # Search
                if self._fm(expr_re, i) == True: # Match
                    res_len += 1
                    res.append(i)
                    if res_len == num:
                        break

                if time() - start_time > TIME_LIMIT: # timeout
                    return self._error("timeout")

            return res

    def search_print(self, expr: str, num:int = 200) -> None: # print the result
        a = time()
        res = test.search(expr)
        print(f"Expr:{expr}")
        print(f"Found {len(res)} items in {time() - a:.2f} seconds:")

        for i in range(len(res)):
            print(res[i], end="")
            print(("\n" if (i%10) == 9 else "\t"),end="")
        
        print()

if __name__ == "__main__":
    print("你好")
    test = JishoSearcher()
    # expr = "abcd"
    # format = [0,-2, 0, 0]
    # for i in test._splitter(expr, format):
    #     print(i)
    # print(len(test._splitter(expr, format)))
    # flag = True
    # for i in dict:
    #     flag = test._indict(i) and flag
    # print(test._indict("awa"))
    test.search_print("AB;!JI;QW")
    #test.search_print("う＠AZう;！＊｛５ー｝＆＜あ＞＊｛１ー３｝「！o」い")
    #test.search_print("う＠う")
