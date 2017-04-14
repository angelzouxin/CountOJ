# CountOJ
Crawl each person’s training info who is one of school’s ACM/ICPC team members that submit problems to online-judges, it contains the status of Submissions , Accepted , and problem ID, what’s more , it records the total Accepted and submissions everyday

drawing on the experience of [kidozh](https://github.com/kidozh)

supportedOJ
'poj', 'hdu', 'zoj', 'codeforces', ‘codechef', 'fzu', 'acdream', 'bzoj', 'ural', 'csu', 'hust', 'spoj', 'sgu', 'vjudge', 'bnu', 'cqu', 'uestc'

1.import team info into excel like this


user_id | user_name | ojID1| ojID2| ... |
---- | ---- | ---- | ---- | ---- |
id1 | name1 | ojID1_1 | ojID1_2|...| 
id2 |  name2 | ojID2_1| ojID2_2|...|

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
