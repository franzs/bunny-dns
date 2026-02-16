"""Tests for data model parsing."""

import pytest

from bunny_dns import (
    AccelerationStatus,
    CertificateKeyType,
    LogAnonymizationType,
    MonitorStatus,
    MonitorType,
    RecordType,
    SmartRoutingType,
)
from bunny_dns.models import (
    DnsRecord,
    DnsRecordInput,
    DnsSecDsRecord,
    DnsZone,
    DnsZoneImportResult,
    DnsZoneList,
    EnvironmentalVariable,
    GeolocationInfo,
    IPGeoLocationInfo,
)


# ---------------------------------------------------------------------------
# IPGeoLocationInfo
# ---------------------------------------------------------------------------
class TestIPGeoLocationInfo:
    def test_from_dict(self):
        data = {
            "ASN": 13335,
            "CountryCode": "US",
            "Country": "United States",
            "OrganizationName": "Cloudflare Inc",
            "City": "San Francisco",
        }
        info = IPGeoLocationInfo.from_dict(data)
        assert info is not None
        assert info.asn == 13335
        assert info.country_code == "US"
        assert info.country == "United States"
        assert info.organization_name == "Cloudflare Inc"
        assert info.city == "San Francisco"

    def test_from_dict_none(self):
        assert IPGeoLocationInfo.from_dict(None) is None

    def test_from_dict_empty(self):
        assert IPGeoLocationInfo.from_dict({}) is None

    def test_from_dict_minimal(self):
        info = IPGeoLocationInfo.from_dict({"ASN": 100})
        assert info is not None
        assert info.asn == 100
        assert info.country_code is None


# ---------------------------------------------------------------------------
# GeolocationInfo
# ---------------------------------------------------------------------------
class TestGeolocationInfo:
    def test_from_dict(self):
        data = {
            "Latitude": 51.5074,
            "Longitude": -0.1278,
            "Country": "United Kingdom",
            "City": "London",
        }
        info = GeolocationInfo.from_dict(data)
        assert info is not None
        assert info.latitude == 51.5074
        assert info.longitude == -0.1278
        assert info.country == "United Kingdom"
        assert info.city == "London"

    def test_from_dict_none(self):
        assert GeolocationInfo.from_dict(None) is None

    def test_from_dict_minimal(self):
        info = GeolocationInfo.from_dict({"Latitude": 0.0, "Longitude": 0.0})
        assert info is not None
        assert info.country is None
        assert info.city is None


# ---------------------------------------------------------------------------
# EnvironmentalVariable
# ---------------------------------------------------------------------------
class TestEnvironmentalVariable:
    def test_from_dict(self):
        ev = EnvironmentalVariable.from_dict({"Name": "KEY", "Value": "val"})
        assert ev is not None
        assert ev.name == "KEY"
        assert ev.value == "val"

    def test_from_dict_none(self):
        assert EnvironmentalVariable.from_dict(None) is None

    def test_from_dict_empty(self):
        assert EnvironmentalVariable.from_dict({}) is None


