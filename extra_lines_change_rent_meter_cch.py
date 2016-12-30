#!/usr/bin/env python

# db = 'database'
# user = 'user'
# pwd = 'pwd'
# port = 8069
# uri = 'http://{0}.erp.clients'.format(db)
#
#
# %load https://raw.githubusercontent.com/gisce/powerp-tools/master/extra_lines_change_rent_meter_cch.py

amount_per_day=-0.008857
description = "Abonament del cobrament indegut del lloguer de comptador sense CCH durant el 2016"
start_date = '2016-01-01'
end_date = '2016-12-31'

uos_id = 16 # ALQ/dia

products_ids = [193]

from erppeek import Client
erp = Client(server=uri+":"+str(port), user=user, password=pwd, db=db)

for product_id in products_ids:
    line_ids = erp.model('giscedata.facturacio.factura.linia').search(
        [
            ('product_id','=', product_id)
        ]
    )
    if line_ids:
        lines = erp.model('giscedata.facturacio.factura.linia').read(
            line_ids,
            ['factura_id','quantity','uos_id']
        )

        seen = set()
        for line in lines:
            invoice_id = line['factura_id'][0]
            if invoice_id in seen:
                raise Exception("More than one line per invoice")
            else:
                seen.add(invoice_id)

        invoices_data = {}
        for line in lines:
            invoice_id = line['factura_id'][0]
            invoices_data[invoice_id] = {
                'quantity': line['quantity'],
                'unit': line['uos_id']
            }

        cancelling_invoice_ids = erp.model('giscedata.facturacio.factura').search(
            [('tipo_rectificadora', 'in' , ('R', 'A', 'B'))]
        )
        if cancelling_invoice_ids:
            cancelling_invoices = erp.model('giscedata.facturacio.factura').read(
                cancelling_invoice_ids,
                ['ref']
            )
            cancelled_invoice_ids = [ x['ref'][0] for x in cancelling_invoices ]
            invoice_ids = list(set(invoices_data.keys()) - set(cancelled_invoice_ids))

        invoice_ids = erp.model('giscedata.facturacio.factura').search(
            [
                ('id', 'in', invoice_ids),
                ('polissa_tg', '!=', '1'),
                ('data_inici', '>=', start_date),
                ('data_final', '<=', end_date)
            ]
        )
        if invoice_ids:
            invoices = erp.model('giscedata.facturacio.factura').read(
                invoice_ids,
                ['polissa_id']
            )
        else:
            invoices = []

        for invoice_id in invoice_ids:
            if invoices_data[invoice_id]['unit'][0] != uos_id:
                raise Exception(
                    "Error: invoice unit != ALQ/dia invoice_id {} invoice_unit_id {}"
                    .format(invoice_id, invoices_data[invoice_id]['unit'][0])
                )

        policies = {}
        for invoice in invoices:
            policy_id = invoice['polissa_id'][0]
            policies.setdefault(policy_id, 0)
            policies[policy_id] += invoices_data[invoice['id']]['quantity']
            
	for policy in policies:
            columns = {
                'name': description,
                'polissa_id': policy,
                'uos_id': uos_id,
                'date_from': start_date,
                'date_to': end_date,
                'quantity': policies[policy],
                'price_unit': amount_per_day,
                'date_line_from': start_date,
                'date_line_to': end_date
            }
            erp.model('giscedata.facturacio.extra').create(columns)

