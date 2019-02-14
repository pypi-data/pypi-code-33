class Pipeline(object):
    """负责处理数据对象(Item)"""

    def process_item(self, item):
        """处理item对象"""
        print("item: ", item)