# coding=utf-8

__author__ = 'zouxin'

import xlwt

class WriteXLSUtil:
    ezxf = xlwt.easyxf
    heading_xf = ezxf('font: bold on; align:wrap on, vert centre, horiz center')

    @staticmethod
    def write_xls(sheet_name, headings, data):
        heading_xf = WriteXLSUtil.heading_xf
        # data_xfs = [WriteXLSUtil.kind_to_xf_map[k] for k in WriteXLSUtil.kinds]
        rowx = 0

        for colx, value in enumerate(headings):
            sheet_name.write(rowx, colx, value, heading_xf)

        sheet_name.set_panes_frozen(True)  # frozenheadings instead of split panes

        sheet_name.set_horz_split_pos(rowx + 1)  # ingeneral, freeze after last heading row

        sheet_name.set_remove_splits(True)  # if userdoes unfreeze, don't leave a split there

        for row in data:

            rowx += 1

            for colx, value in enumerate(row):
                sheet_name.write(rowx, colx, value)

