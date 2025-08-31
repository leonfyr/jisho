import re

class JishoMatcher:
    def __init__(self, dictionary_file="word.dic"):
        # 加载词典
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            self.dictionary = [line.strip() for line in f]
        self.dictionary_set = set(self.dictionary)
        
        # 预计算满足@条件的词汇（前缀词）
        self.at_words_set = self._precompute_at_words()
        
        # 定义行和段的映射
        self._init_property_mappings()
    
    def _precompute_at_words(self):
        """预计算所有满足@条件的词汇（即存在后缀词，使前缀+后缀成词）"""
        at_words = set()
        for word in self.dictionary:
            for i in range(1, len(word)):
                prefix = word[:i]
                suffix = word[i:]
                if prefix in self.dictionary_set and suffix in self.dictionary_set:
                    at_words.add(prefix)
        return at_words
    
    def _init_property_mappings(self):
        """初始化假名的行和段映射关系"""
        # 行映射（清音、浊音、半浊音）
        rows = {
            'aa': 'あいうえお',  # あ行
            'k': 'かきくけこ',   # か行
            's': 'さしすせそ',   # さ行
            't': 'たちつてと',   # た行
            'n': 'なにぬねの',   # な行
            'h': 'はひふへほ',   # は行
            'm': 'まみむめも',   # ま行
            'y': 'やゆよ',       # や行
            'r': 'らりるれろ',   # ら行
            'w': 'わを',         # わ行
            'g': 'がぎぐげご',   # が行
            'z': 'ざじずぜぞ',   # ざ行
            'd': 'だぢづでど',   # だ行
            'b': 'ばびぶべぼ',   # ば行
            'p': 'ぱぴぷぺぽ',   # ぱ行
        }
        
        # 段映射（基于假名的元音）
        dans = {'a': set(), 'i': set(), 'u': set(), 'e': set(), 'o': set()}
        for chars in rows.values():
            for c in chars:
                if c.endswith('あ') or c in 'わは': dans['a'].add(c)
                if c.endswith('い'): dans['i'].add(c)
                if c.endswith('う') or c in 'ゆふ': dans['u'].add(c)
                if c.endswith('え'): dans['e'].add(c)
                if c.endswith('お') or c in 'を': dans['o'].add(c)
        
        self.rows = rows
        self.dans = dans
    
    def _property_to_set(self, property_str):
        """将属性表达式（如[ks]）转换为字符集"""
        if property_str == 'nn':
            return {'ん'}
        if property_str == 'aa':
            return set(self.rows['aa'])
        
        char_set = set()
        for code in property_str:
            if code in self.dans:  # 段属性
                char_set |= self.dans[code]
            elif code in self.rows:  # 行属性
                char_set |= set(self.rows[code])
            else:
                raise ValueError(f"无效属性代码: {code}")
        return char_set
    
    def _tokenize_base(self, s):
        """将基础表达式拆分为令牌序列（字面量、通配符、属性匹配）"""
        tokens = []
        i = 0
        while i < len(s):
            if s[i] == '?':
                tokens.append(('wildcard', '?'))
                i += 1
            elif s[i] == '*':
                if i + 1 < len(s) and s[i + 1] == '[':
                    j = i + 2
                    while j < len(s) and s[j] != ']':
                        j += 1
                    if j >= len(s) or s[j] != ']':
                        raise ValueError("未闭合的*[]范围")
                    range_str = s[i + 2:j]
                    parts = range_str.split('-', 1)
                    if not parts or len(parts) > 2:
                        raise ValueError(f"无效范围表达式: {range_str}")
                    min_len = parts[0].strip() or '0'
                    max_len = parts[1].strip() if len(parts) > 1 and parts[1] else ''
                    try:
                        min_val = int(min_len) if min_len else 0
                        max_val = int(max_len) if max_len else ''
                    except ValueError:
                        raise ValueError(f"范围必须为整数: {range_str}")
                    tokens.append(('star_range', (min_val, max_val)))
                    i = j + 1
                else:
                    tokens.append(('wildcard', '*'))
                    i += 1
            elif s[i] == '[':
                j = i + 1
                while j < len(s) and s[j] != ']':
                    j += 1
                if j >= len(s) or s[j] != ']':
                    raise ValueError("未闭合的属性表达式")
                prop_str = s[i + 1:j]
                tokens.append(('property', prop_str))
                i = j + 1
            else:  # 字面量（假名）
                start = i
                while i < len(s) and s[i] not in ['?', '*', '[', ']']:
                    i += 1
                lit = s[start:i]
                if lit:
                    tokens.append(('literal', lit))
        return tokens
    
    def _base_to_regex(self, base_expr):
        """将基础表达式转换为正则表达式"""
        tokens = self._tokenize_base(base_expr)
        regex_parts = []
        for token_type, value in tokens:
            if token_type == 'literal':
                regex_parts.append(re.escape(value))
            elif token_type == 'wildcard':
                regex_parts.append('.' if value == '?' else '.*')
            elif token_type == 'star_range':
                min_val, max_val = value
                if max_val == '':
                    regex_parts.append(f'.{{{min_val},}}')  # *[n-]
                elif min_val == '':
                    regex_parts.append(f'.{{0,{max_val}}}')  # *[-n]
                else:
                    regex_parts.append(f'.{{{min_val},{max_val}}}')  # *[m-n]
            elif token_type == 'property':
                char_set = self._property_to_set(value)
                if not char_set:
                    raise ValueError(f"属性表达式 {value} 生成空字符集")
                regex_parts.append(f'[{"".join(re.escape(c) for c in char_set)}]')
        return f'^{"".join(regex_parts)}$'
    
    def match(self, query):
        """执行查询，返回匹配的词汇列表"""
        # 预处理：全角符号转半角
        full_to_half = {
            '？': '?', '（': '(', '）': ')', '＜': '<', '＞': '>',
            '！': '!', '＆': '&', '＠': '@', '［': '[', '］': ']'
        }
        query = ''.join(full_to_half.get(c, c) for c in query)
        
        # 检查并报错不支持的语法
        if re.search(r'[;<>]', query):
            raise NotImplementedError("暂不支持代数式匹配和重排操作")
        
        # 分割复合表达式（|）
        parts = []
        start = 0
        depth = 0  # 括号嵌套深度
        for i, char in enumerate(query):
            if char == '(':
                depth += 1
            elif char == ')':
                if depth > 0:
                    depth -= 1
            elif char == '|' and depth == 0:
                parts.append(query[start:i])
                start = i + 1
        parts.append(query[start:])
        
        # 处理每个子表达式
        all_matches = set()
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # 检查成词条件（@）
            has_at_cond = part.endswith('@')
            base_expr = part[:-1] if has_at_cond else part
            
            # 转换为正则表达式
            try:
                regex_str = self._base_to_regex(base_expr)
                pattern = re.compile(regex_str)
            except Exception as e:
                raise ValueError(f"表达式解析错误: {part} - {str(e)}")
            
            # 匹配词典
            for word in self.dictionary:
                if pattern.match(word):
                    if has_at_cond:
                        if word in self.at_words_set:
                            all_matches.add(word)
                    else:
                        all_matches.add(word)
        
        return sorted(all_matches)

