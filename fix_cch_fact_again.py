# db = 'database'
# user = 'user'
# pwd = 'pwd'
# port = 8069
# uri = 'http://{0}.erp.clients'.format(db)
#
# batch_name = '04/2016'
#
# %load https://raw.githubusercontent.com/gisce/powerp-tools/master/fix_cch_fact_again.py

from erppeek import Client
erp = Client(server=uri+":"+str(port), user=user, password=pwd, db=db)

for id in erp.GiscedataFacturacioFactura.search(
    [
        ('polissa_tg', '=', '1'),
        ('cch_fact_available', '=', False),
        ('lot_facturacio.name', '=', batch_name)
    ]
):
    try:
        erp.GiscedataFacturacioFactura.fix_cch_fact([id])
    except:
        pass
