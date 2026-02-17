#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Neil John (@neijohn) <neijohn@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
__copyright__ = "Copyright (c) 2025 Cisco and/or its affiliates."
__author__ = "Neil John"

DOCUMENTATION = """
---

module: nd_manage_vpc_pairs
short_description: Manage vPC pairs in Nexus devices.
version_added: "1.0.0"
author: Neil John (@neijohn)
description:
- Create, update, delete, override, and query vPC pairs on Nexus devices.
- Supports state-based operations with intelligent diff calculation for optimal API calls.
- Uses Pydantic model validation for vPC pair configurations.
options:
    state:
        choices:
        - merged
        - replaced
        - deleted
        - overridden
        - query
        default: merged
        description:
        - The state of the vPC pair configuration after module completion.
        type: str
    deploy:
        description:
        - Deploy the configuration changes to the fabric after applying them.
        - When true, automatically saves the configuration and then triggers a fabric deployment via POST to /api/v1/manage/fabrics/{fabric}/actions/deploy?forceShowRun=true
        - Configuration is saved via POST to /api/v1/manage/fabrics/{fabric}/actions/configSave before deployment.
        - Deployment only occurs if there are actual changes (diff is not empty), pending operations, or switches in transitional states.
        - Cannot be used when state is 'query'.
        - Only applicable for states that modify configuration (merged, replaced, deleted, overridden).
        type: bool
        default: false
    dry_run:
        description:
        - When true, shows what changes would be made without actually executing them.
        - Displays all API requests that would be sent, the diff of changes, and whether deployment would occur.
        - No actual configuration changes are made to the fabric.
        - Useful for validating configurations and understanding what operations would be performed.
        - Cannot be used when state is 'query'.
        type: bool
        default: false
    config:
        description:
        - A list of vPC pair configuration dictionaries.
        type: list
        elements: dict
        suboptions:
            peer1_switch_id:
                description:
                - peer1 switch serial number for the vPC pair.
                - Must be a valid switch serial number.
                required: true
                type: str
            peer2_switch_id:
                description:
                - peer2 switch serial number for the vPC pair.
                - Must be a valid switch serial number.
                required: true
                type: str
            useVirtualPeerLink:
                description:
                - Enable virtual pair link for the vPC pair.
                - When true, virtual pair link is present and configured.
                - When false, physical pair link is used.
                type: bool
                default: true
notes:
    - This module uses the RestSend architecture for improved testability and reliability
    - RestSend provides protocol-based HTTP abstraction with automatic retry logic
    - Results are aggregated using the Results class for consistent output format
    - Check mode is fully supported via RestSend's built-in check_mode handling
    - The dry_run parameter maps to Ansible's check_mode internally
"""

EXAMPLES = """
# Create a new vPC pair with virtual pair link
- name: Create vPC pair with virtual pair link
  cisco.nd.nd_manage_vpc_pairs:
    state: merged
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: true

# Create a vPC pair with physical pair link
- name: Create vPC pair with physical pair link
  cisco.nd.nd_manage_vpc_pairs:
    state: merged
    config:
      - peer1_switch_id: "FDO23040Q87"
        peer2_switch_id: "FDO23040Q88"
        useVirtualPeerLink: false

# Create multiple vPC pairs
- name: Create multiple vPC pairs
  cisco.nd.nd_manage_vpc_pairs:
    state: merged
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: true
      - peer1_switch_id: "FDO23040Q87"
        peer2_switch_id: "FDO23040Q88"
        useVirtualPeerLink: false

# Replace existing vPC pair configuration
- name: Replace vPC pair configuration
  cisco.nd.nd_manage_vpc_pairs:
    state: replaced
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: false

# Delete a specific vPC pair
- name: Delete vPC pair
  cisco.nd.nd_manage_vpc_pairs:
    state: deleted
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"

# Query existing vPC pairs
- name: Query all vPC pairs
  cisco.nd.nd_manage_vpc_pairs:
    state: query

# Query specific vPC pair
- name: Query specific vPC pair
  cisco.nd.nd_manage_vpc_pairs:
    state: query
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"

# Override vPC pair configurations (replace all with specified configs)
- name: Override all vPC pair configurations
  cisco.nd.nd_manage_vpc_pairs:
    state: overridden
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: true
      - peer1_switch_id: "FDO23040Q89"
        peer2_switch_id: "FDO23040Q90"
        useVirtualPeerLink: false

# Override without any new vPC pairs (delete all existing)
- name: Override without any new vPC pairs
  cisco.nd.nd_manage_vpc_pairs:
    state: overridden

# Create vPC pair and deploy the configuration changes
# Note: When deploy=true, deployment only occurs if there are actual changes or pending operations
# Configuration is automatically saved before deployment
- name: Create vPC pair and deploy changes
  cisco.nd.nd_manage_vpc_pairs:
    state: merged
    deploy: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: true

# Use dry run to preview what changes would be made without executing them
# Shows all planned API requests, diff information, and deployment decision
- name: Preview vPC pair changes with dry run
  cisco.nd.nd_manage_vpc_pairs:
    state: merged
    deploy: true
    dry_run: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: true

# Dry run to check what deployment actions would be taken
- name: Preview deployment actions only
  cisco.nd.nd_manage_vpc_pairs:
    state: query
    deploy: true
    dry_run: true
- name: Create vPC pair with deployment
  cisco.nd.nd_manage_vpc_pairs:
    state: merged
    deploy: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: true

# Replace vPC pair configuration and deploy changes
# Note: Configuration save and deploy happen automatically when deploy=true
- name: Replace vPC pair with deployment
  cisco.nd.nd_manage_vpc_pairs:
    state: replaced
    deploy: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
        useVirtualPeerLink: false

# Delete vPC pair and deploy the changes
# Note: Configuration is saved automatically before deployment
- name: Delete vPC pair with deployment
  cisco.nd.nd_manage_vpc_pairs:
    state: deleted
    deploy: true
    config:
      - peer1_switch_id: "FDO23040Q85"
        peer2_switch_id: "FDO23040Q86"
"""

RETURN = """
changed:
    description: Whether the module made any changes
    type: bool
    returned: always
    sample: true
diff:
    description: Dictionary of configurations grouped by operation type (POST, PUT, DELETE). Only populated with keys for operations that were actually performed.
    type: dict
    returned: always
    sample: {
        "POST": [
            {
                "peer1SwitchId": "FDO23040Q85",
                "peer2SwitchId": "FDO23040Q86",
                "useVirtualPeerLink": true
            }
        ],
        "PUT": [
            {
                "peer1SwitchId": "FDO23040Q85",
                "peer2SwitchId": "FDO23040Q86",
                "useVirtualPeerLink": false
            }
        ]
    }
response:
    description: List of API responses from the Nexus Dashboard with operation context
    type: list
    returned: always
    sample: [
        {
            "vpc_pair_key": "FDO23040Q85-FDO23040Q86",
            "operation": "POST",
            "path": "/api/v1/manage/fabrics/fabric1/vpcPairs",
            "response": {
                "status": "success",
                "message": "vPC pair created successfully"
            }
        }
    ]
warnings:
    description: List of warning messages
    type: list
    returned: when applicable
    sample: []
query:
    description: Current state of vPC pairs (only returned in query state). The pending_create_vpc_pairs and pending_delete_vpc_pairs keys are only included if there are items in those lists.
    type: dict
    returned: when state is query
    sample: {
        "vpc_pairs": [
            {
                "peer1SwitchId": "FDO23040Q85",
                "peer2SwitchId": "FDO23040Q86",
                "useVirtualPeerLink": true
            }
        ],
        "pending_create_vpc_pairs": [
            {
                "peer1SwitchId": "FDO23040Q87",
                "peer2SwitchId": "FDO23040Q88",
                "useVirtualPeerLink": false
            }
        ],
        "pending_delete_vpc_pairs": [
            {
                "peer1SwitchId": "FDO23040Q89",
                "peer2SwitchId": "FDO23040Q90",
                "useVirtualPeerLink": true
            }
        ]
    }
pending_create_pairs_not_in_delete:
    description: List of vPC pairs in pending create state that are not specified in delete wants
    type: list
    returned: when state is deleted
    sample: [
        {
            "peer1SwitchId": "FDO23040Q87",
            "peer2SwitchId": "FDO23040Q88",
            "useVirtualPeerLink": false
        }
    ]
pending_delete_pairs_not_in_delete:
    description: List of vPC pairs in pending delete state that are not specified in delete wants
    type: list
    returned: when state is deleted
    sample: [
        {
            "peer1SwitchId": "FDO23040Q89",
            "peer2SwitchId": "FDO23040Q90",
            "useVirtualPeerLink": true
        }
    ]
result:
    description: List of parsed results from RestSend with success/changed/found flags and sequence numbers for request tracking
    type: list
    returned: always
    sample: [
        {
            "success": true,
            "changed": true,
            "sequence_number": 1
        },
        {
            "success": true,
            "changed": false,
            "found": true,
            "sequence_number": 2
        }
    ]
metadata:
    description: List of operation metadata with vpc_pair_key, operation type, and API path information
    type: list
    returned: always
    sample: [
        {
            "vpc_pair_key": "FDO23040Q85-FDO23040Q86",
            "operation": "create",
            "path": "/api/v1/manage/fabrics/fabric1/switches/FDO23040Q85/vpcPair",
            "sequence_number": 1
        }
    ]
failed:
    description: Whether any operation failed during execution
    type: bool
    returned: always
    sample: false
"""

import inspect
import logging
import re
import traceback
import sys
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.nd.plugins.module_utils.nd import NDModule
from ansible.module_utils.basic import missing_required_lib

# RestSend infrastructure imports
from ansible_collections.cisco.nd.plugins.module_utils.nd_v2 import (
    NDModule as NDModuleV2,
    NDModuleError,
)
from ansible_collections.cisco.nd.plugins.module_utils.enums import (
    HttpVerbEnum,
    OperationType,
)
from ansible_collections.cisco.nd.plugins.module_utils.results import Results

from ..module_utils.common.log import Log
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.model_playbook_vpc_pair import NdVpcPairSchema
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.vpc_pair_endpoints import (
    EpVpcPairGet,
    EpVpcPairPut,
    EpVpcPairOverviewGet,
    EpVpcPairRecommendationGet,
)
from ansible_collections.cisco.nd.plugins.module_utils.manage.vpc_pair.base_paths import VpcPairBasePath

# Alias for backward compatibility - using the nested schema's VpcPairBase as VpcPairModel
VpcPairModel = NdVpcPairSchema.VpcPairBase

try:
    from deepdiff import DeepDiff
except ImportError:
    HAS_DEEPDIFF = False
    DEEPDIFF_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_DEEPDIFF = True
    DEEPDIFF_IMPORT_ERROR = None


