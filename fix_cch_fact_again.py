import click

@click.command()
@click.option('-s', '--server', default='http://localhost', help='Server name')
@click.option('-p', '--port', default=8069, help='Server port', type=click.INT)
@click.option('-d', '--database', help='Database name')
@click.option('-u', '--user', default='admin', help='Database user')
@click.option('-w', '--password', default='admin', help='Database password')
def fix_cch_fact_again(server, port, database, user, password):
    # database = 'database'
    # user = 'user'
    # password = 'pwd'
    # port = 8069
    # uri = 'http://{0}.erp.clients'.format(db)
    #
    # batch_name = '04/2016'
    #
    # %load https://raw.githubusercontent.com/gisce/powerp-tools/master/fix_cch_fact_again.py

    from erppeek import Client
    erp = Client(server=server+':'+str(port), user=user, password=password, db=database)

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

if __name__ == '__main__':
    fix_cch_fact_again()

