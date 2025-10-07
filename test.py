from main import JishoSearcher

def test():
    test = JishoSearcher(lang="zh")
    # test.search_print("！＊｛５ー｝＆＜あ＞＊｛１ー３｝「！o」い")
    # print(test._process_normal("Aああ@あ*{1-3}ああO"))
    test.search_print("A\"DB'D")
    # test.search_print("CA;C;A?[o];ACB;(((AB?[C])));|A|=2;|B|=2;|C|=2")
    # test.search_print("A;B;AB?ま",num=20)
    # test.search_print("A;B;AB\"") # Test "
    
test()