'''
Quick script to contact the br-EFB bank modules and plot data from them
Requires the brEFB_CJH library I wrote to do the communication
9/28/2019 CJH
'''
print("Importing libraries (~ 5s) ...", flush=True)
import brEFB_CJH as brefb
import os, sys
from datetime import datetime
bank = sys.argv[1]
end_time = float(sys.argv[2])
brefb.set_banks()
print("Acquiring data from bank {0} ...".format(bank), flush=True)
df_br, label = brefb.prepare_all_telemetry(end_time=end_time, dt=.1, axes=4, bank=bank, print_spark=True)
#fname = 'test_bank_' + bank.lower() +'.png'
fname = datetime.now().strftime('%Y%m%d_%H%M')+ '_bank_'+ bank.lower() +'.png'
print("\nGenerating image and saving as {0} (~5s) ...".format(fname), flush=True)
brefb.create_matplot(df_br,label,axes=4,save=True,fname='.//png//'+ fname)
#hv.save(br_plot, file_name)
print("Calling image ...", flush=True)
#os.system('gpicview '+ './/png//'+ fname + ' &')
os.system('display '+ './/png//'+ fname + ' &')