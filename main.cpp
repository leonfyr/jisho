#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <regex>
#include <algorithm>
#include <chrono>
#include <memory>
#include <cctype>
#include <sstream>
#include <map>
#include <set>

using namespace std;

const string DICT_PATH = "jisho.dic";
const string ENCODING = "shift_JIS";

unordered_map<string, string> TRANS = {
    {"？", "?"},
    {"⋆", "*"},
    {"＊", "*"},
    {"【", "["},
    {"】", "]"},
    {"「", "["},
    {"」", "]"},
    {"『", "["},
    {"』", "]"},
    {"＆", "&"},
    {"｜", "|"},
    {"！", "!"},
    {"（", "("},
    {"）", ")"},
    {"《", "<"},
    {"》", ">"},
    {"＜", "<"},
    {"＞", ">"},
    {"＠", "@"},
    {"；", ";"},
    {"＝", "="},
    {"“", "\""},
    {"”", "\""},
    {"‘", "'"},
    {"’", "'"},
    {"｛", "{"},
    {"｝", "}"},
    {"０", "0"},
    {"１", "1"},
    {"２", "2"},
    {"３", "3"},
    {"４", "4"},
    {"５", "5"},
    {"６", "6"},
    {"７", "7"},
    {"８", "8"},
    {"９", "9"}
};

const double PI = 3.1415927;

unordered_set<char> KANA = {
    'あ','い','う','え','お','か','が','き','ぎ','く','ぐ','け','げ','こ','ご',
    'さ','ざ','し','じ','す','ず','せ','ぜ','そ','ぞ','た','だ','ち','ぢ','つ','づ',
    'て','で','と','ど','な','に','ぬ','ね','の','は','ば','ぱ','ひ','び','ぴ','ふ',
    'ぶ','ぷ','へ','べ','ぺ','ほ','ぼ','ぽ','ま','み','む','め','も','や','ゆ','よ',
    'ら','り','る','れ','ろ','わ','を','ん','ー'
};

unordered_set<char> ULETTER = {
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
};

unordered_set<char> LLETTER = {
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'
};

unordered_set<char> PUNC = {
    '?','*','[',']','&','|','!','(',')','<','>','@',';','=','\"','\'','{','}'
};

unordered_set<char> NUM = {
    '0','1','2','3','4','5','6','7','8','9'
};

unordered_set<char> ALLOW = []() {
    unordered_set<char> result;
    result.insert(KANA.begin(), KANA.end());
    result.insert(ULETTER.begin(), ULETTER.end());
    result.insert(LLETTER.begin(), LLETTER.end());
    result.insert(PUNC.begin(), PUNC.end());
    result.insert(NUM.begin(), NUM.end());
    return result;
}();

unordered_map<string, string> L2K = {
    {"x", "あいうえお"},
    {"k", "かきくけこ"},
    {"s", "さしすせそ"},
    {"t", "たちつてと"},
    {"n", "なにぬねの"},
    {"h", "はひふへほ"},
    {"m", "まみむめも"},
    {"y", "やゆよ"},
    {"r", "らりるれろ"},
    {"w", "わを"},
    {"g", "がぎぐげご"},
    {"z", "ざじずぜぞ"},
    {"d", "だぢづでど"},
    {"b", "ばびぶべぼ"},
    {"p", "ぱぴぷぺぽ"},
    {"a", "あかさたなはまやらわがざだばぱ"},
    {"i", "いきしちにひみりぎじぢびぴ"},
    {"u", "うくすつぬふむゆるぐずづぶぷ"},
    {"e", "えけせてねへめよれげぜでべぺ"},
    {"o", "おこそとのほもよろをごぞどぼぽ"},
    {"q", "ん"}
};

const int TIME_LIMIT = 20;

vector<string> dict;
unordered_map<size_t, string> hasht;
unordered_map<int, vector<string>> dict_by_length;
unordered_map<char, vector<string>> dict_by_first_char;

