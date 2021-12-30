import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow ,QMessageBox
from ui import Ui_Spider
import requests
from lxml import etree
#from multiprocessing import Pool
f#rom multiprocessing import Manager
import time
import re


class mwindow(QWidget, Ui_Spider):
    def __init__(self):
        super(mwindow, self).__init__()
        self.setupUi(self)
        self.initUi()
        self.initarg()



    def initUi(self):
        #绑定事件
        self.spider_button.clicked.connect(self.add_list)
        self.url_button.clicked.connect(self.out_url)
        self.wl_button.clicked.connect(self.out_wl_url)


    def initarg(self):
        # 全局url变量
        global temp_list2
        temp_list2 = []

        # 全局外联变量
        global temp_list
        temp_list = []

        global quen_list
        quen_list = []

        global count
        count = 0



    def out_url(self):
        widgetres = self.write_text()

        with open('url.txt','w+',encoding='utf-8') as f:
            for i in widgetres:
                f.writelines(i + '\n')
        QMessageBox.about(self, '','导出成功')


    def out_wl_url(self):
        widgetres = temp_list

        with open('wl_url.txt','w+',encoding='utf-8') as f:
            for i in widgetres:
                f.writelines(i + '\n')
        QMessageBox.about(self, '','导出成功')


    def add_list(self):
        num = self.url_text.text()
        # 爬取标签列表
        p_list = ['//@href', '//@src', '//@link']

        # 判断是否为本域名参数
        domain_url = self.doamin_text.text()
        domain_list = domain_url.split(";")

        #开始之前情况清空所有列表数据
        self.url_list.clear()
        self.wl_list.clear()
        temp_list.clear()
        temp_list2.clear()
        quen_list.clear()

        # 判断是否为空
        if len(num) == 0:
            QMessageBox.about(self,'','请输入url')
        if len(domain_url) == 0:
            QMessageBox.about(self, '', '请输入domain!')
        if len(num) !=0 and len(domain_list) != 0:
            self.pool_pc(p_list,num,domain_list)


    def sprider(self,reg, url, domain_url):
        if url not in temp_list2:
            # 将每次跑的url写进3.txt
            temp_list2.append(url)

            # 添加跑的url元素
            self.url_list.addItem(str(url))
            QApplication.processEvents()


            x = self.link_url(url)

            if x != None:
                # 获取页面源码
                html = etree.HTML(x.content)

                tpl_content = self.get_tpt_content(reg, html)

                filter_list = self.get_filter_list(url, tpl_content)

                self.cycle(url, filter_list, domain_url)

        else:
            # q.put(url)
            time.sleep(0.01)

    def cycle(self,url, filter_list, domain_url):

        # 进行判断下方是否还有url,如果有继续,如果没有停止
        flag = 0
        temp_filter_list = []
        set(filter_list)
        for fl in filter_list:
            for d_url in domain_url:
                if d_url in fl:
                    if fl not in temp_list2:
                        temp_filter_list.append(fl)
                        flag = 1

                if d_url not in fl:
                    temp_list.append(fl)

                    # 添加外联列表元素
                    self.wl_list.addItem(str(fl))
                    QApplication.processEvents()

        if flag == 1:
            for te in set(temp_filter_list):
                quen_list.append(te)

        # q.put(url)
        time.sleep(0.01)

    def get_filter_list(self,url, tpl_content):
        # 过滤第一次讲有的//href前加上http://,filter_list1保存过滤后的列表元素
        filter_list1 = []

        # 对url进行匹配出前
        paren = r"(?:https|http)?://(?:[-\w.]|(?:%[\da-zA-Z]))+(?:[com|cn|org|js|css|img|net]+)"

        url_qinzui = re.findall(paren, url)[0]

        # 判断是否已'/'开头,是就添加前缀
        if len(tpl_content) != 0:
            for tpl_c in tpl_content:
                if tpl_c[0:4] != 'http':
                    if tpl_c[0:1] == '/':
                        tpl = url_qinzui + tpl_c
                        filter_list1.append(tpl)
                    elif tpl_c[0:1] == '.':
                        tpl = url_qinzui + '/' + tpl_c
                        filter_list1.append(tpl)
                    elif tpl_c[0:3] == 'www':
                        tpl = tpl_c
                        filter_list1.append(tpl)
                    else:
                        tpl = url_qinzui + '/' + tpl_c
                        filter_list1.append(tpl)
                else:
                    filter_list1.append(tpl_c)
        return filter_list1

    def get_tpt_content(self,reg, html):
        all_content = []
        for r in reg:
            try:
                tpl_content = list(set(html.xpath(r)))

            except:
                continue

            tpl_content = [tp for tp in tpl_content if tp != '']
            tpl_content = [' '.join([i.strip() for i in tp.strip().split('\t')]) for tp in tpl_content]
            all_content += tpl_content

        return set(all_content)

    def link_url(self,url):
        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
                }

        # 做异常处理,如果连接不同提示URL以及跳过
        try:
            x = requests.get(url, allow_redirects=False, headers=head, timeout=2)
            if x != None:
                return x
        except:
            print('无法连接' + url)

    def write_text(self):
        # 存url
        url_list = []

        # 存css
        css_list = []

        # 存js
        js_list = []

        # 存图片
        img_list = []

        all_list = list(set(temp_list2))
        for a in all_list:
            h_3 = (a[-3:]).lower()
            h_4 = (a[-4:]).lower()
            if h_3 == '.js':
                js_list.append(a)
            elif h_4 == '.css':
                css_list.append(a)
            elif h_4 == '.jpg' or h_4 == '.png' or h_4 == '.gif':
                img_list.append(a)
            else:
                url_list.append(a)
        # 组合列表
        new_list = ['URL列表为:'] + url_list + ['\n\nJS列表为:'] + js_list + ['\n\nCSS列表为'] + \
                   css_list + ['\n\n图片列表为'] + img_list

        return new_list

    def pool_pc(self,p_list, seedUrl, domain_url):
         # 使用进程池
        # pool = Pool()
        # q = Manager().Queue()
        # 当前页的处理
        self.sprider(p_list, seedUrl, domain_url)

        # 抓取队列中的信息为空，则退出循环
        while quen_list:
            url = quen_list.pop(0)
            self.sprider(p_list, url, domain_url)

        QMessageBox.about(self,'','爬虫完毕')
        # pool.close()
        # pool.join()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = mwindow()
    w.show()
    sys.exit(app.exec_())