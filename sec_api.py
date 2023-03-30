# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 15:01:15 2023

@author: Excellerant
"""

import requests
import pandas as pd
from datetime import date

from _constants import BASE_URL_XBRL_COMPANY_FACTS


class SECAPI:
    def __init__(self, cik:str, lookback:int = 8):
        self.cik = cik
        self.lookback = lookback
        self.header = {'User-Agent': "pythonlearnin@gmail.com"}
        self.url = f"{BASE_URL_XBRL_COMPANY_FACTS}/CIK{cik}.json"


    def set_periods(self):
        curr_qtr = date.today().month // 4 + 1
        curr_year = date.today().year
        period_list = []
        for x in range(0, self.lookback):
            new_year = curr_year - x
            frame_ye = f'CY{new_year}'
            period_list.append(frame_ye)
            for y in range(4, 0, -1):
                if new_year == curr_year:
                    if y >= curr_qtr:
                        pass
                    else:
                        frame_qe = f'CY{new_year}Q{y}'
                        period_list.append(frame_qe)
                else:
                    frame_qe = f'CY{new_year}Q{y}'
                    period_list.append(frame_qe)
        df_frames = pd.DataFrame(index=period_list)

        return df_frames


    def get(self):
        response = requests.get(self.url, headers=self.header)
        response = response.json()

        
        return response

    def clean(self):

        df_final = self.set_periods()
        raw_df = pd.json_normalize(self.get()['facts']['us-gaap'])

        keep_list = ('Assets', 'Liabilities', 'StockholdersEquity', 'LiabilitiesAndStockholdersEquity',
                 'SalesRevenueNet', 'CostOfGoodsAndServicesSold', ' NetIncomeLoss', 'AccountsReceivableNetCurrent',
                 'Revenues', 'SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax')

        for x, col in enumerate(raw_df.columns):
            col_name = col.split('.')[0]
            col_type = col.split('.')[1]

            if col_name in keep_list:
                if col_type == 'units':
                    temp_list = raw_df[col].explode('TEMP')
                    df_temp = (pd.DataFrame(temp_list.apply(pd.Series)))
                    df_temp.frame = df_temp.frame.str.replace('I', '')
                    df_temp = df_temp.rename(columns={'val':f'{col_name}'})
                    df_temp = df_temp.set_index('frame')

                    if df_final.shape[1] == 0:
                        df_final = df_final.merge(df_temp, how='left', left_index=True, right_index=True)
                        df_final = df_final[['end','filed','fy','fp','form',f'{col_name}']]
                    else:
                        df_temp = df_temp[[f'{col_name}']]
                        df_final = df_final.merge(df_temp, how='left', left_index=True, right_index=True)

        df_final = df_final.sort_index(ascending=False).reset_index().rename(columns={'index': 'FRAME'})
        df_final['YEAR'] = [x[2:6] for x in df_final['FRAME']]
        df_final['PERIOD'] = [x[6:] if len(x) > 6 else 'YE' for x in df_final['FRAME']]
        df_final['CALC'] = 0 #DUMMY COLUMN FOR CALCS
        return df_final


df_nvidia = SECAPI('0001045810', 4).clean()
print(df_nvidia[['FRAME', 'YEAR', 'PERIOD', 'end', 'Assets']][df_nvidia['PERIOD']=='Q4'])
print(df_nvidia[['FRAME', 'Assets', 'Liabilities', 'Revenues']][df_nvidia['PERIOD']=='Q4'].set_index('FRAME').T)

df_dak = SECAPI('0000915779', 4).clean()
print(df_dak[['FRAME', 'YEAR', 'PERIOD', 'end', 'Assets']][df_dak['PERIOD']=='Q4'])
print(df_dak[['FRAME', 'Assets', 'Liabilities', 'Revenues']][df_dak['PERIOD']=='Q4'].set_index('FRAME').T)

# df_cf = SECAPI('0000811532', 10).get()
# print(df_cf[['FRAME', 'YEAR', 'PERIOD', 'end', 'Assets']][df_cf['PERIOD']=='Q4'])
