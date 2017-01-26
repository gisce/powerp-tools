# encoding=utf8
from urlparse import urlparse
from datetime import date, timedelta
import logging

import click
from erppeek import Client


logger = logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('-s', '--server', help='PowERP Server Uri')
@click.option('-d', '--days-ago', type=click.INT, help='Number of days ago')
def main(server, days_ago):
    uri = urlparse(server)
    server = '{p.scheme}://{p.hostname}:{p.port}'.format(p=url)
    db = url.path.lstrip('/')
    user = url.username
    password = url.password
    c = Client(server, db, user, password)
    logger.info('Connected to %s@%s', server, db)
    date = (date.today() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

    export_p5d = c.model('wizard.export.comer.p5d')
    wiz_id = export_p5d.create({
        'date_from': date,
        'date_to': date
        'file_format': 'cch_val'
    })
    logger.info('Generating P5D for %s', date)
    export_p5d.export([wiz_id])
    logger.info('P5D exported')
