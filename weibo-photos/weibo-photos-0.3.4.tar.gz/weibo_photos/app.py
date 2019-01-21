from weibo_photos.weibo_images_crawler import WeiboImageCrawler
import click

@click.group()
def cli():
    """这是一个用于下载微博图片的小工具"""
    pass

@cli.command()
@click.argument('key')
def search(key):
    """根据用户名搜索用户信息"""
    crawler = WeiboImageCrawler()
    crawler.init_requests()
    crawler.search_user(key)

@cli.command()
@click.option('--detail/--no-detail', '-d/-nd', default=False, help='是否显示专辑详细信息，默认只显示专辑ID和标题')
@click.argument('userid')
def albums(detail, userid):
    """显示该用户下的所有专辑信息"""
    crawler = WeiboImageCrawler(userid)
    crawler.init_requests()
    crawler.get_album_info()
    crawler.print_albums_info()

@cli.command()
@click.option('-p', '--path', help='设置下载目录路径')
@click.argument('userid')
@click.argument('albumid')
@click.argument('albumtype')
def photos(path, userid, albumid, albumtype):
    """下载整个相册"""
    crawler = WeiboImageCrawler(userid)
    crawler.init_requests()
    crawler.get_images_address(albumid, albumtype)
    crawler.save_all_images(userid, albumid, path)

@cli.command()
@click.argument('userid')
@click.argument('albumid')
@click.argument('albumtype')
def export(userid, albumid, albumtype):
    """将图片地址保存到文本文件中"""
    crawler = WeiboImageCrawler(userid)
    crawler.init_requests()
    crawler.get_images_address(albumid, albumtype)
    crawler.write_images_address(albumid)
    
if __name__ == "__main__":
    cli()







    