# ---------------------------------------------------------------------------
# DnsRecord
# ---------------------------------------------------------------------------
class TestDnsRecord:
    def test_from_dict_minimal(self, sample_record_data):
        record = DnsRecord.from_dict(sample_record_data)
        assert record.id == 101
        assert record.type == RecordType.A
        assert record.ttl == 300
        assert record.value == "1.2.3.4"
        assert record.name == "www"
        assert record.weight == 0
        assert record.priority == 0
        assert record.port == 0
        assert record.accelerated is False
        assert record.disabled is False
        assert record.comment == "Test record"
        assert record.monitor_status == MonitorStatus.UNKNOWN
        assert record.monitor_type == MonitorType.NONE
        assert record.smart_routing_type == SmartRoutingType.NONE
        assert record.acceleration_status == AccelerationStatus.NONE

    def test_from_dict_full(self, sample_record_data_full):
        record = DnsRecord.from_dict(sample_record_data_full)
        assert record.id == 202
        assert record.weight == 100
        assert record.priority == 10
        assert record.port == 8080
        assert record.flags == 128
        assert record.tag == "issue"
        assert record.accelerated is True
        assert record.accelerated_pull_zone_id == 999
        assert record.link_name == "my-link"
        assert record.auto_ssl_issuance is True

        # IPGeoLocationInfo
        assert record.ip_geo_location_info is not None
        assert record.ip_geo_location_info.asn == 13335
        assert record.ip_geo_location_info.city == "San Francisco"

        # GeolocationInfo
        assert record.geolocation_info is not None
        assert record.geolocation_info.latitude == 37.7749
        assert record.geolocation_info.longitude == -122.4194

        # Enums
        assert record.monitor_status == MonitorStatus.ONLINE
        assert record.monitor_type == MonitorType.HTTP
        assert record.smart_routing_type == SmartRoutingType.LATENCY
        assert record.acceleration_status == AccelerationStatus.COMPLETED

        # Environmental variables
        assert len(record.environmental_variables) == 2
        assert record.environmental_variables[0].name == "ENV_KEY"
        assert record.environmental_variables[1].value == "val2"

        assert record.latency_zone == "europe"

    def test_from_dict_missing_optional_fields(self):
        data = {
            "Id": 1,
            "Ttl": 300,
            "Weight": 0,
            "Priority": 0,
            "Port": 0,
            "Accelerated": False,
            "AcceleratedPullZoneId": 0,
            "GeolocationLatitude": 0.0,
            "GeolocationLongitude": 0.0,
            "Disabled": False,
            "AutoSslIssuance": False,
        }
        record = DnsRecord.from_dict(data)
        assert record.id == 1
        assert record.type is None
        assert record.value is None
        assert record.name is None
        assert record.ip_geo_location_info is None
        assert record.geolocation_info is None
        assert record.environmental_variables == []
        assert record.comment is None

    def test_from_dict_string_enums(self):
        """Test that string enum values also parse correctly."""
        data = {
            "Id": 1,
            "Type": "CNAME",
            "Ttl": 300,
            "Value": "example.com",
            "Name": "alias",
            "Weight": 0,
            "Priority": 0,
            "Port": 0,
            "Accelerated": False,
            "AcceleratedPullZoneId": 0,
            "GeolocationLatitude": 0.0,
            "GeolocationLongitude": 0.0,
            "Disabled": False,
            "AutoSslIssuance": False,
            "MonitorStatus": "Online",
            "MonitorType": "Ping",
            "SmartRoutingType": "Geolocation",
            "AccelerationStatus": "Pending",
        }
        record = DnsRecord.from_dict(data)
        assert record.type == RecordType.CNAME
        assert record.monitor_status == MonitorStatus.ONLINE
        assert record.monitor_type == MonitorType.PING
        assert record.smart_routing_type == SmartRoutingType.GEOLOCATION
        assert record.acceleration_status == AccelerationStatus.PENDING