class ConfigParser {
private:
    unordered_map<string, unordered_map<string, string>> data;
    string current_section;

public:
    void read(const string& filename, const string& encoding = "utf-8") {
        ifstream file(filename);
        if (!file.is_open()) {
            return;
        }

        string line;
        while (getline(file, line)) {
            // Remove BOM if present
            if (!line.empty() && static_cast<unsigned char>(line[0]) == 0xEF && 
                line.size() >= 3 && static_cast<unsigned char>(line[1]) == 0xBB && 
                static_cast<unsigned char>(line[2]) == 0xBF) {
                line = line.substr(3);
            }

            // Trim whitespace
            line.erase(0, line.find_first_not_of(" \t\r\n"));
            line.erase(line.find_last_not_of(" \t\r\n") + 1);

            if (line.empty() || line[0] == ';' || line[0] == '#') {
                continue;
            }

            if (line[0] == '[' && line.back() == ']') {
                current_section = line.substr(1, line.size() - 2);
                data[current_section] = unordered_map<string, string>();
            } else {
                size_t pos = line.find('=');
                if (pos != string::npos) {
                    string key = line.substr(0, pos);
                    string value = line.substr(pos + 1);
                    
                    // Trim
                    key.erase(0, key.find_first_not_of(" \t"));
                    key.erase(key.find_last_not_of(" \t") + 1);
                    value.erase(0, value.find_first_not_of(" \t"));
                    value.erase(value.find_last_not_of(" \t") + 1);
                    
                    if (!current_section.empty()) {
                        data[current_section][key] = value;
                    }
                }
            }
        }
    }

    string get(const string& section, const string& key) {
        if (data.find(section) != data.end() && data[section].find(key) != data[section].end()) {
            return data[section][key];
        }
        return "";
    }
};

ConfigParser config;

class JishoSearcher {
private:
    string lang;
    unordered_map<string, string> _pattern_cache;
    unordered_map<string, vector<string>> _result_cache;
    
    // QAT related members
    vector<string> qat_exprs;
    vector<int> qat_letters;
    vector<string> qat_current_letters;
    vector<string> qat_current_answer;
    int qat_num_limit;
    chrono::steady_clock::time_point qat_start_time;
    vector<string> qat_answers;
    string qat_error;
    bool stop;
    
    // Splitter related members
    vector<string> _splitter_stack;
    vector<vector<string>> _splitter_ans;

public:
    JishoSearcher(const string& lang = "en") : lang(lang), stop(false) {
        // Initialize TRANS with ALLOW characters
        for (char c : ALLOW) {
            TRANS[string(1, c)] = string(1, c);
        }
        
        // Read dictionary file
        ifstream file(DICT_PATH);
        if (!file.is_open()) {
            cerr << "Error: Cannot open dictionary file: " << DICT_PATH << endl;
            return;
        }
        
        string line;
        while (getline(file, line)) {
            // Remove BOM if present and trim
            if (!line.empty() && static_cast<unsigned char>(line[0]) == 0xEF && 
                line.size() >= 3 && static_cast<unsigned char>(line[1]) == 0xBB && 
                static_cast<unsigned char>(line[2]) == 0xBF) {
                line = line.substr(3);
            }
            
            line.erase(0, line.find_first_not_of(" \t\r\n"));
            line.erase(line.find_last_not_of(" \t\r\n") + 1);
            
            if (!line.empty()) {
                dict.push_back(line);
            }
        }
        
        // Build hash table
        for (const auto& word : dict) {
            hash<string> hasher;
            hasht[hasher(word)] = word;
        }
        
        // Build indices
        for (const auto& word : dict) {
            // Index by length
            int length = word.length();
            dict_by_length[length].push_back(word);
            
            // Index by first character
            if (!word.empty()) {
                char first_char = word[0];
                dict_by_first_char[first_char].push_back(word);
            }
        }
        
        // Read config
        config.read("./i18n.cfg", "utf-8");
        
        // Initialize QAT letters
        qat_letters.resize(26, 0);
        qat_current_letters.resize(26, "");
    }

private:
    string _error(const string& text, const string& ex = "") {
        string res = "#" + config.get(lang, text);
        if (!ex.empty()) {
            res += ":" + ex;
        }
        return res;
    }

