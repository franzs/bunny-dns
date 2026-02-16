bunny-dns
=========

A Python SDK for the `Bunny.net <https://bunny.net>`_ DNS API.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Installation
------------

.. code-block:: bash

   pip install bunny-dns

Quick Start
-----------

.. code-block:: python

   from bunny_dns import BunnyDNS

   client = BunnyDNS(access_key="your-api-key")
   zones = client.list_dns_zones()
   for zone in zones.items:
       print(zone.domain)
