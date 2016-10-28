#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime

from erppeek import Client
import csv
import sys
import click

dbname = os.getenv('OPENERP_DB', 'DB_NAME')
port = int(os.getenv('OPENERP_PORT', 28069))
user = os.getenv('OPENERP_USER', 'root')
pwd = os.getenv('OPENERP_PASSWORD', '*******')

fesho = True
step_by_step = False 

# polissa.id,polissa.name

# fitxer = len(sys.argv) > 1 and sys.argv[1] or '/tmp/polisses.txt'
# lot_facturacio = len(sys.argv) > 2 and sys.argv[2] or 79

def main(fitxer, data_activacio, mod_contract=False):
    path, filename = os.path.split(fitxer)
    log_file = os.path.join(path, '{0}_{1}'.format('LOG', filename))
    logger = logging.getLogger('myapp')
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info('#######Start now {0}'.format(datetime.today()))
    polisses = []
    with open(fitxer, 'r') as fpc:
        polreader = csv.reader(fpc)
        for lin in polreader:
            polisses.append(lin)

    vals_mod = {'tg': '1'}
    # data_activacio = '2015-07-01'

    O = Client('http://localhost:%d' % port, dbname, user, pwd)
    for pol in polisses:
        pol_id = int(pol[0])
        try:
            polissa = O.GiscedataPolissa.get(pol_id)
       
            polissa.send_signal('modcontractual')
            polissa.write(vals_mod)
            wz_crear_mc_obj = O.GiscedataPolissaCrearContracte
            ctx = {'active_id': pol_id, 'lang': 'es_ES'}
            params = {'duracio': 'actual', 'accio': 'nou'}
    
            wiz = wz_crear_mc_obj.create(params, ctx)
            wiz_id = wiz.id
            #wiz = wz_crear_mc_obj.get(wiz_id, ctx)
            res = wz_crear_mc_obj.onchange_duracio([wiz_id], data_activacio,
                                                   wiz.duracio, ctx)
            result_atr = None
            if res.get('warning', False):
                params = {'accio': 'modificar'}
                if mod_contract:
                    logger.info('%s (%s) Try to modify modcon' % (
                        pol[1], pol_id) 
                    )
                    wiz = wz_crear_mc_obj.create(params, ctx)
                    wiz_id = wiz.id
                    #wiz = wz_crear_mc_obj.browse(wiz_id, ctx)
                    wiz.action_crear_contracte()
                    result_atr = O.GiscedataPolissa.crear_cas_atr(pol_id, 'D1')
                else:
                   logger.warning('%s (%s) WARNING modcon no creada' % (
                       pol[1], pol_id))
                   polissa.send_signal('undo_modcontractual')
            else:
                wiz.write({'data_final': res['value']['data_final'] or '',
                           'data_inici': data_activacio})
                wiz.action_crear_contracte()
                # Create D1
                result_atr = O.GiscedataPolissa.crear_cas_atr(pol_id, 'D1')
                logger.info('%s (%s) OK' % (pol[1], pol_id))
            if result_atr and len(result_atr) == 2:
                if 'ERROR' in result_atr[1].upper():
                    logger.warning('%s (%s) WARNING ATR case not created with message %s' % (
                        pol[1], pol_id, result_atr[1]))
        except Exception, e:
            logger.error('%s (%s) ERROR actualizando póliza: %s' % (
                pol[1], pol_id, e))
            polissa.send_signal('undo_modcontractual')

        sys.stdout.flush()
    if step_by_step:
                sys.stderr.write('Prem una tecla per continuar ...')
                raw_input()

@click.command()
@click.option('-f', '--filepath', default='/tmp/polisses.txt',
              help='Path to policy file')
@click.option('-d', '--start-date', help='Start date')
@click.option('-m', '--modify-contract', help='Modifiy current contract', default=True)
def tg_to_mensual(**kwargs):
    main(kwargs['filepath'], kwargs['start_date'], kwargs['modify_contract'])


if __name__ == "__main__":
    tg_to_mensual()
