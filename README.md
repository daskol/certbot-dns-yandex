# Certbot Plugin: Yandex DNS

*Yandex DNS Authenticator plugin for Certbot*

## Overview

Package provide certbot authenticator plugin for Yandex DNS (aka PDD) which
allows to perform dns-01 probe. This kind of challange is the only way for now
to issue wildcard certificates with certbot.

NOTE This plugin will not be requested to merge in certbot repo until like
issues certbot/certbot#6464, certbot/certbot#6503, and certbot/certbot#6504 are
solved first.

### Installation

The easies way to install plugin is insllation the plugin directly from git
with PIP.

```bash
pip install git+https://github.com/daskol/certbot-dns-yandex.git
```

### Usage

There is nothing special to use the plugin for certificate management.
Essentially, the only things one should do is explicitely specify authenticator
with option `-a` of certbot. Credentials to plugin could be passed either with
CLI option `--dns-yandex-token` or environment variable `YANDEX_PDD_TOKEN`.
The env variable has higher priority then CLI option. See example below.

```bash
export YANDEX_PDD_TOKEN=<secret-token>
certbot certonly -a dns-yandex --dns-yandex-token <secret-token> ...
```

### CLI

The package provides a CLI for management DNS records in Yandex DNS from shell
as well. As soon as the package installed one can list, add, or remove DNS
records (several examples below).

```bash
# List DNS records for a domain.
yandex-dns ls example.org
# Remove domain by DNS record ID for a domain.
yandex-dns rm example.org 31513386
# Add TXT record to DNS for a domain.
yandex-dns add example.org TXT "Hello, world!" --subdomain greeting
```
