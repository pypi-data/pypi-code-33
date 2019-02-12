# SeeQR Python Library Test File

from src import main as seeqr


def string_to_plaintext_test():
    print('string_to_plaintext_test')
    print('================')
    print('''
        Test #1
        String -> SeeQR Data
        String = "Test"
        Bold = True
        Font size = 50
        Font color = Green
    ''')
    print(seeqr.gendata_textstring(text='Test', is_bold=True, fontsize=50, fontcolor='Green'))
    print('''
        Test #2
        String -> SeeQR Data
        String = "281938249213"
        Bold = False
        Font size = 100
        Font color = Red
        ''')
    print(seeqr.gendata_textstring(text='281938249213', is_bold=False, fontsize=100, fontcolor='Red'))
    print('''
        Test #3
        String -> SeeQR Data
        String = "Test_Hoge_Maru_2525_IEEEE"
        Bold = True
        Font size = 10
        Font color = Magenta
        ''')
    print(seeqr.gendata_textstring(text='Test_Hoge_Maru_2525_IEEEE', is_bold=True, fontsize=10, fontcolor='Magenta'))
    print('================')


def htmlstring_to_html_test():
    print('htmlstring_to_html_test')
    print('================')
    print('''
        Test #1
        HTML String -> SeeQR Data
        String = "<html><body><h1>SeeQR Test</h1></body></html>"
    ''')
    print(seeqr.gendata_htmlstring(html='<html><body><h1>SeeQR Test</h1></body></html>'))
    print('''
        Test #2
        HTML String -> SeeQR Data
        String = "<html><body><h1>SeeQR Test</h1><div class="test"><h2>TEST</h2></div></body></html>"
        ''')
    print(seeqr.gendata_htmlstring(html=
                                   '<html><body><h1>SeeQR Test</h1><div class="test"><h2>TEST</h2></div></body></html>'
                                   ))
    print('''
        Test #3
        HTML String -> SeeQR Data
        String = "<html><head><style>.test { color: Blue; }</style></head><body><h1>SeeQR Test</h1><div class="test"><h2>TEST</h2></div></body></html>"
        ''')
    print(seeqr.gendata_htmlstring(html='<html><head><style>.test { color: Blue; }</style></head><body><h1>SeeQR Test</h1><div class="test"><h2>TEST</h2></div></body></html>'))
    print('================')


def textfile_to_plaintext_test():
    print('textfile_to_plaintext_test')
    print('================')
    print('''
            Test #1
            Text file -> SeeQR Data
            File path = '/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.txt'
            Bold = True
            Font size = 50
            Font color = Green
        ''')
    print(seeqr.gendata_textfile(filepath='/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.txt', is_bold=True, fontsize=50, fontcolor='Green'))
    print('''
            Test #2
            Text file -> SeeQR Data
            File path = '/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.txt'
            Bold = False
            Font size = 100
            Font color = Red
            ''')
    print(seeqr.gendata_textfile(filepath='/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.txt', is_bold=False, fontsize=100, fontcolor='Red'))
    print('''
            Test #3
            Text file -> SeeQR Data
            File path = '/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.txt'
            Bold = True
            Font size = 10
            Font color = Magenta
            ''')
    print(seeqr.gendata_textfile(filepath='/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.txt', is_bold=True, fontsize=10, fontcolor='Magenta'))
    print('================')


def csvfile_to_csv_test():
    print('csvfile_to_csv_test')
    print('================')
    print('''
            Test
            CSV file -> SeeQR Data
            File path = '/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.csv'
        ''')
    print(seeqr.gendata_csvfile(filepath='/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.csv'))
    print('================')


def htmlfile_to_html_test():
    print('csvfile_to_csv_test')
    print('================')
    print('''
            Test
            HTML file -> SeeQR Data
            File path = '/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.html'
        ''')
    print(seeqr.gendata_htmlfile(filepath='/Users/moppoi5168/SeeQR/src/python_library/SeeQR/test/test.html'))
    print('================')


def main():
    print('Starting Test.....')
    seeqr.hello_library()
    print('================')
    # string_to_plaintext_test()
    # htmlstring_to_html_test()
    # textfile_to_plaintext_test()
    # csvfile_to_csv_test()
    # htmlfile_to_html_test()


if __name__ == '__main__':
    main()