    string _normalize(const string& expr) {
        if (expr.empty()) {
            return _error("empty");
        }
        
        vector<int> bracket_counts = {0, 0, 0, 0}; // round, square, angle, curly
        string normalized;
        
        for (char c : expr) {
            if (c == ' ' || c == '\n') {
                continue;
            }
            
            // Translate using dictionary lookup
            string c_str(1, c);
            if (TRANS.find(c_str) != TRANS.end()) {
                c_str = TRANS[c_str];
                c = c_str[0];
            }
            
            if (ALLOW.find(c) == ALLOW.end()) {
                return _error("normalizerange", string(1, c));
            }
            
            // Handle brackets
            switch (c) {
                case '[':
                    if (bracket_counts[1] > 0 || bracket_counts[2] > 0 || bracket_counts[3] > 0) {
                        return _error("bracket");
                    }
                    bracket_counts[1]++;
                    if (!normalized.empty() && normalized.back() != '*' && normalized.back() != '?' && normalized.back() != '}') {
                        return _error("syntax", string(1, normalized.back()));
                    }
                    normalized += c;
                    break;
                    
                case ']':
                    if (bracket_counts[1] <= 0) {
                        return _error("bracket");
                    }
                    bracket_counts[1]--;
                    normalized += c;
                    break;
                    
                case '(':
                    if (bracket_counts[2] > 0 || bracket_counts[3] > 0) {
                        return _error("bracket");
                    }
                    bracket_counts[0]++;
                    normalized += c;
                    break;
                    
                case ')':
                    if (bracket_counts[0] <= 0) {
                        return _error("bracket");
                    }
                    bracket_counts[0]--;
                    normalized += c;
                    break;
                    
                case '<':
                    if (bracket_counts[1] > 0 || bracket_counts[2] > 0 || bracket_counts[3] > 0) {
                        return _error("bracket");
                    }
                    bracket_counts[2]++;
                    normalized += c;
                    break;
                    
                case '>':
                    if (bracket_counts[2] <= 0) {
                        return _error("bracket");
                    }
                    bracket_counts[2]--;
                    normalized += c;
                    break;
                    
                case '{':
                    if (bracket_counts[1] > 0 || bracket_counts[2] > 0 || bracket_counts[3] > 0) {
                        return _error("bracket");
                    }
                    bracket_counts[3]++;
                    if (!normalized.empty() && normalized.back() != '*' && normalized.back() != ']') {
                        return _error("syntax", string(1, normalized.back()));
                    }
                    normalized += c;
                    break;
                    
                case '}':
                    if (bracket_counts[3] <= 0) {
                        return _error("bracket");
                    }
                    bracket_counts[3]--;
                    normalized += c;
                    break;
                    
                default:
                    if (isalpha(c)) {
                        if (bracket_counts[3] > 0) { // in curly brackets
                            if (c == 'ー') {
                                normalized += '-';
                            } else {
                                return _error("syntax", string(1, c));
                            }
                        } else if (bracket_counts[1] > 0) { // in square brackets
                            normalized += tolower(c);
                        } else {
                            normalized += toupper(c);
                        }
                    } else if (NUM.find(c) != NUM.end()) {
                        if (bracket_counts[1] > 0 || bracket_counts[2] > 0) {
                            return _error("syntax");
                        }
                        normalized += c;
                    } else {
                        normalized += c;
                    }
                    break;
            }
        }
        
        // Check for unclosed brackets
        if (bracket_counts[0] > 0 || bracket_counts[1] > 0 || bracket_counts[2] > 0 || bracket_counts[3] > 0) {
            return _error("bracket");
        }
        
        // Remove empty brackets
        string result = normalized;
        size_t pos;
        while ((pos = result.find("()")) != string::npos) result.replace(pos, 2, "");
        while ((pos = result.find("{}")) != string::npos) result.replace(pos, 2, "");
        while ((pos = result.find("<>")) != string::npos) result.replace(pos, 2, "");
        while ((pos = result.find("[]")) != string::npos) result.replace(pos, 2, "");
        
        return result;
    }

    bool _indict(const string& expr) {
        hash<string> hasher;
        return hasht.find(hasher(expr)) != hasht.end();
    }

    vector<string> _permutation(const string& expr) {
        if (expr.length() <= 1) {
            return {expr};
        }
        
        vector<string> result;
        string sorted_expr = expr;
        sort(sorted_expr.begin(), sorted_expr.end());
        
        do {
            result.push_back(sorted_expr);
        } while (next_permutation(sorted_expr.begin(), sorted_expr.end()));
        
        // Remove duplicates
        sort(result.begin(), result.end());
        result.erase(unique(result.begin(), result.end()), result.end());
        
        return result;
    }

