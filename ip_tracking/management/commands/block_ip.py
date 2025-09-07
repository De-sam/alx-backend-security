# ip_tracking/management/commands/block_ip.py
from django.core.management.base import BaseCommand, CommandError
from ipaddress import ip_address as _ip_parse

from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = "Add an IP address to the BlockedIP list. Usage: python manage.py block_ip <IP>"

    def add_arguments(self, parser):
        parser.add_argument("ip", type=str, help="IPv4 or IPv6 address to block")

    def handle(self, *args, **options):
        raw_ip = options["ip"].strip()

        # Validate IP format
        try:
            parsed = _ip_parse(raw_ip)
        except ValueError:
            raise CommandError(f"'{raw_ip}' is not a valid IP address")

        ip_str = str(parsed)

        obj, created = BlockedIP.objects.get_or_create(ip_address=ip_str)
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Blocked IP added: {ip_str}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ IP already blocked: {ip_str}"))