# ---------------------------------------------------------------------------
# DnsRecordInput
# ---------------------------------------------------------------------------
class TestDnsRecordInput:
    def test_to_dict_minimal(self):
        inp = DnsRecordInput(type=RecordType.A, value="1.2.3.4", ttl=300)
        d = inp.to_dict()
        assert d["Type"] == 0
        assert d["Value"] == "1.2.3.4"
        assert d["Ttl"] == 300
        assert "Id" not in d
        assert "Name" not in d

    def test_to_dict_full(self):
        inp = DnsRecordInput(
            id=42,
            type=RecordType.MX,
            ttl=3600,
            value="mail.example.com",
            name="",
            weight=10,
            priority=10,
            flags=0,
            tag="issue",
            port=25,
            pull_zone_id=100,
            script_id=200,
            accelerated=True,
            monitor_type=MonitorType.HTTP,
            geolocation_latitude=51.5,
            geolocation_longitude=-0.1,
            latency_zone="europe",
            smart_routing_type=SmartRoutingType.LATENCY,
            disabled=False,
            environmental_variables=[
                EnvironmentalVariable(name="K", value="V"),
            ],
            comment="My record",
            auto_ssl_issuance=True,
        )
        d = inp.to_dict()
        assert d["Id"] == 42
        assert d["Type"] == 4  # MX
        assert d["Ttl"] == 3600
        assert d["Value"] == "mail.example.com"
        assert d["Name"] == ""
        assert d["Weight"] == 10
        assert d["Priority"] == 10
        assert d["Flags"] == 0
        assert d["Tag"] == "issue"
        assert d["Port"] == 25
        assert d["PullZoneId"] == 100
        assert d["ScriptId"] == 200
        assert d["Accelerated"] is True
        assert d["MonitorType"] == 2  # Http
        assert d["GeolocationLatitude"] == 51.5
        assert d["GeolocationLongitude"] == -0.1
        assert d["LatencyZone"] == "europe"
        assert d["SmartRoutingType"] == 1  # Latency
        assert d["Disabled"] is False
        assert d["EnviromentalVariables"] == [{"Name": "K", "Value": "V"}]
        assert d["Comment"] == "My record"
        assert d["AutoSslIssuance"] is True

    def test_to_dict_empty(self):
        inp = DnsRecordInput()
        d = inp.to_dict()
        assert d == {}

    def test_to_dict_flags_validation(self):
        with pytest.raises(ValueError, match="flags must be between 0 and 255"):
            DnsRecordInput(flags=256).to_dict()

        with pytest.raises(ValueError, match="flags must be between 0 and 255"):
            DnsRecordInput(flags=-1).to_dict()

    def test_to_dict_flags_boundary(self):
        assert DnsRecordInput(flags=0).to_dict() == {"Flags": 0}
        assert DnsRecordInput(flags=255).to_dict() == {"Flags": 255}

    def test_mutable(self):
        """DnsRecordInput should be mutable."""
        inp = DnsRecordInput()
        inp.id = 42
        inp.type = RecordType.A
        assert inp.id == 42
        assert inp.type == RecordType.A


# ---------------------------------------------------------------------------
# DnsZone
# ---------------------------------------------------------------------------
class TestDnsZone:
    def test_from_dict(self, sample_zone_data):
        zone = DnsZone.from_dict(sample_zone_data)
        assert zone.id == 12345
        assert zone.domain == "example.com"
        assert zone.nameservers_detected is True
        assert zone.custom_nameservers_enabled is False
        assert zone.nameserver1 == "ns1.bunny.net"
        assert zone.nameserver2 == "ns2.bunny.net"
        assert zone.soa_email == "admin@example.com"
        assert zone.logging_enabled is True
        assert zone.logging_ip_anonymization_enabled is True
        assert zone.log_anonymization_type == LogAnonymizationType.ONE_DIGIT
        assert zone.dns_sec_enabled is False
        assert zone.certificate_key_type == CertificateKeyType.ECDSA
        assert zone.date_modified is not None
        assert zone.date_created is not None
        assert zone.nameservers_next_check is not None
        assert len(zone.records) == 1
        assert zone.records[0].id == 101

    def test_from_dict_no_records(self, sample_zone_data):
        sample_zone_data["Records"] = None
        zone = DnsZone.from_dict(sample_zone_data)
        assert zone.records == []

    def test_from_dict_log_anonymization_drop(self, sample_zone_data):
        sample_zone_data["LogAnonymizationType"] = 1
        zone = DnsZone.from_dict(sample_zone_data)
        assert zone.log_anonymization_type == LogAnonymizationType.DROP

    def test_from_dict_certificate_key_rsa(self, sample_zone_data):
        sample_zone_data["CertificateKeyType"] = 1
        zone = DnsZone.from_dict(sample_zone_data)
        assert zone.certificate_key_type == CertificateKeyType.RSA

    def test_from_dict_minimal(self):
        data = {
            "Id": 1,
            "DateModified": "2024-01-01T00:00:00Z",
            "DateCreated": "2024-01-01T00:00:00Z",
            "NameserversDetected": False,
            "CustomNameserversEnabled": False,
            "NameserversNextCheck": "2024-01-02T00:00:00Z",
            "LoggingEnabled": False,
            "LoggingIPAnonymizationEnabled": False,
            "DnsSecEnabled": False,
        }
        zone = DnsZone.from_dict(data)
        assert zone.id == 1
        assert zone.domain is None
        assert zone.records == []
        assert zone.log_anonymization_type is None
        assert zone.certificate_key_type is None


