# db = 'database'
# user = 'user'
# pwd = 'pwd'
# port = 8069
# uri = 'http://{0}.erp.clients'.format(db)
# %load https://raw.githubusercontent.com/gisce/powerp-tools/master/validate_profile_only_with_cch.py

from erppeek import Client
erp = Client(server=uri+":"+str(port), user=user, password=pwd, db=db)

policies = erp.GiscedataPolissa
meters = erp.GiscedataLecturesComptador
tg_profile_validate = erp.TgProfileValidate 

policy_ids = policies.search([('tg','=','1')])
meter_ids = meters.search([('polissa', 'in', policy_ids)])
for meter_id in meter_ids:
    meter_name = meters.build_name_tg(meter_id)
    tg_profile_validate.validate_profile([], [meter_name])
