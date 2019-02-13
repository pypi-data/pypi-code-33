class Paginator(object):
    '''
    A class for paginating, you can save and transmit data with it after get data from database.
    This class applicable for pagination in admin system
    '''

    def __init__(self, current_page, total_page_count, items, total_item_count, page_size=10):
        '''
        :param int current_page: Current page number
        :param int total_page_count: Total page count
        :param object items: Paging data
        :param int total_item_count: Total item count
        :param int page_size: How many items per page
        '''
        self.current_page = current_page
        self.total_page_count = total_page_count
        self.items = items
        self.total_item_count = total_item_count
        self.page_size = page_size

    def get_dict(self):
        '''
        Convert Paginator instance to dict

        :return: Paging data
        :rtype: dict
        '''

        return dict(
            current_page=self.current_page,
            total_page_count=self.total_page_count,
            items=self.items,
            total_item_count=self.total_item_count,
            page_size=self.page_size
        )
