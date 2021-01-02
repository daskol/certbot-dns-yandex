#   encoing: utf8
#   filename: plugin.py

import zope.interface

from logging import getLogger

from certbot.errors import PluginError
from certbot.interfaces import IAuthenticator, IPluginFactory
from certbot.plugins.dns_common import DNSAuthenticator

from .client import Client


logger = getLogger(__name__)


@zope.interface.implementer(IAuthenticator)
@zope.interface.provider(IPluginFactory)
class Authenticator(DNSAuthenticator):
    """DNS Authenticator for Yandex DNS (aka PDD).

    This Authenticator uses the Yandex DNS API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are ' \
                  'using Yandex DNS manager aka PDD for DNS).'

    TTL = 60  # TTL for entry in DNS cache.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records_index = {}

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super().add_parser_arguments(add, default_propagation_seconds=60)
        add('token',
            default=None,
            help='Access token to API. Value could be specified via '
                 'YANDEX_PDD_TOKEN environment variable.',
            type=str)

    def more_info(self) -> str:
        return 'This plugin configures a DNS TXT record to respond to a ' \
               'dns-01 challenge using the Yandex DNS API (aka PDD).'

    def _setup_credentials(self):
        # Just try to instantiate API bindings and check whether access token
        # exists.
        if Client(self.conf('token')).token is None:
            raise PluginError('Unable to get credentials (PDD access token). '
                              'Automatic credentials lookup failed to get '
                              'token from CLI optionsi and environment '
                              'variable.')

    def _perform(self, domain, validation_name, validation):
        logger.debug('perform dns-01 probe for domain %s for record %s',
                     domain, validation_name)

        kwargs = {
            'ttl': Authenticator.TTL,
            'subdomain': validation_name.removesuffix(domain)[:-1],
        }

        record = Client(self.conf('token')) \
            .add(domain, 'TXT', validation, **kwargs)
        self.records_index[(domain, validation_name)] = record

    def _cleanup(self, domain, validation_name, validation):
        logger.debug('cleanup for domain %s for subdomain %s',
                     domain, validation_name)

        if record := self.records_index.pop((domain, validation_name), None):
            Client(self.conf('token')).delete(domain, record.record_id)