    string _union(const string& a, const string& b) {
        unordered_set<char> chars;
        for (char c : a) chars.insert(c);
        for (char c : b) chars.insert(c);
        
        string result;
        for (char c : chars) result += c;
        return result;
    }

    string _intersection(const string& a, const string& b) {
        unordered_set<char> a_chars(a.begin(), a.end());
        string result;
        for (char c : b) {
            if (a_chars.find(c) != a_chars.end()) {
                result += c;
            }
        }
        return result;
    }

    string _complement(const string& a) {
        string result;
        for (char c : KANA) {
            if (a.find(c) == string::npos) {
                result += c;
            }
        }
        return result;
    }

    void _splitter_re(const string& expr, const vector<int>& format) {
        int length = format[0];
        if (format.size() == 1) {
            if (length > 0 && expr.length() != length) {
                return;
            } else if (length < 0 && expr.length() < -length) {
                return;
            } else {
                vector<string> new_entry = _splitter_stack;
                new_entry.push_back(expr);
                _splitter_ans.push_back(new_entry);
                return;
            }
        } else {
            if (length > 0) {
                if (expr.length() < length) {
                    return;
                } else {
                    _splitter_stack.push_back(expr.substr(0, length));
                    _splitter_re(expr.substr(length), vector<int>(format.begin() + 1, format.end()));
                    _splitter_stack.pop_back();
                    return;
                }
            } else {
                for (int i = -length; i <= (int)expr.length(); i++) {
                    _splitter_stack.push_back(expr.substr(0, i));
                    _splitter_re(expr.substr(i), vector<int>(format.begin() + 1, format.end()));
                    _splitter_stack.pop_back();
                }
            }
        }
    }

    vector<vector<string>> _splitter(const string& expr, const vector<int>& format) {
        _splitter_stack.clear();
        _splitter_ans.clear();
        _splitter_re(expr, format);
        return _splitter_ans;
    }

    string _curly(const string& expr) {
        if (expr.empty()) {
            return "";
        }
        
        string processed = expr;
        replace(processed.begin(), processed.end(), '-', ',');
        
        vector<string> parts;
        stringstream ss(processed);
        string part;
        while (getline(ss, part, ',')) {
            if (!part.empty()) {
                bool is_digit = true;
                for (char c : part) {
                    if (!isdigit(c)) {
                        is_digit = false;
                        break;
                    }
                }
                if (!is_digit || stoi(part) < 0 || stoi(part) > 10) {
                    return _error("syntax", expr);
                }
            }
        }
        
        return "{" + expr + "}";
    }

    string _square(const string& expr) {
        if (expr.empty()) {
            return "";
        }
        
        string processed = expr;
        // Remove unnecessary outer parentheses
        while (processed.length() >= 2 && processed[0] == '(' && processed.back() == ')') {
            int level = 1;
            bool is_complete = true;
            for (size_t i = 1; i < processed.length() - 1; i++) {
                if (processed[i] == '(') {
                    level++;
                } else if (processed[i] == ')') {
                    level--;
                }
                if (level == 0) {
                    is_complete = false;
                    break;
                }
            }
            if (is_complete) {
                processed = processed.substr(1, processed.length() - 2);
            } else {
                break;
            }
        }
        
        // Find global &| operators
        int inbracket = 0;
        for (size_t i = 0; i < processed.length(); i++) {
            char c = processed[i];
            if (c == '(') {
                inbracket++;
            } else if (c == ')') {
                inbracket--;
            } else if (inbracket == 0 && (c == '&' || c == '|')) {
                string left = _square(processed.substr(0, i));
                string right = _square(processed.substr(i + 1));
                if (left[0] == '#' || right[0] == '#') {
                    return (left[0] == '#') ? left : right;
                }
                return (c == '&') ? _intersection(left, right) : _union(left, right);
            }
        }
        
        // Handle negation
        if (processed[0] == '!') {
            string text = _square(processed.substr(1));
            return (text[0] == '#') ? text : _complement(text);
        }
        
        // Normal case - process characters
        string modified = processed;
        size_t pos;
        while ((pos = modified.find("aa")) != string::npos) modified.replace(pos, 2, "x");
        while ((pos = modified.find("nn")) != string::npos) modified.replace(pos, 2, "q");
        
        string result;
        for (char c : modified) {
            string c_str(1, c);
            if (L2K.find(c_str) != L2K.end()) {
                result = _union(result, L2K[c_str]);
            } else if (KANA.find(c) != KANA.end()) {
                result = _union(result, string(1, c));
            } else {
                return _error("syntax", string(1, c));
            }
        }
        
        return result;
    }

