# coding=utf-8

__author__ = 'zouxin'

import datetime
import time

import xlrd
from xlwt import *


class AcManager:
    supportedOJ = ['poj', 'hdu', 'zoj', 'codeforces', 'fzu', 'acdream', 'bzoj', 'ural', 'csu', 'hust', 'spoj', 'sgu',
                   'vjudge', 'bnu', 'cqu', 'uestc', 'zucc']

    def __init__(self):
        self.user_list = []
        self.col_id = []

    def get_IDlist(self, id_file):
        self.data = xlrd.open_workbook(id_file)
        self.crawel_date = time.strftime('%Y-%m-%d %a %H:%M', time.localtime(time.time()))
        tabel = self.data.sheet_by_index(0)
        rows, cols = tabel.nrows, tabel.ncols
        head = tabel.row_values(0)
        self.col_id = [head[idx] for idx in range(cols)]
        for row in range(1, rows):
            mes = tabel.row_values(row)
            id, name = mes[:2]
            id = int(id)
            oj_id = {self.col_id[idx]: (type(mes[idx]) == float and str(int(mes[idx])) or mes[idx]) for idx in
                     range(2, cols) if mes[idx] is not None and mes[idx] != ''}

            oj_id['default'] = oj_id.get('zucc') is None and oj_id.get('hdu') or oj_id.get('zucc')
            print({id, name}, oj_id)
            self.user_list.append([id, name, oj_id])

    #get pre info from excel
    def get_pre_info(self, info_file, sheet_name1='ac_count', sheet_name2='ac_submission'):
        from xlsUtil import xlsUtil
        self.info = xlrd.open_workbook(info_file)
        self.col_id, info_data = xlsUtil.read_xls(info_file, sheet_name1)
        self.col_id = self.col_id[:-2]

        info_head, info_achieve = xlsUtil.read_xls(info_file, sheet_name2)

        self.crawel_date = info_data[0][-1]
        # print(self.crawel_date)

        idx, col = 0, len(info_data)
        for ac_num in info_achieve:
            # print (ac_num)
            id, name = ac_num[:2]
            id = int(id)
            acArchive = {self.col_id[id]: (
                ac_num[id] != '' and set(map(lambda x: x.strip("'"), ac_num[id].strip('{}').split(', '))) or set()) for
            id
                in range(2, len(ac_num))}
            self.user_list.append([id, name, {}, acArchive.copy()])
        for ac_sub in info_data:
            submitNum = {self.col_id[id]: int(ac_sub[id].split('/')[-1]) for id in range(2, len(ac_sub) - 2)}
            self.user_list[idx].append(submitNum.copy())
            idx += 1

    def get_count(self):
        from countOJUtil import Crawler
        for user in self.user_list:
            crawler = Crawler(user[2])
            crawler.run()
            user.append(crawler.acArchive.copy())
            user.append(crawler.submitNum.copy())

    def save_count(self, out_file):
        from xlsUtil import xlsUtil
        w = Workbook()
        ws1 = w.add_sheet('ac_count')
        headings = self.col_id.copy()
        headings.append('总计AC/Submission')
        headings.append('统计日期')
        datas = []
        for user in self.user_list:
            data = []
            # AC_num/AC_submission
            user_num = user[3]
            user_sub = user[4]
            data.append(user[0])  # id
            data.append(user[1])  # name
            sum_num, sum_sub = 0, 0
            for col_name in self.col_id[2:]:
                if user_num.get(col_name) is not None:
                    ac_num = len(user_num.get(col_name))
                    ac_sub = user_sub.get(col_name)
                    sum_num += ac_num
                    sum_sub += ac_sub
                    data.append('%d/%d' % (ac_num, ac_sub))
                else:
                    data.append('0/0')
            data.append('%d/%d' % (sum_num, sum_sub))
            data.append(self.crawel_date)
            datas.append(data)
        xlsUtil.write_xls(ws1, headings, datas)
        ws2 = w.add_sheet('ac_submission')
        headings = self.col_id
        datas = []
        for user in self.user_list:
            data = []
            user_num = user[3]
            data.append(user[0])
            data.append(user[1])
            for col_name in self.col_id[2:]:
                if user_num.get(col_name) is not None:
                    data.append('%s' % ('' if len(user_num.get(col_name)) == 0 else str(user_num.get(col_name))))
                else:
                    data.append('')
            datas.append(data)
        xlsUtil.write_xls(ws2, headings, datas)
        w.save(out_file)

    #substract pre
    @staticmethod
    def get_today_mes(today, pre):
        res = AcManager()
        # for user in today.user_list:
        #     print (user[4])
        today_dic = {data[0]: data[1:] for data in today.user_list}
        pre_dic = {data[0]: data[1:] for data in pre.user_list}
        # for user in pre.user_list:
        #     print(user[:3],user[-1])
        # print('---------'*10)
        # for user in today.user_list:
        #     print(user[:3],user[-1])
        # print('---------' * 10)
        res.crawel_date = today.crawel_date
        res.col_id = today.col_id
        res.user_list = [[user] + today_dic[user][:2] + (today_dic[user][2:] if pre_dic.get(user) is None
                         else ([{oj: today_dic[user][2][oj] if pre_dic[user][2].get(oj) is None else today_dic[user][2][oj] - pre_dic[user][2][oj] for oj in today_dic[user][2]}]
                               +[{oj: today_dic[user][3][oj] if pre_dic[user][3].get(oj) is None else today_dic[user][3][oj] - pre_dic[user][3][oj] for oj in today_dic[user][3]}]))
                         for user in today_dic]

        # for user in res.user_list:
        #     print(user[:3], user[-1])
        return res


if __name__ == '__main__':
    headName = 'Count_list_'
    sufNameFormat = '%Y_%m_%d'
    today = datetime.datetime.today()
    oneDay = datetime.timedelta(days=1)
    yesterday = today - oneDay
    fileName = headName + today.strftime(sufNameFormat)
    preName = 'total_'+yesterday.strftime(sufNameFormat)
    totalName = 'total_'+today.strftime(sufNameFormat)

    # get pre ac info
    pre_acManager = AcManager()
    pre_acManager.get_pre_info(preName+'.xls')

    # get team info and count
    total_acManager = AcManager()
    total_acManager.get_IDlist('id_list.xls')
    total_acManager.get_count()

    # get substract
    today_acManager = AcManager.get_today_mes(total_acManager, pre_acManager)
    total_acManager.save_count(totalName + '.xls')
    today_acManager.save_count(fileName + '.xls')
