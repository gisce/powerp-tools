# db = 'database'
# user = 'user'
# pwd = 'pwd'
# port = 8069
# uri = 'http://{0}.erp.clients'.format(db)
# %load https://raw.githubusercontent.com/gisce/powerp-tools/master/profiles_assign_invoice.py

from erppeek import Client
erp = Client(server=uri+":"+str(port), user=user, password=pwd, db=db)

invoices = erp.model('giscedata.facturacio.factura')
profiles = erp.model('giscedata.perfils.perfil')

search_params = [
    ('state', 'in', ('open', 'paid')),
    ('invoice_id.journal_id.code', 'ilike', 'ENERGIA%')
]

search_params_cancelling = search_params[:]
search_params_cancelling.append(
    ('tipo_rectificadora', 'in' , ('R', 'A', 'B'))
)
        
cancelling_invoice_ids = invoices.search(search_params_cancelling)

if cancelling_invoice_ids:
    cancelling_invoices = invoices.read(
        cancelling_invoice_ids,
        ['ref']
    )
    cancelled_invoice_ids = [ x['ref'][0] for x in cancelling_invoices ]

    search_params.extend(
        [
            ('id', 'not in', cancelled_invoice_ids)
        ]
    )

search_params.extend(
    [
        ('tipo_rectificadora', 'in', ('N', 'R')),
    ]
)

invoice_ids = invoices.search(search_params)

if invoice_ids:
    for invoice in invoices.browse(invoice_ids):
        first_profile = invoice.data_inici.replace('-','')
        last_profile = invoice.data_final.replace('-','') + '24' 
        profile_ids = profiles.search(
            [
                ('cups', '=', invoice.polissa_id.cups.name),
                ('name', '>=', first_profile),
                ('name', '<=', last_profile)
            ]
        )
        if profile_ids:
            profiles.write(profile_ids, {'invoice': invoice.id})