    string _bracket(const string& expr) {
        if (count(expr.begin(), expr.end(), '[') > 1 || count(expr.begin(), expr.end(), '{') > 1) {
            return _error("syntax", expr);
        }
        
        string result;
        size_t open_bracket = expr.find('[');
        size_t close_bracket = expr.find(']');
        if (open_bracket != string::npos && close_bracket != string::npos) {
            result += "[";
            result += _square(expr.substr(open_bracket + 1, close_bracket - open_bracket - 1));
            result += "]";
        }
        
        size_t open_curly = expr.find('{');
        size_t close_curly = expr.find('}');
        if (open_curly != string::npos && close_curly != string::npos) {
            result += _curly(expr.substr(open_curly + 1, close_curly - open_curly - 1));
        }
        
        return result;
    }

    string _regex(const string& expr) {
        string result;
        size_t i = 0;
        while (i < expr.length()) {
            if (expr[i] == '?' || expr[i] == '*') {
                size_t j = i + 1;
                
                while (true) {
                    if (j >= expr.length()) break;
                    
                    bool iscurly = false;
                    if (expr[j] == '{') {
                        iscurly = true;
                    } else if (expr[j] == '[') {
                        iscurly = false;
                    } else {
                        break;
                    }
                    
                    char close_char = iscurly ? '}' : ']';
                    while (j < expr.length() && expr[j] != close_char) {
                        j++;
                    }
                    if (j < expr.length()) {
                        j++;
                    }
                }
                
                if (j == i + 1) { // No Bracket
                    if (expr[i] == '?') {
                        result += '.';
                    } else {
                        result += ".*";
                    }
                } else { // Handle Bracket
                    string bracket = _bracket(expr.substr(i + 1, j - i - 1));
                    if (bracket[0] == '#') {
                        return bracket;
                    }
                    
                    if (expr[i] == '?') {
                        if (bracket.find('{') != string::npos) {
                            return _error("syntax", expr.substr(i, j - i));
                        } else if (bracket.find('[') != string::npos) {
                            result += bracket;
                        } else {
                            return _error("syntax", expr.substr(i, j - i));
                        }
                    } else { // expr[i] == "*"
                        if (bracket.find('[') != string::npos) {
                            if (bracket.find('{') != string::npos) {
                                result += bracket;
                            } else {
                                result += bracket + "*";
                            }
                        } else {
                            if (bracket.find('{') != string::npos) {
                                result += "." + bracket;
                            }
                        }
                    }
                }
                i = j;
            } else {
                result += expr[i];
                i++;
            }
        }
        
        return result;
    }

    // Placeholder for _atQAT - would need more complex implementation
    string _atQAT(const string& expr) {
        // Simplified implementation - would need more work for full functionality
        bool has_at_or_upper = false;
        for (char c : expr) {
            if (c == '@' || (isalpha(c) && isupper(c))) {
                has_at_or_upper = true;
                break;
            }
        }
        
        if (has_at_or_upper) {
            // Simplified implementation
            return "@" + expr;
        } else {
            return _regex(expr);
        }
    }

    // Placeholder for _lg - would need more complex implementation
    string _lg(const string& expr) {
        if (expr.find('<') != string::npos) {
            // Simplified implementation for permutation
            return "|" + expr;
        } else {
            return _atQAT(expr);
        }
    }

