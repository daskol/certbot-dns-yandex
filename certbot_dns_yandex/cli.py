#   encoding: utf8
#   filename: cli.py
"""Simple CLI for viewing and modification of DNS records in Yandex DNS manager
(Pochta-Dlya-Domena aka PDD). Acces token could be issued on the management
page. Follow https://pddimp.yandex.ru/api2/admin/get_token to issue token.
"""

import logging
import os

from argparse import Action, ArgumentParser
from dataclasses import asdict

from .client import Client


class EnvDefault(Action):

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super().__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def add_domain(args):
    argnames = (
        'domain', 'type',
        'content',
        'priority',
        'ttl',
        'subdomain',
        'admin_mail',
        'weight',
        'port',
        'target',
    )

    kwargs = {arg: getattr(args, arg) for arg in argnames}
    record = Client(args.token).add(**kwargs)
    fields = ('record_id', 'type', 'fqdn', 'content')

    for field in fields:
        value = getattr(record, field)
        name = field.replace('_', ' ')
        print(f'{name:>10s}: {value:<}')


def del_domain(args):
    Client(args.token).delete(args.domain, args.record_id)


def list_domains(args):
    domain = args.domain.removesuffix('.')
    records = Client(args.token).list(domain)

    if not records:
        print('no dns records for', domain)
        return

    hdr = '{record_id:>12s} {type:>10s} {ttl:<6s} {fqdn:>24s} {content:28s}'
    fmt = '{record_id:>12d} {type:>10s} {ttl:<6d} {fqdn:>24s} {content:28s}'
    header = hdr.format(record_id='RECORD ID',
                        type='TYPE',
                        fqdn='DOMAIN',
                        ttl='TTL',
                        content='CONTENT')
    print(header)
    for record in records:
        if (fqdn := record.fqdn.removesuffix(domain)) == '':
            record.fqdn = '@'
        else:
            record.fqdn = fqdn.removesuffix('.')
        print(fmt.format(**asdict(record)))


parser = ArgumentParser(description=__doc__)
parser.add_argument('--token', action=EnvDefault, envvar='YANDEX_PDD_TOKEN', type=str, help='access token')  # noqa

subparser = parser.add_subparsers(title='commands')

domain_addition = subparser.add_parser('add')
domain_addition.set_defaults(func=add_domain)
domain_addition.add_argument('domain', type=str, help='domain of interest')
domain_addition.add_argument('type', type=str, help='record type')
domain_addition.add_argument('content', type=str, help='record value')
domain_addition.add_argument('--subdomain', type=str, help='name of subdomain')
domain_addition.add_argument('--ttl', type=int, help='record ttl')
domain_addition.add_argument('--priority', type=int, help='record priority')
domain_addition.add_argument('--admin-mail', type=int, help='email address of domain administrator')  # noqa
domain_addition.add_argument('--weight', type=int, help='weight of SRV record')
domain_addition.add_argument('--port', type=int, help='service port in SRV record')  # noqa
domain_addition.add_argument('--target', type=str, help='canonical hostname of service in SRV record')  # noqa

domain_deletion = subparser.add_parser('rm')
domain_deletion.set_defaults(func=del_domain)
domain_deletion.add_argument('domain', type=str, help='domain of interest')
domain_deletion.add_argument('record_id', type=int, help='identifier of DNS record')  # noqa

domain_listing = subparser.add_parser('ls')
domain_listing.set_defaults(func=list_domains)
domain_listing.add_argument('domain', type=str, help='domain of interest')


def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        subcommands = ', '.join(sorted(subparser.choices.keys()))
        parser.error(f'no subcommand (possible choices are {{{subcommands}}})')
    args.func(args)
