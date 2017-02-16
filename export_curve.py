# encoding=utf8
from urlparse import urlparse
from datetime import date, timedelta
import logging

import click
from erppeek import Client


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Export CCH')


@click.command()
@click.option('-s', '--server', help='PowERP Server Uri')
@click.option('-d', '--days-ago', type=click.INT, help='Number of days ago')
def main(server, days_ago):
    url = urlparse(server)
    server = '{p.scheme}://{p.hostname}:{p.port}'.format(p=url)
    db = url.path.lstrip('/')
    user = url.username
    password = url.password
    c = Client(server, db, user, password)
    logger.info('Connected to %s@%s', server, db)
    d = (date.today() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

    export_p5d = c.model('wizard.export.comer.p5d')
    wiz = export_p5d.create({
        'date_from': d,
        'date_to': d,
        'file_format': 'cch_val'
    })
    wiz.export()
    logger.info('Queued P5D export for %s', d)


if __name__ == '__main__':
    main()