    // Placeholder for _gb - would need more complex implementation
    string _gb(const string& expr) {
        if (expr.empty()) {
            return _error("empty");
        }
        
        // Simplified implementation
        string processed = expr;
        while (processed.length() >= 2 && processed[0] == '(' && processed.back() == ')') {
            processed = processed.substr(1, processed.length() - 2);
        }
        
        // Check for global operators | & !
        if (processed.find('|') != string::npos) {
            return "|" + processed;
        } else if (processed.find('&') != string::npos) {
            return "&" + processed;
        } else if (processed[0] == '!') {
            return "!" + processed.substr(1);
        } else {
            return _lg(processed);
        }
    }

    string _process_normal(const string& expr) {
        return _gb(expr);
    }

    string _process_qat(const string& expr) {
        return _atQAT(expr);
    }

    bool _nfm(const string& expr, const string& word) {
        if (expr == "@") {
            return _indict(word);
        } else if (expr[0] == '|' || expr[0] == '&' || expr[0] == '!') {
            // Simplified implementation for boolean operations
            // Full implementation would need to parse the expression tree
            return regex_match(word, regex(expr.substr(1)));
        } else {
            return regex_match(word, regex(expr));
        }
    }

    void _setup_qat() {
        qat_exprs.clear();
        qat_letters.assign(26, 0);
        qat_current_letters.assign(26, "");
        qat_current_answer.clear();
        qat_num_limit = 0;
        qat_start_time = chrono::steady_clock::now();
        qat_answers.clear();
        qat_error = " ";
        stop = false;
    }

    void _qat(int depth) {
        auto current_time = chrono::steady_clock::now();
        auto elapsed = chrono::duration_cast<chrono::seconds>(current_time - qat_start_time).count();
        if (elapsed > TIME_LIMIT) {
            qat_error = _error("timeout");
            stop = true;
            return;
        }
        
        if (stop) return;
        
        if (depth >= (int)qat_exprs.size()) {
            string answer;
            for (size_t i = 0; i < qat_current_answer.size(); i++) {
                if (i > 0) answer += ";";
                answer += qat_current_answer[i];
            }
            qat_answers.push_back(answer);
            if ((int)qat_answers.size() >= qat_num_limit) {
                stop = true;
            }
            return;
        }
        
        // Simplified implementation - would need more work for full QAT functionality
        string expr = qat_exprs[depth];
        for (const string& word : dict) {
            if (_nfm(expr, word)) {
                if (depth < (int)qat_current_answer.size()) {
                    qat_current_answer[depth] = word;
                } else {
                    qat_current_answer.push_back(word);
                }
                _qat(depth + 1);
                if (stop) return;
            }
        }
    }

public:
    vector<string> search(const string& expr, int num = 200) {
        // Check cache first
        string cache_key = expr + "|" + to_string(num);
        if (_result_cache.find(cache_key) != _result_cache.end()) {
            return _result_cache[cache_key];
        }
        
        _setup_qat();
        
        if (expr.empty()) {
            return {_error("empty")};
        }
        
        string normalized = _normalize(expr);
        if (normalized[0] == '#') {
            return {normalized};
        }
        
        // Normal search (no semicolon)
        if (normalized.find(';') == string::npos) {
            string expr_re = _process_normal(normalized);
            if (expr_re[0] == '#') {
                return {expr_re};
            }
            
            vector<string> result;
            auto start_time = chrono::steady_clock::now();
            
            // Use optimized search based on pattern characteristics
            vector<string>* search_candidates = &dict;
            
            // If fixed length pattern, use length index
            if (expr_re.find(".*") == string::npos && expr_re.find('.') == string::npos) {
                int target_length = expr_re.length();
                if (dict_by_length.find(target_length) != dict_by_length.end()) {
                    search_candidates = &dict_by_length[target_length];
                }
            }
            
            for (const string& word : *search_candidates) {
                auto current_time = chrono::steady_clock::now();
                auto elapsed = chrono::duration_cast<chrono::seconds>(current_time - start_time).count();
                if (elapsed > TIME_LIMIT) {
                    return {_error("timeout")};
                }
                
                if (_nfm(expr_re, word)) {
                    result.push_back(word);
                    if ((int)result.size() >= num) {
                        break;
                    }
                }
            }
            
            _result_cache[cache_key] = result;
            return result;
        } else {
            // QAT search (with semicolons)
            if (normalized.find('<') != string::npos || normalized.find('>') != string::npos) {
                return {_error("syntax", "< or > in QAT")};
            }
            
            qat_num_limit = num;
            
            vector<string> exprs;
            stringstream ss(normalized);
            string item;
            while (getline(ss, item, ';')) {
                if (!item.empty()) {
                    // Remove unnecessary parentheses
                    while (item.length() >= 2 && item[0] == '(' && item.back() == ')') {
                        item = item.substr(1, item.length() - 2);
                    }
                    exprs.push_back(item);
                }
            }
            
            if (exprs.empty()) {
                return {_error("empty")};
            }
            
            // Process length limitations
            for (size_t i = 0; i < exprs.size(); i++) {
                if (exprs[i].find('=') != string::npos) {
                    // Simplified implementation for length constraints
                    // Would need more work for full implementation
                    size_t pos = exprs[i].find('=');
                    if (pos != string::npos && pos >= 3 && exprs[i][0] == '|' && exprs[i][pos-1] == '|') {
                        char letter = exprs[i][1];
                        if (letter >= 'A' && letter <= 'Z') {
                            int letter_idx = letter - 'A';
                            string length_str = exprs[i].substr(pos + 1);
                            try {
                                int length_val = stoi(length_str);
                                if (length_val > 0 && length_val < 10) {
                                    qat_letters[letter_idx] = length_val;
                                    exprs.erase(exprs.begin() + i);
                                    i--;
                                }
                            } catch (...) {
                                // Invalid number
                            }
                        }
                    }
                }
            }
            
            if (exprs.empty()) {
                return {_error("empty")};
            }
            
            // Check for global operators
            for (const string& expr_item : exprs) {
                int bracket_level = 0;
                for (char c : expr_item) {
                    if (c == '(' || c == '[') {
                        bracket_level++;
                    } else if (c == ')' || c == ']') {
                        bracket_level--;
                    } else if (bracket_level == 0 && (c == '&' || c == '|' || c == '!')) {
                        return {_error("syntax", expr_item)};
                    }
                }
            }
            
            // Sort by number of uppercase letters
            sort(exprs.begin(), exprs.end(), [](const string& a, const string& b) {
                int count_a = count_if(a.begin(), a.end(), [](char c) { return isupper(c); });
                int count_b = count_if(b.begin(), b.end(), [](char c) { return isupper(c); });
                return count_a > count_b;
            });
            
            // Process expressions
            for (const string& expr_item : exprs) {
                string processed = _process_qat(expr_item);
                if (processed[0] == '#') {
                    return {processed};
                }
                qat_exprs.push_back(processed);
            }
            
            qat_current_answer.resize(qat_exprs.size(), "");
            _qat(0);
            
            if (qat_error[0] == '#') {
                return {qat_error};
            } else {
                _result_cache[cache_key] = qat_answers;
                return qat_answers;
            }
        }
    }

