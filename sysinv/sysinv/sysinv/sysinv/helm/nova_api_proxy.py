#
# Copyright (c) 2018 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from sysinv.common import exception
from sysinv.helm import common
from sysinv.helm import openstack


class NovaApiProxyHelm(openstack.OpenstackBaseHelm):
    """Class to encapsulate helm operations for the nova chart"""

    CHART = common.HELM_CHART_NOVA_API_PROXY

    SERVICE_NAME = common.HELM_CHART_NOVA_API_PROXY
    AUTH_USERS = ['nova']

    def get_overrides(self, namespace=None):

        overrides = {
            common.HELM_NS_OPENSTACK: {
                'pod': {
                    'user': {
                        'nova_api_proxy': {
                            'uid': 0
                        }
                    },
                    'replicas': {
                        'proxy': self._num_controllers()
                    }
                },
                'conf': {
                    'nova_api_proxy': {
                        'DEFAULT': {
                            'nfvi_compute_listen': self._get_management_address()
                        },
                    }
                },
                'endpoints': self._get_endpoints_overrides(),
            }
        }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]
        elif namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)
        else:
            return overrides

    def _get_endpoints_overrides(self):
        nova_service_name = self._operator.chart_operators[
            common.HELM_CHART_NOVA].SERVICE_NAME

        return {
            'identity': {
                'auth': self._get_endpoints_identity_overrides(
                    nova_service_name, self.AUTH_USERS),
            },
            'compute': {
                'host_fqdn_override':
                    self._get_endpoints_host_fqdn_overrides(
                        common.HELM_CHART_NOVA),
                'port': self._get_endpoints_port_api_public_overrides(),
                'scheme': self._get_endpoints_scheme_public_overrides(),
            },
        }