# ---------------------------------------------------------------------------
# DnsZoneList
# ---------------------------------------------------------------------------
class TestDnsZoneList:
    def test_from_dict(self, sample_zone_list_data):
        result = DnsZoneList.from_dict(sample_zone_list_data)
        assert result.current_page == 1
        assert result.total_items == 1
        assert result.has_more_items is False
        assert len(result.items) == 1
        assert result.items[0].domain == "example.com"

    def test_from_dict_empty(self):
        data = {
            "CurrentPage": 1,
            "TotalItems": 0,
            "HasMoreItems": False,
            "Items": [],
        }
        result = DnsZoneList.from_dict(data)
        assert result.items == []
        assert result.total_items == 0

    def test_from_dict_multiple_pages(self):
        data = {
            "CurrentPage": 2,
            "TotalItems": 50,
            "HasMoreItems": True,
            "Items": [],
        }
        result = DnsZoneList.from_dict(data)
        assert result.current_page == 2
        assert result.total_items == 50
        assert result.has_more_items is True

    def test_from_dict_null_items(self):
        data = {
            "CurrentPage": 1,
            "TotalItems": 0,
            "HasMoreItems": False,
            "Items": None,
        }
        result = DnsZoneList.from_dict(data)
        assert result.items == []


# ---------------------------------------------------------------------------
# DnsZoneImportResult
# ---------------------------------------------------------------------------
class TestDnsZoneImportResult:
    def test_from_dict(self, sample_import_result_data):
        result = DnsZoneImportResult.from_dict(sample_import_result_data)
        assert result.records_successful == 10
        assert result.records_failed == 2
        assert result.records_skipped == 1

    def test_from_dict_all_zero(self):
        data = {"RecordsSuccessful": 0, "RecordsFailed": 0, "RecordsSkipped": 0}
        result = DnsZoneImportResult.from_dict(data)
        assert result.records_successful == 0
        assert result.records_failed == 0
        assert result.records_skipped == 0


# ---------------------------------------------------------------------------
# DnsSecDsRecord
# ---------------------------------------------------------------------------
class TestDnsSecDsRecord:
    def test_from_dict(self, sample_dnssec_data):
        ds = DnsSecDsRecord.from_dict(sample_dnssec_data)
        assert ds.enabled is True
        assert ds.ds_record == "example.com. 3600 IN DS 12345 13 2 ABCDEF..."
        assert ds.digest == "ABCDEF1234567890"
        assert ds.digest_type == "SHA-256"
        assert ds.algorithm == 13
        assert ds.public_key == "BASE64PUBLICKEY=="
        assert ds.key_tag == 12345
        assert ds.flags == 257
        assert ds.ds_configured is False

    def test_from_dict_minimal(self):
        data = {
            "Enabled": False,
            "Algorithm": 0,
            "KeyTag": 0,
            "Flags": 0,
            "DsConfigured": False,
        }
        ds = DnsSecDsRecord.from_dict(data)
        assert ds.enabled is False
        assert ds.ds_record is None
        assert ds.digest is None
        assert ds.public_key is None