# 测试代码
if __name__ == "__main__":
    # 创建测试词典
    test_words = [
        "あい", "あお", "あう", "あか", "あき", "あく", "あけ", "あこ",  # あ行
        "かき", "かく", "かこ", "かあ",  # か行
        "さし", "さす", "させ", "さそ",  # さ行
        "たち", "たつ", "たて", "たと",  # た行
        "はは", "はひ", "はへ",  # は行
        "やゆ", "やよ",  # や行
        "わを",  # わ行
        "がぎ", "がぐ", "がご",  # が行
        "ざじ", "ざず", "ざぞ",  # ざ行
        "だぢ", "だづ", "だど",  # だ行
        "ばび", "ばぶ", "ばぼ",  # ば行
        "ぱぴ", "ぱぷ", "ぱぽ",  # ぱ行
        "さん", "しん", "にん",  # ん
        "そと", "そとで", "で",  # 成词条件测试
    ]
    with open("test_word.dic", "w", encoding="utf-8") as f:
        for word in test_words:
            f.write(f"{word}\n")
    
    # 初始化匹配器
    jm = JishoMatcher("test_word.dic")
    
    # 测试用例
    tests = [
        ("あ?", ["あい", "あお", "あう", "あか", "あき", "あく", "あけ", "あこ"]),
        ("?[k]", ["あか", "あき", "あく", "あけ", "あこ", "かき", "かく", "かこ", "かあ"]),
        ("*[1-2&k]", ["かき", "かく", "かこ", "かあ"]),
        ("そと@", ["そとで"]),  # そと+で=そとで 是词汇
        ("*[1-2&s]", ["さし", "さす", "させ", "さそ"]),
        ("[ae]?", ["あい", "あお", "あう", "あか", "あき", "あく", "あけ", "あこ", "かあ", "さん"]),
        ("?[!あのみ]", ["あき", "あく", "あけ", "かき", "かく", "かこ", "かあ", "さし", "さす", "させ", "さそ", "たち", "たつ", "たて", "たと", "はは", "はひ", "はへ", "やゆ", "やよ", "わを", "がぎ", "がぐ", "がご", "ざじ", "ざず", "ざぞ", "だぢ", "だづ", "だど", "ばび", "ばぶ", "ばぼ", "ぱぴ", "ぱぷ", "ぱぽ", "さん", "しん", "にん", "そと", "そとで", "で"]),
        ("あ?|か?", ["あい", "あお", "あう", "あか", "あき", "あく", "あけ", "あこ", "かき", "かく", "かこ", "かあ"]),
    ]
    
    # 运行测试
    for i, (query, expected) in enumerate(tests):
        try:
            result = jm.match(query)
            result_sorted = sorted(result)
            expected_sorted = sorted(expected)
            assert result_sorted == expected_sorted, f"测试失败: {query} -> 得到 {result_sorted}, 预期 {expected_sorted}"
            print(f"测试 {i+1} 通过: {query} -> 匹配 {len(result)} 个词汇")
        except Exception as e:
            print(f"测试 {i+1} 失败: {query} - {str(e)}")
    
    # 测试错误输入
    error_tests = [
        "?[1-2]",  # ?不能带长度
        "*[a]",    # 无效范围
        "[xyz]",   # 无效属性代码
        "<あ>",    # 不支持重排
        "AB;",     # 不支持代数式
    ]
    for query in error_tests:
        try:
            jm.match(query)
            print(f"错误测试失败: {query} 未引发异常")
        except Exception as e:
            print(f"错误测试通过: {query} -> {str(e)}")

# 注意：实际使用时应指定真实词典文件
# jm = JishoMatcher("word.dic")
# results = jm.match("そと@")
# print(results)