# db = 'database'
# user = 'user'
# pwd = 'pwd'
# port = 8069
# uri = 'http://{0}.erp.clients'.format(db)
#
# date = '2017-03-01'
#
# %load https://raw.githubusercontent.com/gisce/powerp-tools/master/get_cch_policies_without_tg_meter.py

from erppeek import Client
erp = Client(server=uri+":"+str(port), user=user, password=pwd, db=db)

policies = []

policy_amendment_ids = erp.model('giscedata.polissa.modcontractual').search(
    [
         ('data_inici', '=', date),
         ('tg', '=', 1)
    ],
    0,
    None,
    None,
    {'active_test': False}
)
if policy_amendment_ids:
    for policy_amendment in erp.model('giscedata.polissa.modcontractual').browse(
         policy_amendment_ids,
    ):
        meter_id = policy_amendment.polissa_id.comptadors_actius(date,date)
        meter = erp.model('giscedata.lectures.comptador').browse(meter_id)
    
        if meter.tg == False:
            policies.append(policy_amendment.polissa_id.name)
	    print policy_amendment.polissa_id.name

print policies