    void search_print(const string& expr, int num = 200, bool to_file = false) {
        auto start_time = chrono::steady_clock::now();
        vector<string> result;
        
        try {
            result = search(expr, num);
        } catch (const exception& e) {
            cout << "Unexpected Error: " << e.what() << endl;
            return;
        }
        
        auto end_time = chrono::steady_clock::now();
        auto elapsed = chrono::duration_cast<chrono::milliseconds>(end_time - start_time).count();
        
        cout << "Expr: " << expr << endl;
        cout << "Found " << result.size() << " items in " << elapsed / 1000.0 << " seconds:" << endl;
        cout << endl;
        
        if (result.empty()) {
            cout << "No Solution." << endl;
        } else if (result[0][0] == '#') {
            cout << result[0] << endl;
        } else {
            for (size_t i = 0; i < result.size(); i++) {
                cout << result[i];
                if ((i + 1) % 10 == 0) {
                    cout << endl;
                } else {
                    cout << "\t";
                }
            }
        }
        cout << endl << endl;
    }
};

// Initialize static members
vector<string> dict;
unordered_map<size_t, string> hasht;
unordered_map<int, vector<string>> dict_by_length;
unordered_map<char, vector<string>> dict_by_first_char;

int main() {
    JishoSearcher searcher;
    // Example usage
    searcher.search_print("！＊｛５ー｝＆＜あ＞＊｛１ー３｝「！o」い", 10);
    return 0;
}