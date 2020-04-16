```python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

# 本代码粗分箱：等深/等频分箱。
# 1）按照样本数，对变量分10份；
# 2）根据该粗分箱结果计算IV值。

def Cut_DF(df, y_col, x_col, bins_num=10):
    '''
    对自变量取值划分区间，输出变量的分箱明细和IV值
    df：包含2列：待分箱的单个自变量、因变量y
    y_col: 因变量名
    x_col：待分箱的单个自变量名
    bins_num：要划分的区间数，默认为10
    '''
    var_cnt = len(set(df[x_col]))
    total_bad = sum(df[y_col])
    total_good = len(df[y_col]) - sum(df[y_col])
    
    if str(df[x_col].dtype) == 'object' or var_cnt < bins_num:
        bad_cnt = df[y_col].groupby(df[x_col]).agg('sum')
        sample_cnt = df[y_col].groupby(df[x_col]).agg('count')
    else:
        df['new_x'] = pd.qcut(df[x_col], bins_num, duplicates='drop')
        sample_cnt = df[y_col].groupby(df['new_x']).agg('count')
        bad_cnt = df[y_col].groupby(df['new_x']).agg('sum')
        good_cnt = sample_cnt-bad_cnt
    
    # 若出现好/坏样本为0的箱，则人为+1，避免IV为inf
    for i in range(0,len(bad_cnt)):
        if bad_cnt[i] == 0:
            bad_cnt[i] += 1
            total_bad += 1
    
    for i in range(0,len(good_cnt)):
        if good_cnt[i] == 0:
            good_cnt[i] += 1
            total_good += 1
    
    bad_percent_series = bad_cnt / total_bad
    good_percent_series = good_cnt / total_good
    
    woe_list = list(np.log(bad_percent_series/good_percent_series))   
    IV_list = list((good_percent_series - bad_percent_series) * np.log(good_percent_series / bad_percent_series))
    bad_rate_list = bad_cnt / sample_cnt
    
    bins_df = pd.DataFrame({
                            'bin': bad_cnt.index
                            ,'bad_rate': bad_rate_list
                            ,'woe': woe_list
                            ,'iv': IV_list
                            ,'total_count': sample_cnt
                            })
    bins_df.insert(0, 'Var', x_col)
    bins_df = bins_df.reset_index(drop=True)
    iv = sum(IV_list)
    return bins_df, iv
    
def Print_Var(df, y_col, raw_var_list, bins_num=10):
    final_var_list = []
    iv_list = []
    pre_bins_df = pd.DataFrame()
    
    for x_col in raw_var_list:
        bins_df, iv = Cut_DF(df, y_col, x_col, bins_num)
        pre_bins_df = pd.concat([pre_bins_df, bins_df])
        final_var_list.append(x_col)
        iv_list.append(iv)
            
    pre_iv_df = pd.DataFrame({
                            'Var': final_var_list
                            ,'iv': iv_list
                            })
    pre_iv_df = pre_iv_df.sort_values('iv', ascending=False)
    return pre_iv_df, pre_bins_df
```
