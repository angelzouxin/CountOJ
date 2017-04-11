# coding=utf-8

__author__ = 'zouxin'

import xlrd
from xlwt import *
import time


class AcManager:
    supportedOJ = ['poj', 'hdu', 'zoj', 'codeforces', 'fzu', 'acdream', 'bzoj', 'ural', 'csu', 'hust', 'spoj', 'sgu',
                   'vjudge', 'bnu', 'cqu', 'uestc', 'zucc']
    user_list = []
    col_id = []

    def __init__(self, id_file):
        self.data = xlrd.open_workbook(id_file)
        self.crawel_data = time.strftime('%Y-%m-%d %a %H:%M', time.localtime(time.time()))
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

            oj_id['default'] = oj_id.get('had') is not None and oj_id.get('hdu') or oj_id.get('zucc')
            print({id, name}, oj_id)
            self.user_list.append([id, name, oj_id])

    def get_count(self):
        from countOJUtil import Crawler
        for user in self.user_list:
            crawler = Crawler(user[2])
            crawler.run()
            user.append(crawler.acArchive.copy())
            user.append(crawler.submitNum.copy())

    def save_count(self, out_file):
        import writeXLSUtil
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
            data.append(user[0])
            data.append(user[1])
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
            data.append(self.crawel_data)
            datas.append(data)
        writeXLSUtil.WriteXLSUtil.write_xls(ws1, headings, datas)
        ws2 = w.add_sheet('ac_submission')
        headings = self.col_id
        datas = []
        for user in self.user_list:
            data = []
            user_num = user[3]
            user_sub = user[4]
            data.append(user[0])
            data.append(user[1])
            for col_name in self.col_id[2:]:
                if user_num.get(col_name) is not None:
                    data.append('%s' % ('' if len(user_num.get(col_name)) == 0 else str(user_num.get(col_name))))
                else:
                    data.append('')
            datas.append(data)
        writeXLSUtil.WriteXLSUtil.write_xls(ws2, headings, datas)
        w.save(out_file)


if __name__ == '__main__':
    acManager = AcManager('Id_list.xlsx')
    acManager.get_count()
    acManager.save_count('Count_list.xls')