class UpdateInventory:
    """
    Class to update the Ansible inventory with vPC pair information.

    This class is responsible for updating the Ansible inventory with the current state
    of switches retrieved from Nexus Dashboard (ND).

    Attributes:
        nd: Nexus Dashboard instance for making API requests.
        switches: List of SwitchModel objects representing the current state of switches.
        logger: Logger instance for logging debug information.
        path: API endpoint path for retrieving switch information.
        verb: HTTP method used for the request (GET).
        sw_sn_from_ip: Dictionary mapping switch IP addresses to serial numbers.
    """

    def __init__(self, nd, logger=None):
        self.class_name = self.__class__.__name__
        self.nd = nd
        self.switches = []
        self.logger = logger or logging.getLogger(f"nd.{self.class_name}")
        self.fabric = self.nd.params.get("fabric")
        self.path = VpcPairBasePath.fabrics(self.fabric, "switches")
        self.verb = "GET"
        self.sw_sn_from_ip = {}

    def refresh(self):
        """
        Refreshes the switch state by fetching the latest data from the ND API.

        This method updates the internal switches attribute with fresh data
        retrieved from the network controller using the configured path and HTTP verb.

        Returns:
            None: Updates the self.switches attribute directly.

        Raises:
            AnsibleModule.fail_json: If API request fails or response is invalid
        """
        self.logger.debug("Fetching switch state from ND API at path: %s with verb: %s", self.path, self.verb)

        try:
            response = self.nd.request(self.path, method=self.verb)
        except Exception as error:
            error_msg = f"Failed to fetch switch inventory from {self.path}: {str(error)}"
            self.logger.error(error_msg)
            self.nd.fail_json(msg=error_msg)

        # Validate response structure
        if response is None:
            error_msg = f"Received None response from {self.path}"
            self.logger.error(error_msg)
            self.nd.fail_json(msg=error_msg)

        if not isinstance(response, dict):
            error_msg = f"Expected dict response from {self.path}, got {type(response).__name__}"
            self.logger.error(error_msg)
            self.nd.fail_json(msg=error_msg)

        self.switches = response.get("switches", [])
        if not self.switches:
            self.logger.warning("No switches found in the response from ND API.")
            return

        self.logger.debug("Switch state retrieved: %s", json.dumps(self.switches, indent=2))

        # Create switch ip to serial number mapping with error handling
        try:
            self.sw_sn_from_ip = {sw["fabricManagementIp"]: sw["serialNumber"] for sw in self.switches if "fabricManagementIp" in sw and "serialNumber" in sw}
            self.logger.info("Switch IP to Serial Number mapping: %s", self.sw_sn_from_ip)
        except (KeyError, TypeError) as error:
            self.logger.warning(f"Error creating IP to SN mapping: {error}. Continuing with empty mapping.")
            self.sw_sn_from_ip = {}

    def get_switch_serial_numbers(self):
        """
        Get a set of all switch serial numbers in the fabric.

        Returns:
            set: Set of switch serial numbers present in the fabric.
        """
        serial_numbers = set()
        for sw in self.switches:
            if "serialNumber" in sw:
                serial_numbers.add(sw["serialNumber"])
        return serial_numbers

    def switch_exists(self, switch_id):
        """
        Check if a switch exists in the fabric inventory.

        Args:
            switch_id (str): Switch serial number to check

        Returns:
            bool: True if switch exists in fabric, False otherwise
        """
        serial_numbers = self.get_switch_serial_numbers()
        return switch_id in serial_numbers


