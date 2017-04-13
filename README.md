# CountOJ
Crawler each persons of school ACM-ICPC team’s online-judges Accepted, Submissions and Accepted Problems ID

Count Accepted and submissions everyday

drawing on the experience of [kidozh](https://github.com/kidozh)

supportedOJ
'poj', 'hdu', 'zoj', 'codeforces', 'fzu', 'acdream', 'bzoj', 'ural', 'csu', 'hust', 'spoj', 'sgu', 'vjudge', 'bnu', 'cqu', 'uestc'

1.import team info into excel like this


user_id | user_name | oj_id1| oj_id2| ... |
---- | ---- | ---- | ---- | ---- |
id1 | name1 | oj_id1_1 | oj_id1_2|...| 
id2 |  name2 | oj_id2_1| oj_id2_2|...|

2.run acManager.py

```python3
if __name__ == '__main__':
    ...
    pre_acManager = AcManager()
    pre_acManager.get_pre_info(preName)

    #get team info and count
    total_acManager = AcManager()
    total_acManager.get_IDlist('id_list.xls')
    total_acManager.get_count()
    # total_acManager.get_pre_info(preName)

    #get substract
    today_acManager = AcManager.get_today_mes(total_acManager, pre_acManager)
    total_acManager.save_count(totalName)
    today_acManager.save_count(fileName + '.xls')
```


## motivation
count school ACM-ICPC teams training info

## dependency

- Python 3.x
- http.cookiejar
- xlrd／xlwt
- configparser

## license

MIT License
