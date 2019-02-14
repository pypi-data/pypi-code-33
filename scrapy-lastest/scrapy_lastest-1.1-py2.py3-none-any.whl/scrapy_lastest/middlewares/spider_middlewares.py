class SpiderMiddleware(object):
    '''爬虫中间件基类'''

    def process_request(self, request):
        '''预处理请求对象'''
        print("这是爬虫中间件：process_request方法")
        return request

    def process_response(self, response):
        '''预处理数据对象'''
        print("这是爬虫中间件：process_response方法")
        return response