class GetHave:
    """
    Class to retrieve and process vPC pair state information from Nexus Dashboard (ND).

    This class handles the retrieval of vPC pair state information from the Nexus Dashboard
    API and processes the response into a list of VpcPairModel objects.

    Attributes:
        class_name (str): Name of the class.
        log (Logger): Logger instance for this class.
        fabric (str): Fabric name to query vPC pairs for.
        path (str): API endpoint path for vPC pair information.
        recommendation_path (str): API endpoint path for vPC pair recommendations used for virtual peer link.
        verb (str): HTTP method used for the request (GET).
        vpc_pair_state (dict): Raw vPC pair state data retrieved from ND.
        want (list): List of processed VpcPairModel objects.
        nd: Nexus Dashboard instance for making API requests.
        sw_sn_from_ip (dict): Mapping of switch IP addresses to serial numbers.

    Methods:
        refresh(): Fetches the current vPC pair state from Nexus Dashboard.
        validate_nd_state(): Processes the vPC pair state data into VpcPairModel objects.
        get_virtual_peer_link_details(): Retrieves virtual peer link details for vPC pairs.
    """

    def __init__(self, nd, inventory, logger=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")
        self.fabric = nd.params.get("fabric")
        self.vpc_pair_state = {}
        self.have = []
        self.nd = nd
        self.switches = inventory.switches
        msg = "ENTERED GetHave(): "
        self.log.debug(msg)

    def refresh(self):
        """
        Refreshes the vPC pair state by analyzing switch inventory data.

        This method processes the switches from inventory to:
        1. Identify existing vPC pairs from switches with vpcConfigured=true
        2. Track switches that are pending (not in vPC pairs)
        3. Track switch pairs that are in vPC but marked as pending

        Returns:
            None: Updates the vpc_pair_list, pending_switches, and pending_vpc_pairs attributes
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]

        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        self.pending_switches = []
        self.pending_delete_vpc_pairs = []
        self.pending_create_vpc_pairs = []
        self.pending_pairs = []
        processed_switch_ids = set()

        # Process each switch to find vPC pairs and pending switches
        for switch in self.switches:
            switch_id = switch.get("switchId")

            if switch_id in processed_switch_ids:
                self.log.warning("Switch %s already processed", switch_id)
                continue

            other_peer = self.get_recommendation_details(switch_id)
            self.log.debug("Other peer details: %s" % other_peer)

            processed_switch_ids.add(switch_id)

            vpc_configured = switch.get("vpcConfigured", False)
            vpc_data = switch.get("vpcData", {})
            status = switch.get("additionalData", {}).get("configSyncStatus")
            self.log.debug(f"Processing switch: {switch_id}, vPC Configured: {vpc_configured}, Status: {status}")

            if vpc_configured and vpc_data:
                peer_switch_id = vpc_data.get("peerSwitchId")
                # Mark both switches as processed to avoid duplicate entries
                processed_switch_ids.add(peer_switch_id)

                # Create a VpcPairModel (VpcPairBase from nested schema) to get consistent pair key
                temp_vpc_pair_data = {
                    "switchId": switch_id,
                    "peerSwitchId": peer_switch_id,
                    "useVirtualPeerLink": False,  # Default to False, will be updated later if needed
                }
                temp_vpc_pair = NdVpcPairSchema.VpcPairBase(**temp_vpc_pair_data)
                if not other_peer:
                    self.pending_delete_vpc_pairs.append(temp_vpc_pair)
                else:
                    # old 3.2 api uses useVirtualPeerlink instead of useVirtualPeerLink (case sensitive)
                    self.log.debug("useVirtualPeerLink updated: %s" % other_peer.get("useVirtualPeerlink"))
                    temp_vpc_pair.use_virtual_peer_link = other_peer.get("useVirtualPeerlink", False)
                    self.have.append(temp_vpc_pair)
            elif other_peer:

                peer_switch_id = other_peer.get("serialNumber")
                # Mark both switches as processed to avoid duplicate entries
                processed_switch_ids.add(peer_switch_id)

                temp_vpc_pair_data = {"switchId": switch_id, "peerSwitchId": peer_switch_id, "useVirtualPeerLink": other_peer.get("useVirtualPeerLink", False)}
                self.pending_create_vpc_pairs.append(NdVpcPairSchema.VpcPairBase(**temp_vpc_pair_data))

            self.log.debug("have: %s" % self.have)
            self.log.debug("pending_delete: %s" % self.pending_delete_vpc_pairs)
            self.log.debug("pending_create: %s" % self.pending_create_vpc_pairs)

    def get_recommendation_details(self, switchId):
        """
        Helper function to get recommendation details for a switch.

        Args:
            switchId (str): The switch ID for which to retrieve recommendation details.

        Returns:
            dict: A dictionary with the peer switch ID and useVirtualPeerLink status, or None if not found.

        Raises:
            Does not raise exceptions - returns None on errors and logs warnings
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        try:
            # Use endpoint model for VPC pair recommendations
            endpoint = EpVpcPairRecommendationGet()
            endpoint.fabric_name = self.fabric
            endpoint.switch_id = switchId
            path = endpoint.path
            verb = endpoint.verb

            self.log.debug(f"Fetching VPC pair recommendation from: {path}")
            vpc_pair_recommendation = self.nd.request(path, method=verb.value)

            # Validate response
            if vpc_pair_recommendation is None:
                self.log.warning(f"Received None response from VPC pair recommendation for switch {switchId}")
                return None

            # Handle response - look for current peer in the recommendations list
            if isinstance(vpc_pair_recommendation, list):
                for sw in vpc_pair_recommendation:
                    if isinstance(sw, dict) and (sw.get("currentPeer") or sw.get("isCurrentPeer")):
                        return sw
            else:
                self.log.warning(
                    f"Expected list response from VPC pair recommendation for switch {switchId}, " f"got {type(vpc_pair_recommendation).__name__}"
                )

            return None

        except Exception as error:
            self.log.warning(f"Error fetching VPC pair recommendation for switch {switchId}: {str(error)}")
            return None


class Common:
    """
    Common utility class that provides shared functionality for all state operations in the Cisco ND vPC pair module.

    This class handles the core logic for processing vPC pair configurations across different operational states
    (merged, replaced, deleted, overridden, query) in Ansible tasks. It manages state comparison, parameter
    validation, and payload construction for ND API operations using Pydantic models and utility functions.

    The class leverages utility functions (merge_models, model_payload_with_defaults) to intelligently handle
    vPC pair configuration merging and default value application based on the operation state.

    Attributes:
        modiresult (dict): Dictionary to store operation results including changed state, diffs, API responses and warnings.
        task_params (dict): Parameters provided from the Ansible task.
        state (str): The desired state operation (merged, replaced, deleted, overridden, or query).
        requests (dict): Container for API request requests.
        have (list): List of VpcPairModel objects representing the current state of vPC pairs.
        query (list): List for storing query results.
        validated (list): List of validated configuration items.
        want (list): List of VpcPairModel objects representing the desired state of vPC pairs.
        inventory (obj): Inventory object that contains the state of the switches in the fabric

    Methods:
        validate_task_params(): Validates the task parameters and builds the desired state using utility functions.
        get_pair_from_switches(vpc_pair_list, switch_id_1, switch_id_2): Checks if a vPC pair with the given pairs exists in the specified list.
    """

    def __init__(self, task_params, nd_instance, inventory, logger=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")

        self.result = dict(changed=False, diff={}, response=[], warnings=[])
        self.task_params = task_params
        self.state = task_params["state"]
        self.fabric = task_params["fabric"]
        self.deploy = task_params.get("deploy", False)
        self.dry_run = task_params.get("dry_run", False)
        self.requests = {}
        self.nd = nd_instance
        self.inventory = inventory
        self.have = []
        self.query = []
        self.validated = []
        self.want = []
        self.pending_delete_vpc_pairs = []
        self.pending_create_vpc_pairs = []
        msg = "ENTERED Common(): "
        msg += f"state: {self.state}, dry_run: {self.dry_run}, "
        self.log.debug(msg)
        self.validate_task_params()

    def validate_task_params(self):
        """
        Validates and processes task parameters to create vPC pair model objects.

        This method iterates through each vPC pair configuration in the task parameters
        and converts them into VpcPairModel instances based on the provided configurations.
        The resulting models are stored in the want list for further processing.

        Returns:
            None: Updates self.want list with processed VpcPairModel objects
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        if not self.task_params.get("config"):
            return

        # check if we need to only work with switches in the fabric
        unique_switches_want = set()
        for vpc_pair in self.task_params.get("config", []):
            try:
                # Convert playbook input to API format for validation
                # Handle IP to serial number conversion
                vpc_pair_data = vpc_pair.copy()

                # Convert field names from playbook format to API format if needed
                if "peer1_switch_id" in vpc_pair_data:
                    vpc_pair_data["switchId"] = vpc_pair_data.pop("peer1_switch_id")
                if "peer2_switch_id" in vpc_pair_data:
                    vpc_pair_data["peerSwitchId"] = vpc_pair_data.pop("peer2_switch_id")
                if "use_virtual_peer_link" in vpc_pair_data:
                    vpc_pair_data["useVirtualPeerLink"] = vpc_pair_data.pop("use_virtual_peer_link")

                # Convert IP addresses to serial numbers if mapping is provided
                if self.inventory.sw_sn_from_ip:
                    if "switchId" in vpc_pair_data:
                        original_peer1 = vpc_pair_data["switchId"]
                        vpc_pair_data["switchId"] = self.inventory.sw_sn_from_ip.get(original_peer1, original_peer1)

                    if "peerSwitchId" in vpc_pair_data:
                        original_peer2 = vpc_pair_data["peerSwitchId"]
                        vpc_pair_data["peerSwitchId"] = self.inventory.sw_sn_from_ip.get(original_peer2, original_peer2)

                # Use the nested schema for validation
                validated_config = NdVpcPairSchema.VpcPairBase(**vpc_pair_data)

            except ValueError as error:
                self.nd.fail_json(msg=f"Invalid vPC pair configuration: {str(error)}")

            # Check uniqueness after Pydantic validation
            if validated_config.peer_switch_id and validated_config.peer_switch_id in unique_switches_want:
                self.nd.fail_json(msg=f"Switch IDs must be unique across vPC pairs: {validated_config.peer_switch_id}")
            if validated_config.peer_switch_id:
                unique_switches_want.add(validated_config.peer_switch_id)

            if validated_config.switch_id in unique_switches_want:
                self.nd.fail_json(msg=f"Switch IDs must be unique across vPC pairs: {validated_config.switch_id}")
            unique_switches_want.add(validated_config.switch_id)

            self.want.append(validated_config)

        self.log.debug("Processed vPC pair configurations: %s", self.want)

    def get_pair_from_switches(self, vpc_pair_list, switch_id_1, switch_id_2=None):
        """
        Find a vPC pair by pair switch IDs in the current state.

        This method searches through the current state (`self.have`) for a vPC pair
        with the specified pair switch IDs and returns it if found.

        Args:
            switch_id_1 (str): The peer1 switch ID of the vPC pair to find.
            switch_id_2 (str, optional): The peer2 switch ID of the vPC pair to find.
                                        If None, searches for any pair containing switch_id_1.

        Returns:
            object: The vPC pair object if found, None otherwise.

        Raises:
            AnsibleModule.fail_json: If switch_id_2 is None and multiple vPC pairs
                                     contain switch_id_1 (ambiguous match).
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        msg = f"ENTERED: {self.class_name}.{method_name} with switch_id_1: {switch_id_1}, switch_id_2: {switch_id_2}"
        self.log.debug(msg)

        if not switch_id_2:
            # When only one switch ID is provided, collect all matches
            matches = []
            for vpc_pair in vpc_pair_list:
                vpc_pair_dict = vpc_pair.model_dump()
                # Handle both old field names and new field names from nested schema
                peers = [
                    vpc_pair_dict.get("switchId") or vpc_pair_dict.get("switch_id"),
                    vpc_pair_dict.get("peerSwitchId") or vpc_pair_dict.get("peer_switch_id"),
                ]
                if switch_id_1 in peers:
                    matches.append(vpc_pair)

            # Handle ambiguous matches
            if len(matches) == 0:
                return None
            elif len(matches) == 1:
                return matches[0]
            else:
                # Multiple matches found - this is ambiguous
                match_keys = [pair.get_switch_pair_key() for pair in matches]
                self.log.error(f"Ambiguous vPC pair lookup: switch {switch_id_1} found in multiple pairs: {match_keys}")
                self.nd.fail_json(
                    msg=f"Ambiguous vPC pair lookup: switch {switch_id_1} appears in {len(matches)} vPC pairs: {match_keys}. "
                    f"Please specify both switch IDs to uniquely identify the vPC pair, or fix the configuration to ensure "
                    f"each switch is only part of one vPC pair."
                )
        else:
            for vpc_pair in vpc_pair_list:
                vpc_pair_dict = vpc_pair.model_dump()
                # Handle both old field names and new field names from nested schema
                peers = [
                    vpc_pair_dict.get("switchId") or vpc_pair_dict.get("switch_id"),
                    vpc_pair_dict.get("peerSwitchId") or vpc_pair_dict.get("peer_switch_id"),
                ]
                if switch_id_1 in peers and switch_id_2 in peers:
                    return vpc_pair
        return None

    def validate_no_switch_conflicts(self, exclude_pairs=None):
        """
        Validate that neither switch in vpc_pair want is present in a vpc_pair with another switch in have.

        This ensures that switches are not being added to conflicting vPC pairs.
        A switch can only be part of one vPC pair at a time.

        Args:
            exclude_pairs (list, optional): List of VPC pairs to exclude from conflict checking.
                                           Useful in overridden state where pairs are being deleted
                                           and their switches can be reused in new pairs.

        Raises:
            ValueError: If any switches in want are already part of different vPC pairs in have.
                       Contains all conflicts found, not just the first one.
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]

        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Create set of switch pair keys to exclude from conflict checking
        excluded_keys = set()
        if exclude_pairs:
            excluded_keys = {pair.get_switch_pair_key() for pair in exclude_pairs}
            self.log.debug(f"Excluding {len(excluded_keys)} pairs from conflict checking: {excluded_keys}")

        conflicts = []  # Collect all conflicts before raising error

        for want_vpc_pair in self.want:
            want_switches = {want_vpc_pair.switch_id, want_vpc_pair.peer_switch_id}

            for have_vpc_pair in self.have:
                have_switches = {have_vpc_pair.switch_id, have_vpc_pair.peer_switch_id}

                # Skip pairs that are being excluded (e.g., marked for deletion in overridden state)
                have_pair_key = have_vpc_pair.get_switch_pair_key()
                if have_pair_key in excluded_keys:
                    self.log.debug(f"Skipping conflict check for excluded pair: {have_pair_key}")
                    continue

                # Check if the wanted vPC pair is exactly the same as an existing one
                if want_switches == have_switches:
                    # Same vPC pair exists, this is fine for all operations
                    self.log.debug("vPC pair %s already exists in have state", want_vpc_pair.get_switch_pair_key())
                    break

                # Check for switch conflicts - any switch overlap with different pairs
                switch_overlap = want_switches & have_switches
                if switch_overlap:
                    conflicting_switches = ", ".join(switch_overlap)
                    want_key = want_vpc_pair.get_switch_pair_key()
                    have_key = have_vpc_pair.get_switch_pair_key()

                    conflict_msg = f"Switch(es) {conflicting_switches} in wanted vPC pair {want_key} " f"are already part of existing vPC pair {have_key}"
                    conflicts.append(conflict_msg)
                    self.log.error("Switch conflict detected: %s", conflict_msg)

        # Raise a single error with all conflicts if any were found
        if conflicts:
            error_msg = (
                f"Switch conflicts detected in vPC pair configuration. "
                f"A switch can only be part of one vPC pair at a time. "
                f"Conflicts found:\n" + "\n".join(f"- {conflict}" for conflict in conflicts)
            )
            self.log.error(error_msg)
            self.nd.fail_json(msg=error_msg)

        self.log.debug("No switch conflicts found in vpc pairs validation")

    def validate_switches_exist(self):
        """
        Validate that all switches specified in want list exist in the fabric inventory.

        This method checks that each switch ID referenced in the vPC pair configurations
        actually exists in the fabric. This prevents cryptic API errors later by validating
        switch existence upfront.

        Raises:
            AnsibleModule.fail_json: If any switches in want do not exist in the fabric.
                                     Lists all missing switches in the error message.
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]

        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Get all valid switch serial numbers from inventory
        valid_switches = self.inventory.get_switch_serial_numbers()

        if not valid_switches:
            self.log.warning("No switches found in fabric inventory. Skipping switch existence validation.")
            return

        self.log.debug(f"Valid switches in fabric {self.fabric}: {valid_switches}")

        # Collect all missing switches
        missing_switches = []
        affected_pairs = []

        for want_vpc_pair in self.want:
            pair_key = want_vpc_pair.get_switch_pair_key()

            # Check switch_id (peer1)
            if want_vpc_pair.switch_id not in valid_switches:
                missing_switches.append(want_vpc_pair.switch_id)
                affected_pairs.append(f"{pair_key} (switchId: {want_vpc_pair.switch_id})")

            # Check peer_switch_id (peer2)
            if want_vpc_pair.peer_switch_id not in valid_switches:
                if want_vpc_pair.peer_switch_id not in missing_switches:
                    missing_switches.append(want_vpc_pair.peer_switch_id)
                affected_pairs.append(f"{pair_key} (peerSwitchId: {want_vpc_pair.peer_switch_id})")

        # Raise error if any switches are missing
        if missing_switches:
            error_msg = (
                f"Switch validation failed: The following switch(es) do not exist in fabric '{self.fabric}':\n"
                f"  Missing switches: {', '.join(missing_switches)}\n"
                f"  Affected vPC pairs: {', '.join(affected_pairs)}\n\n"
                f"Please ensure:\n"
                f"  1. Switch serial numbers are correct (not IP addresses)\n"
                f"  2. Switches are discovered and present in the fabric\n"
                f"  3. You have the correct fabric name specified\n\n"
                f"Valid switches in fabric: {', '.join(sorted(valid_switches))}"
            )
            self.log.error(error_msg)
            self.nd.fail_json(msg=error_msg)

        self.log.debug(f"All switches in want list exist in fabric {self.fabric}")

    def save_fabric_config(self):
        """
        Save the fabric configuration before deploying changes.

        This method sends a POST request to the fabric config save endpoint to save
        the current configuration state. This should be called before deploying
        configuration changes.

        Returns:
            dict: Response from the config save API call

        Raises:
            Exception: If the config save operation fails
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Don't save if state is query
        if self.state == "query":
            self.log.debug("Skipping config save for query state")
            return None

        # Don't save if deploy parameter is False (no need to save if we're not deploying)
        if not self.deploy:
            self.log.debug("Deploy parameter is False, skipping config save")
            return None

        config_save_path = VpcPairBasePath.fabrics(self.fabric, "actions", "configSave")
        self.log.info(f"Saving fabric configuration via: {config_save_path}")

        try:
            response = self.nd.request(config_save_path, method="POST", data={})

            # Validate response
            if response is None:
                self.log.warning("Received None response from config save - treating as success")
                response = {"status": "success", "message": "Config save completed (no response body)"}

            self.log.debug("Config save response: %s", response)

            # Store config save response with additional context
            config_save_response_entry = {"operation": "CONFIG_SAVE", "path": config_save_path, "response": response}
            self.result["response"].append(config_save_response_entry)

            return response

        except Exception as error:
            error_msg = f"Failed to save fabric configuration at {config_save_path}: {str(error)}"
            self.log.error(error_msg)
            self.nd.fail_json(msg=error_msg)

    def needs_deployment(self):
        """
        Determine if deployment is needed based on current state and changes.

        Deployment is needed if any of the following conditions are met:
        1. There are items in the diff (actual configuration changes were made)
        2. There are pending create vPC pairs (switches ready to be paired)
        3. There are pending delete vPC pairs (switches ready to be unpaired)
        4. There are any requests in the requests dictionary (operations to be performed)

        Returns:
            bool: True if deployment is needed, False otherwise
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Check if there are any changes in the diff
        has_diff_changes = any(self.result.get("diff", {}).get(operation, []) for operation in ["POST", "PUT", "DELETE"])

        # Check if there are pending operations
        has_pending_create = bool(self.pending_create_vpc_pairs)
        has_pending_delete = bool(self.pending_delete_vpc_pairs)

        # Check if there are any API requests to be made
        has_requests = bool(self.requests)

        self.log.debug(f"Deployment needs assessment:")
        self.log.debug(f"  - Has diff changes: {has_diff_changes}")
        self.log.debug(f"  - Has pending create pairs: {has_pending_create} (count: {len(self.pending_create_vpc_pairs)})")
        self.log.debug(f"  - Has pending delete pairs: {has_pending_delete} (count: {len(self.pending_delete_vpc_pairs)})")
        self.log.debug(f"  - Has API requests: {has_requests} (count: {len(self.requests)})")

        deployment_needed = has_diff_changes or has_pending_create or has_pending_delete or has_requests

        self.log.info(f"Deployment needed: {deployment_needed}")
        return deployment_needed

    def deploy_fabric(self):
        """
        Deploy the fabric configuration changes after applying vPC pair operations.

        This method first checks if deployment is actually needed based on:
        - Presence of configuration changes (diff)
        - Pending create/delete vPC pairs
        - Any API requests that were made

        If deployment is needed, it saves the current configuration and then sends a POST request
        to the fabric deploy endpoint. It should only be called after all other vPC pair operations
        have been completed successfully.

        Returns:
            dict: Response from the deploy API call, or None if deployment is not needed

        Raises:
            Exception: If the config save or deploy operation fails
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Don't deploy if state is query
        if self.state == "query":
            self.log.debug("Skipping deploy for query state")
            return None

        # Don't deploy if deploy parameter is False
        if not self.deploy:
            self.log.debug("Deploy parameter is False, skipping deployment")
            return None

        # Check if deployment is actually needed
        if not self.needs_deployment():
            self.log.info("No configuration changes or pending operations detected, skipping deployment")
            return None

        # Save configuration before deploying
        self.log.info("Configuration changes detected, saving fabric configuration before deployment")
        self.save_fabric_config()

        deploy_path = VpcPairBasePath.fabrics(self.fabric, "actions", "deploy") + "?forceShowRun=true"
        self.log.info(f"Deploying fabric configuration changes via: {deploy_path}")

        try:
            response = self.nd.request(deploy_path, method="POST", data={})

            # Validate response
            if response is None:
                self.log.warning("Received None response from deploy - treating as success")
                response = {"status": "success", "message": "Deploy completed (no response body)"}

            self.log.debug("Deploy response: %s", response)

            # Store deploy response with additional context
            deploy_response_entry = {"operation": "DEPLOY", "path": deploy_path, "response": response}
            self.result["response"].append(deploy_response_entry)

            # Mark as changed if deploy was triggered
            self.result["changed"] = True

            return response

        except Exception as error:
            error_msg = f"Failed to deploy fabric configuration at {deploy_path}: {str(error)}"
            self.log.error(error_msg)
            self.nd.fail_json(msg=error_msg)

    def show_dry_run_deployment_info(self):
        """
        Show what deployment actions would be taken in dry run mode.

        This method evaluates whether deployment would occur and provides
        detailed information about the deployment decision factors without
        actually performing the deployment.
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        deployment_needed = self.needs_deployment()

        deployment_info = {
            "would_deploy": deployment_needed,
            "deployment_decision_factors": {
                "diff_has_changes": bool(self.result.get("diff", {}).get("after") != self.result.get("diff", {}).get("before")),
                "pending_operations": bool(self.pending_create_vpc_pairs or self.pending_delete_vpc_pairs),
                "api_requests_generated": bool(self.result.get("response", [])),
            },
        }

        if deployment_needed:
            deployment_info["planned_actions"] = [
                f"POST {VpcPairBasePath.fabrics(self.fabric, 'actions', 'configSave')}",
                f"POST {VpcPairBasePath.fabrics(self.fabric, 'actions', 'deploy')}?forceShowRun=true",
            ]
            self.log.info("DRY RUN: Would deploy fabric configuration changes")
        else:
            deployment_info["reason_skipped"] = "No changes detected (diff empty, no pending operations, no API requests)"
            self.log.info("DRY RUN: Would skip deployment - no changes detected")

        # Store deployment info in result
        self.result["deployment"] = deployment_info


class Merged:
    """
    A class that implements the 'merged' state strategy for Cisco ND vPC pair configurations.

    This class compares the desired state ('want') with the current state ('have') of
    vPC pairs and generates the necessary API requests to bring the current state in line
    with the desired state. When using the 'merged' state, existing configurations are
    preserved and only the differences or additions are applied.

    The class calculates differences between configurations using DeepDiff and constructs
    appropriate REST API calls (POST for new vPC pairs, PUT for existing ones) with requests
    that reflect only the changes needed.

    Attributes:
        common (Common): Common utility instance for shared functionality

    Methods:
        build_request(): Analyzes desired state against current state and builds API requests
        update_payload_merged(have, want): Generates a merged request payload from current and desired states
        _parse_path(path): Parses DeepDiff paths into component parts
        _process_values_changed(diff, updated_payload): Updates changed values in the payload
        _process_dict_items_added(diff, updated_payload, want_dict): Adds new items to the payload
    """

    def __init__(self, logger=None, common_util=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")
        self.common = common_util

        msg = "ENTERED Merged(): "
        msg += f"state: {self.common.state}, "
        self.log.debug(msg)

        self.payload_request = {}
        self.build_request()
        self.log.debug("Payload request built: %s", self.payload_request)

    def build_request(self):
        """
        Build API request payloads using 4.2 unified PUT endpoint.

        All operations (create and update) use PUT with vpcAction="pair".
        The API automatically determines if it's a create or update.

        Returns:
            None: Updates self.common.requests with request configurations

        Raises:
            ValueError: If a switch in want is already part of a different vPC pair in have
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Validate switch conflicts first
        self.common.validate_no_switch_conflicts()

        # Validate that all switches exist in fabric
        self.common.validate_switches_exist()

        for want_vpc_pair in self.common.want:
            vpc_pair_key = want_vpc_pair.get_switch_pair_key()

            # Find corresponding vPC pair in have (if it exists)
            have_vpc_pair = self.common.get_pair_from_switches(self.common.have, want_vpc_pair.switch_id, want_vpc_pair.peer_switch_id)

            # Determine if changes are needed
            if have_vpc_pair:
                # Existing pair - check if update is needed
                if self._is_update_needed(want_vpc_pair, have_vpc_pair):
                    operation_type = "update"
                    self.log.info(f"vPC pair {vpc_pair_key} exists but needs update")
                else:
                    # No changes needed - skip
                    self.log.debug(f"vPC pair {vpc_pair_key} is already in desired state - skipping")
                    continue
            else:
                # New pair
                operation_type = "create"
                self.log.info(f"vPC pair {vpc_pair_key} does not exist - will create")

            # NEW: Build 4.2 API payload with vpcAction discriminator
            payload = self._build_vpc_pair_payload(want_vpc_pair)

            # Use endpoint model for path and verb
            endpoint = EpVpcPairPut()
            endpoint.fabric_name = self.common.fabric
            endpoint.switch_id = want_vpc_pair.switch_id
            path = endpoint.path
            verb = endpoint.verb

            self.log.debug(f"Operation: {operation_type}, Path: {path}, Verb: {verb.value}, Payload: {json.dumps(payload, indent=2)}")

            # Add to requests dict
            self.common.requests[vpc_pair_key] = {
                "verb": verb.value,  # Use verb from endpoint
                "path": path,
                "payload": payload,
                "operation": operation_type,  # For logging/debugging
            }

        self.log.info(f"Built {len(self.common.requests)} vPC pair request(s)")

    def _build_vpc_pair_payload(self, vpc_pair_model):
        """
        Build the 4.2 API payload for pairing a VPC.

        Constructs payload according to OpenAPI spec with vpcAction
        discriminator and optional template details.

        Args:
            vpc_pair_model: VpcPairModel instance with configuration

        Returns:
            dict: Complete payload for PUT request in 4.2 format
        """
        # NEW: Base payload with vpcAction discriminator and updated field names
        # Use the VpcPairingRequest schema to build the payload
        pairing_data = {
            "vpcAction": "pair",
            "switchId": vpc_pair_model.switch_id,
            "peerSwitchId": vpc_pair_model.peer_switch_id,
            "useVirtualPeerLink": vpc_pair_model.use_virtual_peer_link,
        }

        # Add vpcPairDetails if present in the model
        if vpc_pair_model.vpc_pair_details:
            pairing_data["vpcPairDetails"] = vpc_pair_model.vpc_pair_details

        # Validate using VpcPairingRequest schema and convert to dict
        try:
            pairing_request = NdVpcPairSchema.VpcPairingRequest(**pairing_data)
            payload = pairing_request.model_dump(by_alias=True, exclude_none=True, mode="json")
        except Exception as e:
            self.log.warning(f"Failed to validate with VpcPairingRequest schema: {e}, using raw payload")
            payload = pairing_data

        # NEW: Add template configuration if provided
        template_config = self._get_template_config(vpc_pair_model)
        if template_config:
            payload["vpcPairDetails"] = template_config
            self.log.debug(f"Added vpcPairDetails to payload: {json.dumps(template_config, indent=2)}")

        return payload

    def _get_template_config(self, vpc_pair_model):
        """
        Extract template configuration from VPC pair model if present.

        Supports both default and custom template types:
        - default: Standard parameters (domainId, keepAliveVrf, etc.)
        - custom: User-defined template with custom fields

        Args:
            vpc_pair_model: VpcPairModel instance

        Returns:
            dict: Template configuration or None if not provided
        """
        # Check if model has template configuration
        if not hasattr(vpc_pair_model, "template_config"):
            return None

        template_config = vpc_pair_model.template_config
        if not template_config:
            return None

        template_type = getattr(vpc_pair_model, "template_type", "default")

        if template_type == "custom":
            # Custom template format
            template_name = getattr(vpc_pair_model, "template_name", None)
            if not template_name:
                self.log.warning("Custom template type specified but template_name is missing")
                return None
            return {"type": "custom", "templateName": template_name, "templateConfig": template_config}
        else:
            # Default template format - merge type with config
            result = {"type": "default"}
            result.update(template_config)
            return result

    def _is_update_needed(self, want, have):
        """
        Determine if an update is needed by comparing want and have.

        Uses DeepDiff for intelligent comparison that handles:
        - Field additions
        - Value changes
        - Nested structure changes

        Args:
            want: Desired VPC pair configuration
            have: Current VPC pair configuration

        Returns:
            bool: True if update is needed, False if already in desired state
        """
        try:
            # Use DeepDiff to calculate differences
            diff = DeepDiff(have, want, ignore_order=True, view="tree")

            if diff:
                self.log.debug(f"Configuration differences detected: {diff}")
                return True
            else:
                self.log.debug("No configuration differences detected")
                return False

        except Exception as e:
            # Fallback to simple comparison if DeepDiff fails
            self.log.warning(f"DeepDiff comparison failed: {e}, using simple comparison")
            return want != have


class Replaced:
    """
    A class for handling 'replaced' state operations on Cisco ND vPC pair resources.

    The Replaced class implements the same logic as Merged - it compares the desired state
    with the current state and generates the necessary API requests to bring the current
    state in line with the desired state, preserving existing configurations and only
    applying differences or additions.

    This differs from a traditional 'replaced' operation which would completely replace
    configurations. In this implementation, 'replaced' behaves the same as 'merged'.

    Attributes:
        common (Common): Common utility instance for shared functionality

    Methods:
        build_request(): Analyzes desired state against current state and builds API requests
        _validate_no_switch_conflicts(): Validates that switches aren't in conflicting vPC pairs
    """

    def __init__(self, logger=None, common_util=None, exclude_pairs=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")
        self.common = common_util
        self.exclude_pairs = exclude_pairs or []

        msg = "ENTERED Replaced(): "
        msg += f"state: {self.common.state}, "
        if self.exclude_pairs:
            msg += f"exclude_pairs: {len(self.exclude_pairs)} pairs, "
        self.log.debug(msg)

        self.payload_request = {}
        self.build_request()
        self.log.debug("Payload request built: %s", self.payload_request)

    def build_request(self):
        """
        Build API request payloads using 4.2 unified PUT endpoint.

        All operations (create and update) use PUT with vpcAction="pair".
        The API automatically determines if it's a create or update.

        This implementation is identical to the Merged class behavior.

        Returns:
            None: Updates self.common.requests with request configurations

        Raises:
            ValueError: If a switch in want is already part of a different vPC pair in have
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Validate switch conflicts first
        # Pass exclude_pairs to allow switch reuse in overridden state where pairs are being deleted
        self.common.validate_no_switch_conflicts(exclude_pairs=self.exclude_pairs)

        # Validate that all switches exist in fabric
        self.common.validate_switches_exist()

        for want_vpc_pair in self.common.want:
            vpc_pair_key = want_vpc_pair.get_switch_pair_key()

            # Find corresponding vPC pair in have (if it exists)
            have_vpc_pair = self.common.get_pair_from_switches(self.common.have, want_vpc_pair.switch_id, want_vpc_pair.peer_switch_id)

            # Determine if changes are needed
            if have_vpc_pair:
                # Existing pair - check if update is needed
                if self._is_update_needed(want_vpc_pair, have_vpc_pair):
                    operation_type = "update"
                    self.log.info(f"vPC pair {vpc_pair_key} exists but needs update")
                else:
                    # No changes needed - skip
                    self.log.debug(f"vPC pair {vpc_pair_key} is already in desired state - skipping")
                    continue
            else:
                # New pair
                operation_type = "create"
                self.log.info(f"vPC pair {vpc_pair_key} does not exist - will create")

            # NEW: Build 4.2 API payload with vpcAction discriminator
            payload = self._build_vpc_pair_payload(want_vpc_pair)

            # Use endpoint model for path and verb
            endpoint = EpVpcPairPut()
            endpoint.fabric_name = self.common.fabric
            endpoint.switch_id = want_vpc_pair.switch_id
            path = endpoint.path
            verb = endpoint.verb

            self.log.debug(f"Operation: {operation_type}, Path: {path}, Verb: {verb.value}, Payload: {json.dumps(payload, indent=2)}")

            # Add to requests dict
            self.common.requests[vpc_pair_key] = {
                "verb": verb.value,  # Use verb from endpoint
                "path": path,
                "payload": payload,
                "operation": operation_type,  # For logging/debugging
            }

        self.log.info(f"Built {len(self.common.requests)} vPC pair request(s)")

    def _build_vpc_pair_payload(self, vpc_pair_model):
        """
        Build the 4.2 API payload for pairing a VPC.

        Constructs payload according to OpenAPI spec with vpcAction
        discriminator and optional template details.

        Args:
            vpc_pair_model: VpcPairModel instance with configuration

        Returns:
            dict: Complete payload for PUT request in 4.2 format
        """
        # NEW: Base payload with vpcAction discriminator and updated field names
        # Use the VpcPairingRequest schema to build the payload
        pairing_data = {
            "vpcAction": "pair",
            "switchId": vpc_pair_model.switch_id,
            "peerSwitchId": vpc_pair_model.peer_switch_id,
            "useVirtualPeerLink": vpc_pair_model.use_virtual_peer_link,
        }

        # Add vpcPairDetails if present in the model
        if vpc_pair_model.vpc_pair_details:
            pairing_data["vpcPairDetails"] = vpc_pair_model.vpc_pair_details

        # Validate using VpcPairingRequest schema and convert to dict
        try:
            pairing_request = NdVpcPairSchema.VpcPairingRequest(**pairing_data)
            payload = pairing_request.model_dump(by_alias=True, exclude_none=True, mode="json")
        except Exception as e:
            self.log.warning(f"Failed to validate with VpcPairingRequest schema: {e}, using raw payload")
            payload = pairing_data

        # NEW: Add template configuration if provided
        template_config = self._get_template_config(vpc_pair_model)
        if template_config:
            payload["vpcPairDetails"] = template_config
            self.log.debug(f"Added vpcPairDetails to payload: {json.dumps(template_config, indent=2)}")

        return payload

    def _get_template_config(self, vpc_pair_model):
        """
        Extract template configuration from VPC pair model if present.

        Supports both default and custom template types:
        - default: Standard parameters (domainId, keepAliveVrf, etc.)
        - custom: User-defined template with custom fields

        Args:
            vpc_pair_model: VpcPairModel instance

        Returns:
            dict: Template configuration or None if not provided
        """
        # Check if model has template configuration
        if not hasattr(vpc_pair_model, "template_config"):
            return None

        template_config = vpc_pair_model.template_config
        if not template_config:
            return None

        template_type = getattr(vpc_pair_model, "template_type", "default")

        if template_type == "custom":
            # Custom template format
            template_name = getattr(vpc_pair_model, "template_name", None)
            if not template_name:
                self.log.warning("Custom template type specified but template_name is missing")
                return None
            return {"type": "custom", "templateName": template_name, "templateConfig": template_config}
        else:
            # Default template format - merge type with config
            result = {"type": "default"}
            result.update(template_config)
            return result

    def _is_update_needed(self, want, have):
        """
        Determine if an update is needed by comparing want and have.

        Uses DeepDiff for intelligent comparison that handles:
        - Field additions
        - Value changes
        - Nested structure changes

        Args:
            want: Desired VPC pair configuration
            have: Current VPC pair configuration

        Returns:
            bool: True if update is needed, False if already in desired state
        """
        try:
            # Use DeepDiff to calculate differences
            diff = DeepDiff(have, want, ignore_order=True, view="tree")

            if diff:
                self.log.debug(f"Configuration differences detected: {diff}")
                return True
            else:
                self.log.debug("No configuration differences detected")
                return False

        except Exception as e:
            # Fallback to simple comparison if DeepDiff fails
            self.log.warning(f"DeepDiff comparison failed: {e}, using simple comparison")
            return want != have


class Deleted:
    """
    Handle deletion of vPC pair configurations.

    This class manages the deletion of vPC pairs by comparing the desired state (want)
    with the current state (have) and preparing DELETE operations for vPC pairs that
    exist in both lists.

    Args:
        task_params: The task_params configuration containing the desired state
        have_state: The current state of vPC pairs in the system

    Attributes:
        class_name (str): Name of the current class for logging purposes
        log (logging.Logger): Logger instance for this class
        common (Common): Common utilities and state management
        verb (str): HTTP verb for the operation ("DELETE")
        path (str): API endpoint template for vPC pair deletion
        delete_vpc_pair_keys (list): List of vPC pair keys to be deleted

    The class identifies vPC pairs that exist in both the desired configuration
    and current system state, then prepares the necessary API calls to delete
    those vPC pairs by formatting the deletion path for each vPC pair and storing
    the operation details in the common requests dictionary.
    """

    def __init__(self, logger=None, common_util=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")

        self.common = common_util

        # Create a list of vPC pair keys to be deleted that are in both self.common.want and self.have

        # self.delete_vpc_pair_keys = []
        # for want_vpc_pair in self.common.want:
        #     have_vpc_pair = self.common.vpc_pair_in_have(want_vpc_pair.peer1_switch_id, want_vpc_pair.peer2_switch_id)
        #     if have_vpc_pair:
        #         vpc_pair_key = f"{want_vpc_pair.peer1_switch_id}-{want_vpc_pair.peer2_switch_id}"
        #         self.delete_vpc_pair_keys.append((vpc_pair_key, want_vpc_pair.peer1_switch_id, want_vpc_pair.peer2_switch_id))

        # for vpc_pair_key, peer1_switch_id, peer2_switch_id in self.delete_vpc_pair_keys:
        #     # Create a path for each vPC pair to be deleted
        #     self.common.requests[vpc_pair_key] = {
        #         "verb": self.verb,
        #         "path": self.path.format(fabric=self.common.nd.params.get('fabric'), peer1_switch_id=peer1_switch_id, peer2_switch_id=peer2_switch_id),
        #         "payload": "",
        #     }

        msg = "ENTERED Deleted(): "
        msg += f"state: {self.common.state}, "
        self.log.debug(msg)

        # Validate that all switches exist in fabric before attempting deletion
        self.common.validate_switches_exist()

        self.collect_deletion_requests()

    def _process_vpc_pair_deletions(self, vpc_pairs_to_delete, pending_vpc_pairs_to_delete):
        """
        Helper method to process vPC pair deletions with validation checks.

        Args:
            vpc_pairs_to_delete (list): List of vPC pairs to delete
        """
        # Remove pending delete pairs (they are already being deleted)
        pending_delete_keys = {pair.get_switch_pair_key() for pair in self.common.pending_delete_vpc_pairs}
        self.log.debug("Pending create vpc pairs to be deleted: %s (inconsistent, not handled right now)", pending_vpc_pairs_to_delete)
        for vpc_pair in vpc_pairs_to_delete:
            vpc_pair_key = vpc_pair.get_switch_pair_key()
            if vpc_pair_key in pending_delete_keys:
                self.log.debug(f"Skipping vPC pair {vpc_pair_key} as it is already in pending delete state.")
                continue

            self.log.debug(f"Preparing deletion for vPC pair: {vpc_pair_key}")

            # Use endpoint model for overview check
            try:
                overview_endpoint = EpVpcPairOverviewGet()
                overview_endpoint.fabric_name = self.common.fabric
                overview_endpoint.switch_id = vpc_pair.switch_id
                overview_endpoint.component_type = "full"
                overview_path = overview_endpoint.path

                response = self.common.nd.request(
                    overview_path,
                    method=overview_endpoint.verb.value,
                )

                # Validate response
                if response is None:
                    self.common.nd.fail_json(msg=f"Received None response when checking vPC pair {vpc_pair_key} overview at {overview_path}")

                if not isinstance(response, dict):
                    self.common.nd.fail_json(
                        msg=f"Expected dict response from vPC pair overview for {vpc_pair_key}, got {type(response).__name__}",
                        response=response,
                    )

                self.log.debug("vPC pair overview request: %s", overview_path)
                self.log.debug("vPC pair overview response: %s", json.dumps(response, indent=2))

            except Exception as error:
                error_msg = f"Failed to fetch vPC pair overview for {vpc_pair_key} at {overview_path}: {str(error)}"
                self.log.error(error_msg)
                self.common.nd.fail_json(msg=error_msg)

            # Validate overlay data exists
            if not response.get("overlay"):
                self.common.nd.fail_json(
                    msg=f"vPC pair {vpc_pair_key} might not exist or overlay data unavailable",
                    response=response,
                )

            # Check network count with error handling
            try:
                network_count = response["overlay"].get("networkCount", {})
                if not isinstance(network_count, dict):
                    self.log.warning(f"networkCount is not a dict for {vpc_pair_key}, skipping network validation")
                else:
                    self.log.debug(f"Network count for {vpc_pair_key}: {network_count}")
                    for status, count in network_count.items():
                        if int(count) != 0:
                            self.common.nd.fail_json(
                                msg=f"vPC pair {vpc_pair_key} cannot be deleted because it is in use by {count} networks with status '{status}'. Detach these networks first.",
                            )
            except (KeyError, ValueError, TypeError) as error:
                self.log.warning(f"Error checking network count for {vpc_pair_key}: {error}")

            # Check VRF count with error handling
            try:
                vrf_count = response["overlay"].get("vrfCount", {})
                if not isinstance(vrf_count, dict):
                    self.log.warning(f"vrfCount is not a dict for {vpc_pair_key}, skipping VRF validation")
                else:
                    self.log.debug(f"VRF count for {vpc_pair_key}: {vrf_count}")
                    for status, count in vrf_count.items():
                        if int(count) != 0:
                            self.common.nd.fail_json(
                                msg=f"vPC pair {vpc_pair_key} cannot be deleted because it is in use by {count} VRFs with status '{status}'. Detach these VRFs first.",
                            )
            except (KeyError, ValueError, TypeError) as error:
                self.log.warning(f"Error checking VRF count for {vpc_pair_key}: {error}")

            # Check for active vPC interfaces with error handling
            try:
                if response.get("inventory"):
                    logical_interfaces = response["inventory"].get("logicalInterfaces", {})
                    if isinstance(logical_interfaces, dict):
                        vpc_interface_count = logical_interfaces.get("VPC", 0)
                        if int(vpc_interface_count) != 0:
                            self.common.nd.fail_json(
                                msg=f"vPC pair {vpc_pair_key} cannot be deleted because it has {vpc_interface_count} active vPC member port(s). Remove these interfaces first.",
                            )
                    else:
                        self.log.warning(f"logicalInterfaces is not a dict for {vpc_pair_key}, skipping interface validation")
                else:
                    self.log.warning(
                        f"Inventory data not available in overview response for {vpc_pair_key}. Proceeding with deletion (may fail if vPC interfaces exist)."
                    )
            except (KeyError, ValueError, TypeError) as error:
                self.log.warning(f"Error checking vPC interface count for {vpc_pair_key}: {error}. Proceeding with deletion.")

            # Build deletion payload with vpcAction="unPair" for ND Manage 4.x API
            deletion_payload = {"vpcAction": "unPair"}

            # Validate using VpcUnpairingRequest schema
            try:
                unpair_request = NdVpcPairSchema.VpcUnpairingRequest(**deletion_payload)
                payload = unpair_request.model_dump(by_alias=True, exclude_none=True, mode="json")
            except Exception as e:
                self.log.warning(f"Failed to validate with VpcUnpairingRequest schema: {e}, using raw payload")
                payload = deletion_payload

            # Use endpoint model for deletion
            delete_endpoint = EpVpcPairPut()
            delete_endpoint.fabric_name = self.common.fabric
            delete_endpoint.switch_id = vpc_pair.switch_id

            self.common.requests[vpc_pair_key] = {
                "verb": delete_endpoint.verb.value,
                "path": delete_endpoint.path,
                "payload": payload,
            }

    def collect_deletion_requests(self):
        """
        Get a list of vPC pairs that need to be deleted based on the current state.

        This method compares the desired state (want) with the current state (have)
        and identifies vPC pairs that exist in both lists, preparing them for deletion.
        It also handles pending create and pending delete lists according to the following rules:

        1. If a pair exists in pending_create which is not in deleted wants, add that to results
        2. If a pair is pending deleted, but is not mentioned in deleted wants, add that to results in a separate list
        3. If a pair is already in the pending deleted state and is in deleted want, remove from want and add to normal result

        Returns:
            None: Updates self.common.requests and self.common.result with deletion operations
        """

        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Initialize result lists for pending pairs
        if "pending_create_pairs_not_in_delete" not in self.common.result:
            self.common.result["pending_create_pairs_not_in_delete"] = []
        if "existing_pending_deletes_not_in_request" not in self.common.result:
            self.common.result["existing_pending_deletes_not_in_request"] = []

        vpc_pairs_to_delete = []
        pending_vpc_pairs_to_delete = []
        # Handle case when no specific vPC pairs are requested for deletion
        if not self.common.want:
            self.log.debug("No vPC pairs specified in want, preparing to delete all existing vPC pairs ")
            vpc_pairs_to_delete = list(self.common.have)
            pending_vpc_pairs_to_delete = list(self.common.pending_delete_vpc_pairs)
        else:
            # prints existing pending creates that do not get deleted (deploy will create these)
            for pending_create_pair in self.common.pending_create_vpc_pairs:
                found_pair = self.common.get_pair_from_switches(self.common.want, pending_create_pair.switch_id, pending_create_pair.peer_switch_id)
                if not found_pair:
                    self.log.debug(f"Pending create vPC pair {pending_create_pair.get_switch_pair_key()} not in delete wants, adding to separate results list")
                    self.common.result["pending_create_pairs_not_in_delete"].append(pending_create_pair.model_dump())
                else:
                    pending_vpc_pairs_to_delete.append(pending_create_pair)

            # prints existing pending deletes not in request (deploy will delete these)
            for pending_delete_pair in self.common.pending_delete_vpc_pairs:
                found_pair = self.common.get_pair_from_switches(self.common.want, pending_delete_pair.switch_id, pending_delete_pair.peer_switch_id)

                if not found_pair:
                    self.log.debug(f"Pending delete vPC pair {pending_delete_pair.get_switch_pair_key()} not in delete wants, adding to separate results list")
                    self.common.result["existing_pending_deletes_not_in_request"].append(pending_delete_pair.model_dump())

            # Find vPC pairs that exist in both filtered_want and have
            for vpc_pair in self.common.want:
                found_pair = self.common.get_pair_from_switches(self.common.have, vpc_pair.switch_id, vpc_pair.peer_switch_id)
                if found_pair:
                    vpc_pairs_to_delete.append(vpc_pair)

        # Process the deletions using the helper method
        self._process_vpc_pair_deletions(vpc_pairs_to_delete, pending_vpc_pairs_to_delete)


class Overridden:
    """
    Handles the 'overridden' state for vPC pair management operations.

    This class manages the overridden state by:
    1. Finding all vPC pairs in 'have' but not in 'want' and sending them to delete state
    2. Sending all remaining pairs (those in 'want') to replace state

    The overridden operation ensures that the final state matches exactly what is specified
    in the desired configuration, removing any vPC pairs not explicitly defined and
    creating/updating those that are defined.

    Args:
        logger (optional): Logger instance for debugging. Defaults to None
        common_util (optional): Common utility instance. Defaults to None

    Attributes:
        class_name (str): Name of the current class
        log: Logger instance for debugging operations
        common: Common utility instance for shared operations
    """

    def __init__(self, logger=None, common_util=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")

        self.common = common_util

        msg = "ENTERED Overridden(): "
        msg += f"state: {self.common.state}, "
        self.log.debug(msg)

        # Validate that all switches exist in fabric
        self.common.validate_switches_exist()

        self.build_request()

    def build_request(self):
        """
        Build API requests for overridden state operations.

        This method implements the overridden state logic by:
        1. Finding all vPC pairs in 'have' but not in 'want' and building deletion requests
        2. Processing all vPC pairs in 'want' using replace logic (same as merge)

        The method ensures that the final state exactly matches the desired configuration
        by removing unwanted vPC pairs and creating/updating the desired ones.

        The implementation avoids deepcopy to prevent stale data and race conditions.
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Step 1: Find all vPC pairs in 'have' but not in 'want' and build deletion requests
        vpc_pairs_to_delete = []
        for have_vpc_pair in self.common.have:
            # Check if this have_vpc_pair exists in the want list
            found_in_want = self.common.get_pair_from_switches(self.common.want, have_vpc_pair.switch_id, have_vpc_pair.peer_switch_id)

            if not found_in_want:
                vpc_pairs_to_delete.append(have_vpc_pair)
                self.log.debug(f"vPC pair {have_vpc_pair.get_switch_pair_key()} found in have but not in want - marking for deletion")

        # Build deletion requests directly without using deepcopy
        if vpc_pairs_to_delete:
            self.log.debug(f"Building deletion requests for {len(vpc_pairs_to_delete)} vPC pairs")
            self._build_deletion_requests(vpc_pairs_to_delete)

        # Step 2: Send all remaining pairs (those in 'want') to replace state
        # Use the Replaced class for processing wanted vPC pairs
        # Pass vpc_pairs_to_delete so validation can exclude them from conflict checks
        if self.common.want:
            self.log.debug(f"Using Replaced class to process {len(self.common.want)} vPC pairs in want")
            self.log.debug(f"Passing {len(vpc_pairs_to_delete)} pairs to exclude from conflict validation")
            replaced_handler = Replaced(common_util=self.common, exclude_pairs=vpc_pairs_to_delete)
            # The replaced_handler will have already populated self.common.requests with the replace operations

    def _build_deletion_requests(self, vpc_pairs_to_delete):
        """
        Build deletion requests for vPC pairs without using deepcopy.

        This method directly builds deletion requests for the specified vPC pairs,
        avoiding the race condition and stale data issues that come with deepcopy.

        Args:
            vpc_pairs_to_delete (list): List of VpcPairBase objects to delete

        Raises:
            AnsibleModule.fail_json: If validation checks fail or API calls fail
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Skip pairs that are already in pending delete state
        pending_delete_keys = {pair.get_switch_pair_key() for pair in self.common.pending_delete_vpc_pairs}

        for vpc_pair in vpc_pairs_to_delete:
            vpc_pair_key = vpc_pair.get_switch_pair_key()

            if vpc_pair_key in pending_delete_keys:
                self.log.debug(f"Skipping vPC pair {vpc_pair_key} as it is already in pending delete state.")
                continue

            self.log.debug(f"Building deletion request for vPC pair: {vpc_pair_key}")

            try:
                # Use endpoint model for overview check
                overview_endpoint = EpVpcPairOverviewGet()
                overview_endpoint.fabric_name = self.common.fabric
                overview_endpoint.switch_id = vpc_pair.switch_id
                overview_endpoint.component_type = "full"
                overview_path = overview_endpoint.path

                response = self.common.nd.request(
                    overview_path,
                    method=overview_endpoint.verb.value,
                )

                # Validate response
                if response is None:
                    self.common.nd.fail_json(msg=f"Received None response when checking vPC pair {vpc_pair_key} overview at {overview_path}")

                if not isinstance(response, dict):
                    self.common.nd.fail_json(
                        msg=f"Expected dict response from vPC pair overview for {vpc_pair_key}, got {type(response).__name__}",
                        response=response,
                    )

                self.log.debug("vPC pair overview request: %s", overview_path)
                self.log.debug("vPC pair overview response: %s", json.dumps(response, indent=2))

            except Exception as error:
                error_msg = f"Failed to fetch vPC pair overview for {vpc_pair_key} at {overview_path}: {str(error)}"
                self.log.error(error_msg)
                self.common.nd.fail_json(msg=error_msg)

            # Validate overlay data exists
            if not response.get("overlay"):
                self.common.nd.fail_json(
                    msg=f"vPC pair {vpc_pair_key} might not exist or overlay data unavailable",
                    response=response,
                )

            # Check network count with error handling
            try:
                network_count = response["overlay"].get("networkCount", {})
                if not isinstance(network_count, dict):
                    self.log.warning(f"networkCount is not a dict for {vpc_pair_key}, skipping network validation")
                else:
                    self.log.debug(f"Network count for {vpc_pair_key}: {network_count}")
                    for status, count in network_count.items():
                        if int(count) != 0:
                            self.common.nd.fail_json(
                                msg=f"vPC pair {vpc_pair_key} cannot be deleted because it is in use by {count} networks with status '{status}'. Detach these networks first.",
                            )
            except (KeyError, ValueError, TypeError) as error:
                self.log.warning(f"Error checking network count for {vpc_pair_key}: {error}")

            # Check VRF count with error handling
            try:
                vrf_count = response["overlay"].get("vrfCount", {})
                if not isinstance(vrf_count, dict):
                    self.log.warning(f"vrfCount is not a dict for {vpc_pair_key}, skipping VRF validation")
                else:
                    self.log.debug(f"VRF count for {vpc_pair_key}: {vrf_count}")
                    for status, count in vrf_count.items():
                        if int(count) != 0:
                            self.common.nd.fail_json(
                                msg=f"vPC pair {vpc_pair_key} cannot be deleted because it is in use by {count} VRFs with status '{status}'. Detach these VRFs first.",
                            )
            except (KeyError, ValueError, TypeError) as error:
                self.log.warning(f"Error checking VRF count for {vpc_pair_key}: {error}")

            # Check for active vPC interfaces with error handling
            try:
                if response.get("inventory"):
                    logical_interfaces = response["inventory"].get("logicalInterfaces", {})
                    if isinstance(logical_interfaces, dict):
                        vpc_interface_count = logical_interfaces.get("VPC", 0)
                        if int(vpc_interface_count) != 0:
                            self.common.nd.fail_json(
                                msg=f"vPC pair {vpc_pair_key} cannot be deleted because it has {vpc_interface_count} active vPC member port(s). Remove these interfaces first.",
                            )
                    else:
                        self.log.warning(f"logicalInterfaces is not a dict for {vpc_pair_key}, skipping interface validation")
                else:
                    self.log.warning(
                        f"Inventory data not available in overview response for {vpc_pair_key}. Proceeding with deletion (may fail if vPC interfaces exist)."
                    )
            except (KeyError, ValueError, TypeError) as error:
                self.log.warning(f"Error checking vPC interface count for {vpc_pair_key}: {error}. Proceeding with deletion.")

            # Build deletion payload with vpcAction="unPair" for ND Manage 4.x API
            deletion_payload = {"vpcAction": "unPair"}

            # Validate using VpcUnpairingRequest schema
            try:
                unpair_request = NdVpcPairSchema.VpcUnpairingRequest(**deletion_payload)
                payload = unpair_request.model_dump(by_alias=True, exclude_none=True, mode="json")
            except Exception as e:
                self.log.warning(f"Failed to validate with VpcUnpairingRequest schema: {e}, using raw payload")
                payload = deletion_payload

            # Use endpoint model for deletion
            delete_endpoint = EpVpcPairPut()
            delete_endpoint.fabric_name = self.common.fabric
            delete_endpoint.switch_id = vpc_pair.switch_id

            # Add to requests with delete prefix to avoid key conflicts
            deletion_key = f"delete_{vpc_pair_key}"
            self.common.requests[deletion_key] = {
                "verb": delete_endpoint.verb.value,
                "path": delete_endpoint.path,
                "payload": payload,
            }
            self.log.debug(f"Added deletion request for vPC pair {vpc_pair_key}")


class Query:
    """
    Query class for managing vPC pair state retrieval in Cisco ND.

    This class handles query operations for vPC pair management in the Cisco Nexus Dashboard.
    It provides functionality to retrieve and return vPC pair state information.

    Args:
        task_params: The Ansible task_params context containing configuration parameters
        have_state: The current state of the vPC pairs being queried

    Attributes:
        class_name (str): The name of the current class
        log (logging.Logger): Logger instance for the Query class
        common (Common): Common utility instance for shared operations
        have: The current have state of the vPC pairs

    Note:
        This class is part of the Cisco ND Ansible collection for vPC pair management
        operations and follows the standard query pattern for state retrieval.
    """

    def __init__(self, common_util=None, logger=None):
        self.class_name = self.__class__.__name__
        self.log = logger or logging.getLogger(f"nd.{self.class_name}")
        self.common = common_util

        msg = "ENTERED Query(): "
        msg += f"state: {self.common.state}, "
        self.log.debug(msg)

    def get_query_results(self):
        """
        Retrieve the current state of vPC pairs including pending create and delete lists when they contain items.

        This method collects the current state of vPC pairs from the have state
        and prepares it for output in the query result format. It conditionally includes
        separate lists for pending create and delete vpc pairs only if they contain items.

        When no specific search criteria (want) is provided, all vPC pairs are returned.
        When search criteria is provided, only matching vPC pairs are included in all lists.

        Returns:
            dict: A dictionary containing:
                - query: A nested dictionary with:
                    - vpc_pairs: List of active vPC pair configurations (always present, may be empty)
                    - pending_create_vpc_pairs: List of vPC pairs pending creation (only if items exist)
                    - pending_delete_vpc_pairs: List of vPC pairs pending deletion (only if items exist)
        """
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable
        msg = f"ENTERED: {self.class_name}.{method_name}"
        self.log.debug(msg)

        # Initialize result dictionary with vpc_pairs (always present)
        results = {"query": {"vpc_pairs": []}}

        if not self.common.want:
            # Return all vPC pairs when no specific search criteria provided
            results["query"]["vpc_pairs"] = [vpc_pair.model_dump() for vpc_pair in self.common.have]

            # Only add pending lists if they contain items
            if self.common.pending_create_vpc_pairs:
                results["query"]["pending_create_vpc_pairs"] = [vpc_pair.model_dump() for vpc_pair in self.common.pending_create_vpc_pairs]
            if self.common.pending_delete_vpc_pairs:
                results["query"]["pending_delete_vpc_pairs"] = [vpc_pair.model_dump() for vpc_pair in self.common.pending_delete_vpc_pairs]
        else:
            # Search for specific vPC pairs in have, pending_create, and pending_delete lists
            # Also filter pending lists based on want criteria
            pending_create_filtered = []
            pending_delete_filtered = []
            query_filtered = []

            for item in self.common.want:
                item_dict = item.model_dump()
                found_vpc_pair = None

                # Search in have list
                # Handle both old and new field names
                peer1_id = item_dict.get("switchId") or item_dict.get("peer1SwitchId")
                peer2_id = item_dict.get("peerSwitchId") or item_dict.get("peer2SwitchId")

                if peer2_id:
                    found_vpc_pair = self.common.get_pair_from_switches(self.common.have, peer1_id, peer2_id)
                else:
                    found_vpc_pair = self.common.get_pair_from_switches(self.common.have, peer1_id)

                if found_vpc_pair:
                    query_filtered.append(found_vpc_pair)
                    continue

                # If not found in have, search in pending_create list
                if peer2_id:
                    found_vpc_pair = self.common.get_pair_from_switches(self.common.pending_create_vpc_pairs, peer1_id, peer2_id)
                else:
                    found_vpc_pair = self.common.get_pair_from_switches(self.common.pending_create_vpc_pairs, peer1_id)

                if found_vpc_pair:
                    pending_create_filtered.append(found_vpc_pair)
                    continue

                # If not found in have or pending_create, search in pending_delete list
                if peer2_id:
                    found_vpc_pair = self.common.get_pair_from_switches(self.common.pending_delete_vpc_pairs, peer1_id, peer2_id)
                else:
                    found_vpc_pair = self.common.get_pair_from_switches(self.common.pending_delete_vpc_pairs, peer1_id)

                if found_vpc_pair:
                    pending_delete_filtered.append(found_vpc_pair)

            # Set filtered lists in nested structure - vpc_pairs always present
            results["query"]["vpc_pairs"] = [vpc_pair.model_dump() for vpc_pair in query_filtered]

            # Only add pending lists if they contain filtered items
            if pending_create_filtered:
                results["query"]["pending_create_vpc_pairs"] = [vpc_pair.model_dump() for vpc_pair in pending_create_filtered]
            if pending_delete_filtered:
                results["query"]["pending_delete_vpc_pairs"] = [vpc_pair.model_dump() for vpc_pair in pending_delete_filtered]

        return results


# ============================================================================
# RestSend Helper Functions
# ============================================================================


def execute_request_with_restsend(nd: NDModuleV2, results: Results, vpc_pair_key: str, request_data: dict, mainlog) -> None:
    """
    Execute a single VPC pair request using RestSend pattern.

    Args:
        nd: NDModuleV2 instance
        results: Results aggregation instance
        vpc_pair_key: VPC pair identifier (e.g., "FDO1-FDO2")
        request_data: Dict with verb, path, payload, operation
        mainlog: Logger instance
    """
    verb_str = request_data["verb"]
    path = request_data["path"]
    payload = request_data.get("payload")

    # Convert string verb to HttpVerbEnum
    verb = HttpVerbEnum(verb_str)

    # Build metadata
    metadata = {"vpc_pair_key": vpc_pair_key, "operation": request_data.get("operation", verb_str), "path": path}

    mainlog.info("Executing request for VPC pair %s: %s %s", vpc_pair_key, verb_str, path)
    if payload:
        mainlog.debug("Payload: %s", json.dumps(payload, indent=2))

    try:
        # Use nd_v2.request() which internally uses RestSend
        data = nd.request(path, verb, payload)

        # Build response
        response = {
            "RETURN_CODE": nd.status,
            "METHOD": nd.method,
            "REQUEST_PATH": nd.path,
            "MESSAGE": nd.response,
            "DATA": data,
        }

        # Build result (success based on nd_v2 not raising exception)
        result = {
            "success": True,
            "changed": verb in [HttpVerbEnum.POST, HttpVerbEnum.PUT, HttpVerbEnum.DELETE],
        }

        # Build diff
        diff = build_diff_for_request(verb, vpc_pair_key, payload)

        mainlog.info("Request successful for VPC pair %s", vpc_pair_key)

    except NDModuleError as error:
        # Build error response
        response = {
            "RETURN_CODE": error.status if error.status else -1,
            "MESSAGE": error.msg,
            "REQUEST_PATH": path,
            "METHOD": verb_str,
            "DATA": error.data if error.data else {},
        }

        result = {"success": False, "changed": False}
        diff = {}

        mainlog.error("Request failed for VPC pair %s: %s", vpc_pair_key, error.msg)

    # Register with Results
    results.response_current = response
    results.result_current = result
    results.diff_current = diff
    results.metadata_current = metadata
    results.register_task_result()


def build_diff_for_request(verb: HttpVerbEnum, vpc_pair_key: str, payload: dict) -> dict:
    """
    Build diff dict for a request (maintains current output format).

    Args:
        verb: HTTP verb for the request
        vpc_pair_key: VPC pair identifier
        payload: Request payload

    Returns:
        Diff dict for this request
    """
    switch_ids = vpc_pair_key.replace("delete_", "").split("-")

    if verb == HttpVerbEnum.DELETE:
        return {
            "peer1SwitchId": switch_ids[0] if len(switch_ids) > 0 else "",
            "peer2SwitchId": switch_ids[1] if len(switch_ids) > 1 else "",
        }
    elif verb == HttpVerbEnum.PUT:
        diff_entry = {
            "peer1SwitchId": switch_ids[0] if len(switch_ids) > 0 else "",
            "peer2SwitchId": switch_ids[1] if len(switch_ids) > 1 else "",
        }
        if payload:
            diff_entry.update(payload)
        return diff_entry

    return {}


def deploy_fabric_with_restsend(nd: NDModuleV2, results: Results, fabric: str, mainlog) -> None:
    """
    Deploy fabric changes using RestSend pattern.

    Args:
        nd: NDModuleV2 instance
        results: Results aggregation instance
        fabric: Fabric name
        mainlog: Logger instance
    """
    mainlog.info("Starting fabric deployment for %s", fabric)

    # Step 1: Save config
    save_path = VpcPairBasePath.config_save(fabric)
    mainlog.info("Saving fabric configuration: %s", save_path)

    try:
        nd.request(save_path, HttpVerbEnum.POST, {})

        results.response_current = {
            "RETURN_CODE": nd.status,
            "METHOD": "POST",
            "REQUEST_PATH": save_path,
            "MESSAGE": "Config saved successfully",
            "DATA": {},
        }
        results.result_current = {"success": True, "changed": True}
        results.metadata_current = {"operation": "CONFIG_SAVE", "fabric": fabric}
        results.register_task_result()

        mainlog.info("Configuration saved successfully")

    except NDModuleError as error:
        # Log warning but continue to deploy
        mainlog.warning("Config save failed: %s", error.msg)

        results.response_current = {
            "RETURN_CODE": error.status if error.status else -1,
            "MESSAGE": error.msg,
            "REQUEST_PATH": save_path,
            "METHOD": "POST",
            "DATA": {},
        }
        results.result_current = {"success": False, "changed": False}
        results.metadata_current = {"operation": "CONFIG_SAVE_FAILED", "fabric": fabric}
        results.register_task_result()

    # Step 2: Deploy
    deploy_path = f"{VpcPairBasePath.fabrics(fabric, 'actions/deploy')}?forceShowRun=true"
    mainlog.info("Deploying fabric configuration: %s", deploy_path)

    try:
        nd.request(deploy_path, HttpVerbEnum.POST, {})

        results.response_current = {
            "RETURN_CODE": nd.status,
            "METHOD": "POST",
            "REQUEST_PATH": deploy_path,
            "MESSAGE": "Deployment successful",
            "DATA": {},
        }
        results.result_current = {"success": True, "changed": True}
        results.metadata_current = {"operation": "DEPLOY", "fabric": fabric}
        results.register_task_result()

        mainlog.info("Deployment completed successfully")

    except NDModuleError as error:
        mainlog.error("Deployment failed: %s", error.msg)

        results.response_current = {
            "RETURN_CODE": error.status if error.status else -1,
            "MESSAGE": error.msg,
            "REQUEST_PATH": deploy_path,
            "METHOD": "POST",
            "DATA": {},
        }
        results.result_current = {"success": False, "changed": False}
        results.metadata_current = {"operation": "DEPLOY_FAILED", "fabric": fabric}
        results.register_task_result()
        raise  # Re-raise to fail the module


def main():
    argument_spec = {}
    argument_spec.update(
        state=dict(
            type="str",
            default="merged",
            choices=["merged", "replaced", "deleted", "overridden", "query"],
        ),
        fabric=dict(required=True, type="str"),
        config=dict(required=False, type="list", elements="dict"),
        deploy=dict(required=False, type="bool", default=False),
        dry_run=dict(required=False, type="bool", default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    if sys.version_info < (3, 9):
        module.fail_json(msg="Python version 3.9 or higher is required for this module.")

    if not HAS_DEEPDIFF:
        module.fail_json(msg=missing_required_lib("deepdiff"), exception=DEEPDIFF_IMPORT_ERROR)

    # Validate that deploy is not used with query state
    if module.params.get("state") == "query" and module.params.get("deploy"):
        module.fail_json(msg="Deploy parameter cannot be used with 'query' state")

    # Validate that dry_run is not used with query state
    if module.params.get("state") == "query" and module.params.get("dry_run"):
        module.fail_json(msg="Dry_run parameter cannot be used with 'query' state")

    # Map dry_run to check_mode for RestSend integration
    if module.params.get("dry_run"):
        module.check_mode = True

    # Logging setup
    try:
        log = Log()
        log.commit()
        mainlog = logging.getLogger("nd.main")
    except ValueError as error:
        module.fail_json(str(error))

    mainlog.info("---------------------------------------------")
    mainlog.info("Starting cisco.nd.nd_manage_vpc_pairs module")
    mainlog.info("---------------------------------------------\n")

    # Initialize Results for RestSend aggregation
    state = module.params.get("state")
    results = Results()
    results.state = state
    results.check_mode = module.check_mode
    results.action = "vpc_pair_management"

    # Determine operation type from state
    if state == "query":
        results.operation_type = OperationType.QUERY
    elif state in ["merged", "replaced"]:
        results.operation_type = OperationType.UPDATE
    elif state == "deleted":
        results.operation_type = OperationType.DELETE
    elif state == "overridden":
        results.operation_type = OperationType.UPDATE

    # Initialize both nd modules - legacy for inventory, v2 for requests
    nd = NDModule(module)  # Legacy - used by inventory classes (to be migrated in Task #4)
    nd_v2 = NDModuleV2(module)  # New - used for RestSend requests
    task_params = nd.params
    mainlog.debug("Task parameters: %s", task_params)

    # Initialize inventory with error handling
    try:
        inventory = UpdateInventory(nd)
        inventory.refresh()
    except Exception as error:
        module.fail_json(msg=f"Failed to initialize or refresh inventory: {str(error)}")

    # Validate configuration
    try:
        vpc_pairs = Common(task_params, nd, inventory)
    except ValueError as error:
        module.fail_json(msg=f"Configuration validation error: {str(error)}")
    except Exception as error:
        module.fail_json(msg=f"Unexpected error during configuration validation: {str(error)}")

    # Get current vPC pair state with error handling
    try:
        vp_have = GetHave(nd, inventory)
        vp_have.refresh()
        have = vp_have.have
        vpc_pairs.have = have
        vpc_pairs.pending_delete_vpc_pairs = vp_have.pending_delete_vpc_pairs
        vpc_pairs.pending_create_vpc_pairs = vp_have.pending_create_vpc_pairs
    except Exception as error:
        module.fail_json(msg=f"Failed to retrieve current vPC pair state: {str(error)}")

    mainlog.debug("Haves: %s", vpc_pairs.have)
    mainlog.debug("Wants: %s", vpc_pairs.want)

    # Initialize task handler based on state
    try:
        task = None
        state = task_params.get("state")
        mainlog.debug(f"Initializing task handler for state: {state}")

        if state == "merged":
            task = Merged(common_util=vpc_pairs)
        elif state == "replaced":
            task = Replaced(common_util=vpc_pairs)
        elif state == "deleted":
            task = Deleted(common_util=vpc_pairs)
        elif state == "overridden":
            task = Overridden(common_util=vpc_pairs)
        elif state == "query":
            task = Query(common_util=vpc_pairs)
        else:
            module.fail_json(msg=f"Invalid state: {state}")

        if task is None:
            module.fail_json(msg=f"Failed to initialize task handler for state: {state}")

    except ValueError as error:
        module.fail_json(msg=f"Validation error during task initialization: {str(error)}")
    except Exception as error:
        module.fail_json(msg=f"Unexpected error during task initialization: {str(error)}")

    # Add IP to serial number mapping to results
    try:
        task.common.result["ip_to_sn_mapping"] = task.common.inventory.sw_sn_from_ip
    except Exception as error:
        mainlog.warning(f"Failed to add IP to SN mapping to results: {error}")
        task.common.result["ip_to_sn_mapping"] = {}

    # Handle query state
    if isinstance(task, Query):
        try:
            query_results = task.get_query_results()
            task.common.result.update(query_results)
            task.common.result["changed"] = False
            module.exit_json(**task.common.result)
        except Exception as error:
            module.fail_json(msg=f"Failed to gather vPC pair state: {str(error)}")

    # Process all the requests from task.common.requests using RestSend pattern
    # Sample entry:
    #   {'FDO23040Q85-FDO23040Q86': {'verb': 'DELETE', 'path': '/api/v1/manage/vpc-pairs/FDO23040Q85/FDO23040Q86', 'payload': ''}}
    if task.common.requests:
        mainlog.info("Processing %d VPC pair requests using RestSend", len(task.common.requests))
        for vpc_pair_key, request_data in task.common.requests.items():
            mainlog.debug("Processing request for vPC pair key: %s", vpc_pair_key)
            execute_request_with_restsend(nd_v2, results, vpc_pair_key, request_data, mainlog)
    else:
        mainlog.info("No requests to process")

    # Deploy fabric changes if deploy parameter is True and state is not query
    if task.common.deploy and task.common.state != "query":
        try:
            if task.common.dry_run or module.check_mode:
                mainlog.info("CHECK MODE: Showing deployment information without executing")
                task.common.show_dry_run_deployment_info()
            else:
                mainlog.info("Deploy parameter is True, deploying fabric configuration changes")
                deploy_fabric_with_restsend(nd_v2, results, task.common.fabric, mainlog)
        except NDModuleError as error:
            mainlog.error("Deployment failed with NDModuleError: %s", error.msg)
            # Results already updated by deploy_fabric_with_restsend before raising
            results.build_final_result()
            module.fail_json(**results.final_result)
        except Exception as error:
            mainlog.error("Unexpected error during deployment: %s", error)
            module.fail_json(msg=f"Deployment failed with unexpected error: {str(error)}")

    # Build final result using Results aggregator
    results.build_final_result()

    # For backward compatibility, merge legacy result structure if needed
    # The Results class provides: changed, failed, diff, response, result, metadata
    # Legacy code expects: changed, diff (grouped by verb), response, query, warnings
    final_output = results.final_result

    # For query state, preserve the query results from task.common.result
    if isinstance(task, Query):
        if "query" in task.common.result:
            final_output["query"] = task.common.result["query"]

    # Preserve warnings if any
    if "warnings" in task.common.result:
        final_output["warnings"] = task.common.result["warnings"]

    # Preserve IP to SN mapping if present
    if "ip_to_sn_mapping" in task.common.result:
        final_output["ip_to_sn_mapping"] = task.common.result["ip_to_sn_mapping"]

    # Exit based on results
    if True in results.failed:
        module.fail_json(**final_output)
    module.exit_json(**final_output)


if __name__ == "__main__":
    main()
