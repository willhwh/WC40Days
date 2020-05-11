# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

class D27CrawlerSpider(scrapy.Spider):
    name = 'd27_Crawler'
    allowed_domains = ['www.ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/AnimalForest/M.1588918852.A.3B1.html']
    cookie={'over18': '1'}





    def start_request(self):
        for url in start_urls:
            yield scrapy.Request(url=url,callback=sel.parse)

    def parse(self, response):
        #if response.status != 200: >>> failed to Request
        if response.status!=200:
            print('Error-{} is not available to access'.format(response.url))
            return

        soup=BeautifulSoup(response.text)
        main_content=soup.find(id='main_content')
        #give default value to authoer,title,article_date
        author=''
        title=''
        date=''
        #.select works like .find_all
        #.select >>>list, has no .string
        metas=main_content.select('div.article-metaline')
        metas_f=main_content.findall('div',{'class':'article-metaline'})

        # if --- : >>if exist
        if metas:
            #.string or .text
            if metas[0].select('span.article-meta-value')[0]:
                author= metas[0].select('span.article-meta-value')[0].string
            if metas[1].select('span.article-meta-value')[0]:
                title=metas[1].select('span.article-meta-value')[0].string
            if metas[2].select('span.article-meta-value')[0]:
                date=metas[2].select('span.article-meta-value')[0].strings


            # 從 main_content 中移除 meta 資訊（author, title, date 與其他看板資訊）
            for m in metas:
                m.extract()
            for m in main_content.select('div.article-metaline-right'):
                m.extract()

        #get the comments
        pushes=main_content.find_all('div',class_='push')
        for p in pushes:
            #從 main_content 中移除 push 資訊
            p.extract()

        # 假如文章中有包含「※ 發信站: 批踢踢實業坊(ptt.cc), 來自: xxx.xxx.xxx.xxx」的樣式
        # 透過 regular expression 取得 IP
        # 因為字串中包含特殊符號跟中文, 這邊建議使用 unicode 的型式 u'...'

        #get IP
        try:
            ip = main_content.find(text=re.compile(u'※ 發信站:'))
            #use \. to represent . as .
            ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
        except Exception as e:
            ip = ''



        # 移除文章主體中 '※ 發信站:', '◆ From:', 空行及多餘空白 (※ = u'\u203b', ◆ = u'\u25c6')
        # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
        #
        # 透過 .stripped_strings 的方式可以快速移除多餘空白並取出文字, 可參考官方文件
        #  - https://www.crummy.com/software/BeautifulSoup/bs4/doc/#strings-and-stripped-strings
        filtered = []
        for v in main_content.stripped_strings:
            # 假如字串開頭不是特殊符號或是以 '--' 開頭的, 我們都保留其文字
            if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--']:
                filtered.append(v)


        # 定義一些特殊符號與全形符號的過濾器
        expr = re.compile(u'[^一-龥。；，：“”（）、？《》\s\w:/-_.?~%()]')
        for i in range(len(filtered)):
            #replace element in expr to ""
            filtered[i] = re.sub(expr, '', filtered[i])

        # 移除空白字串, 組合過濾後的文字即為文章本文 (content)
        filtered = [i for i in filtered if i]
        #string.join(iterable)
        #用“ ”區隔
        content = ' '.join(filtered)

        # 處理留言區
        # p 計算推文數量
        # b 計算噓文數量
        # n 計算箭頭數量
        p, b, n = 0, 0, 0
        messages = []
        for push in pushes:
            # 假如留言段落沒有 push-tag 就跳過
            #if not ---:>>>if not exist
            if not push.find('span', 'push-tag'):
                continue

            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[1:].strip(' \t\n\r')
            push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')

            #整理資訊
            messages.append({
                'push_tag': push_tag,
                'push_userid': push_userid,
                'push_content': push_content,
                'push_ipdatetime': push_ipdatetime})
            if push_tag == u'推':
                p += 1
            elif push_tag == u'噓':
                b += 1
            else:
                n += 1

        # 統計推噓文
        # count 為推噓文相抵看這篇文章推文還是噓文比較多
        # all 為總共留言數量
        message_count = {'all': p+b+n, 'count': p-b, 'push': p, 'boo': b, 'neutral': n}

        # 整理文章資訊
        data = {
            'url': response.url,
            'article_author': author,
            'article_title': title,
            'article_date': date,
            'article_content': content,
            'ip': ip,
            'message_count': message_count,
            'messages': messages
        }
        yield data
