import pandas as pd
import string
import random

class JobManager:
    
    
    def __init__(self, orders, item_attb):
        
        order_ids = []
        order_items = []
        order_dues = []
        order_starts = []
        order_dests = []
        self.CAP = 30 # need to make this configurable
        
        for o in orders:
            count = 0
            for i in o.items:
                count += 1
                
                order_items.append(i)
            
            if count > 0:
                order_ids = order_ids + [o.id] * count
                order_dues = order_dues + [o.due] * count
                order_starts = order_starts + [o.start] * count
                order_dests = order_dests + [o.dest] * count
        
        order_df = pd.DataFrame.from_dict({'ORDER_ID':order_ids, 
                                                'ITEM':order_items, 
                                                'START':order_starts,
                                                'DUE':order_dues, 
                                                'DEST':order_dests})

        order_df = order_df.join(item_attb.set_index('ITEM'), on='ITEM')
        self.order_df = order_df[['ORDER_ID','ITEM','DEST','START','DUE','VOL']]
        
    def policyAsManyAsPossible(self):
        
        order_df = self.order_df.copy()
        
        
        order_df = order_df.sort_values(by=['DUE', 'VOL'], ascending = [True, False])
        order_df = order_df.reset_index()
        order_df['JOB_ID'] = ""
        
        vol_sum = 0
        job_index = ''.join(list(random.choices(string.ascii_uppercase, k=5)) + list(random.choices(string.digits, k=4)))
        prev_dest = order_df.iloc[0]['DEST']
        for i, row in order_df.iterrows():
            
            if vol_sum + row['VOL'] <= self.CAP and prev_dest == row['DEST']:
                order_df.at[i,'JOB_ID'] = job_index
                vol_sum += row['VOL']
            else :
                vol_sum = row['VOL']
                job_index = ''.join(list(random.choices(string.ascii_uppercase, k=5)) + list(random.choices(string.digits, k=4)))
                order_df.at[i,'JOB_ID'] = job_index
        
        return order_df
    
    def policyAsManyAsPossibleAndBackup(self):
        
        order_df = self.order_df.copy()
        
        
        order_df = order_df.sort_values(by=['DUE', 'VOL'], ascending = [True, False])
        order_df = order_df.reset_index()
        order_df['JOB_ID'] = ""
        
        vol_sum = 0
        job_index = ''.join(list(random.choices(string.ascii_uppercase, k=5)) + list(random.choices(string.digits, k=4)))
        prev_due = order_df.iloc[0]['DUE']
        prev_dest = order_df.iloc[0]['DEST']
        for i, row in order_df.iterrows():
            
            if vol_sum + row['VOL'] <= self.CAP and prev_due == row['DUE'] and prev_dest == row['DEST']:
                order_df.at[i,'JOB_ID'] = job_index
                vol_sum += row['VOL']
                prev_due = row['DUE']
            else :
                vol_sum = row['VOL']
                job_index = ''.join(list(random.choices(string.ascii_uppercase, k=5)) + list(random.choices(string.digits, k=4)))
                order_df.at[i,'JOB_ID'] = job_index
                prev_due = row['DUE']
        
        return order_df
    
    def policyJobByOrder(self):
        
        order_df = self.order_df.copy()
        
        order_ids = order_df['ORDER_ID'].unique()
        order_df['SORT_ATTB'] = order_df['START'] + order_df['DUE']
        order_df = order_df.sort_values(by=['SORT_ATTB', 'VOL'], ascending = [True, False])
        order_df['JOB_ID'] = ""
        # print('before\n',order_df)
        tmp_bag = []
        
        for oi in order_ids:
            
            tmp = order_df[order_df['ORDER_ID'] == oi]
            
            vol_sum = 0
            job_index = ''.join(list(random.choices(string.ascii_uppercase, k=5)) + list(random.choices(string.digits, k=4)))
            
            for i, row in tmp.iterrows():
            
                if vol_sum + row['VOL'] <= self.CAP :
                    tmp.at[i,'JOB_ID'] = job_index
                    vol_sum += row['VOL']
                else :
                    vol_sum = row['VOL']
                    job_index = ''.join(list(random.choices(string.ascii_uppercase, k=5)) + list(random.choices(string.digits, k=4)))
                    tmp.at[i,'JOB_ID'] = job_index
                    
            tmp_bag.append(tmp)
        
        
        out_df = tmp_bag[0].append(tmp_bag[1:])
        


        # print('end\n',out_df.sort_values(by=['START', 'VOL'] , ascending = [True, False]))

        # return out_df.sort_values(by=['DUE', 'VOL'] , ascending = [True, False])
        return out_df.sort_values(by=['SORT_ATTB'] )