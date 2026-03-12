# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Any, Callable, Dict, List, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.nd.plugins.module_utils.orchestrators.nd_vpc_pair_orchestrator import (
    NDStateMachine,
)
from ansible_collections.cisco.nd.plugins.module_utils.orchestrators.vpc_pair import (
    VpcPairOrchestrator,
)
from pydantic import ValidationError


ActionHandler = Callable[[Any], Any]
RunStateHandler = Callable[[Any], Dict[str, Any]]
DeployHandler = Callable[[Any, str, Dict[str, Any]], Dict[str, Any]]
NeedsDeployHandler = Callable[[Dict[str, Any], Any], bool]


class VpcPairResourceError(Exception):
    """Structured error raised by vpc_pair runtime layers."""

    def __init__(self, msg: str, **details: Any):
        super().__init__(msg)
        self.msg = msg
        self.details = details


class VpcPairStateMachine(NDStateMachine):
    """NDStateMachine adapter with state handling for nd_manage_vpc_pair."""

    def __init__(self, module: AnsibleModule):
        super().__init__(module=module, model_orchestrator=VpcPairOrchestrator)
        self.model_orchestrator.bind_state_machine(self)
        self.current_identifier = None
        self.existing_config: Dict[str, Any] = {}
        self.proposed_config: Dict[str, Any] = {}

    def manage_state(
        self,
        state: str,
        new_configs: List[Dict[str, Any]],
        unwanted_keys: Optional[List] = None,
        override_exceptions: Optional[List] = None,
    ) -> None:
        unwanted_keys = unwanted_keys or []
        override_exceptions = override_exceptions or []

        self.state = state
        if hasattr(self, "params") and isinstance(getattr(self, "params"), dict):
            self.params["state"] = state
        else:
            self.module.params["state"] = state
        self.ansible_config = new_configs or []

        try:
            parsed_items = []
            for config in self.ansible_config:
                try:
                    parsed_items.append(self.model_class.model_validate(config))
                except ValidationError as e:
                    raise VpcPairResourceError(
                        msg=f"Invalid configuration: {e}",
                        config=config,
                        validation_errors=e.errors(),
                    )

            self.proposed = self.nd_config_collection(model_class=self.model_class, items=parsed_items)
            self.previous = self.existing.copy()
        except Exception as e:
            if isinstance(e, VpcPairResourceError):
                raise
            raise VpcPairResourceError(msg=f"Failed to prepare configurations: {e}", error=str(e))

        if state in ["merged", "replaced", "overridden"]:
            self._manage_create_update_state(state, unwanted_keys)
            if state == "overridden":
                self._manage_override_deletions(override_exceptions)
        elif state == "deleted":
            self._manage_delete_state()
        else:
            raise VpcPairResourceError(msg=f"Invalid state: {state}")

    def _manage_create_update_state(self, state: str, unwanted_keys: List) -> None:
        for proposed_item in self.proposed:
            identifier = proposed_item.get_identifier_value()
            try:
                self.current_identifier = identifier

                existing_item = self.existing.get(identifier)
                self.existing_config = (
                    existing_item.model_dump(by_alias=True, exclude_none=True)
                    if existing_item
                    else {}
                )

                try:
                    diff_status = self.existing.get_diff_config(
                        proposed_item, unwanted_keys=unwanted_keys
                    )
                except TypeError:
                    diff_status = self.existing.get_diff_config(proposed_item)

                if diff_status == "no_diff":
                    self.format_log(
                        identifier=identifier,
                        status="no_change",
                        after_data=self.existing_config,
                    )
                    continue

                if state == "merged" and existing_item:
                    final_item = self.existing.merge(proposed_item)
                else:
                    if existing_item:
                        self.existing.replace(proposed_item)
                    else:
                        self.existing.add(proposed_item)
                    final_item = proposed_item

                self.proposed_config = final_item.to_payload()

                if diff_status == "changed":
                    response = self.model_orchestrator.update(final_item)
                    operation_status = "updated"
                else:
                    response = self.model_orchestrator.create(final_item)
                    operation_status = "created"

                if not self.module.check_mode:
                    self.sent.add(final_item)
                    sent_payload = self.proposed_config
                else:
                    sent_payload = None

                self.format_log(
                    identifier=identifier,
                    status=operation_status,
                    after_data=(
                        response
                        if not self.module.check_mode
                        else final_item.model_dump(by_alias=True, exclude_none=True)
                    ),
                    sent_payload_data=sent_payload,
                )
            except Exception as e:
                error_msg = f"Failed to process {identifier}: {e}"
                self.format_log(
                    identifier=identifier,
                    status="no_change",
                    after_data=self.existing_config,
                )
                if not self.module.params.get("ignore_errors", False):
                    raise VpcPairResourceError(
                        msg=error_msg,
                        identifier=str(identifier),
                        error=str(e),
                    )

    def _manage_override_deletions(self, override_exceptions: List) -> None:
        diff_identifiers = self.previous.get_diff_identifiers(self.proposed)
        for identifier in diff_identifiers:
            if identifier in override_exceptions:
                continue

            try:
                self.current_identifier = identifier
                existing_item = self.existing.get(identifier)
                if not existing_item:
                    continue
                self.existing_config = existing_item.model_dump(
                    by_alias=True, exclude_none=True
                )
                self.model_orchestrator.delete(existing_item)
                self.existing.delete(identifier)
                self.format_log(identifier=identifier, status="deleted", after_data={})
            except Exception as e:
                error_msg = f"Failed to delete {identifier}: {e}"
                if not self.module.params.get("ignore_errors", False):
                    raise VpcPairResourceError(
                        msg=error_msg,
                        identifier=str(identifier),
                        error=str(e),
                    )

    def _manage_delete_state(self) -> None:
        for proposed_item in self.proposed:
            identifier = proposed_item.get_identifier_value()
            try:
                self.current_identifier = identifier
                existing_item = self.existing.get(identifier)
                if not existing_item:
                    self.format_log(identifier=identifier, status="no_change", after_data={})
                    continue

                self.existing_config = existing_item.model_dump(
                    by_alias=True, exclude_none=True
                )
                self.model_orchestrator.delete(existing_item)
                self.existing.delete(identifier)
                self.format_log(identifier=identifier, status="deleted", after_data={})
            except Exception as e:
                error_msg = f"Failed to delete {identifier}: {e}"
                if not self.module.params.get("ignore_errors", False):
                    raise VpcPairResourceError(
                        msg=error_msg,
                        identifier=str(identifier),
                        error=str(e),
                    )


class VpcPairResourceService:
    """
    Runtime service for nd_manage_vpc_pair execution flow.

    Orchestrates state management and optional deployment while keeping module
    entrypoint thin.
    """

    def __init__(
        self,
        module: AnsibleModule,
        model_class: Any,
        actions: Dict[str, ActionHandler],
        run_state_handler: RunStateHandler,
        deploy_handler: DeployHandler,
        needs_deployment_handler: NeedsDeployHandler,
    ):
        self.module = module
        self.model_class = model_class
        self.actions = actions
        self.run_state_handler = run_state_handler
        self.deploy_handler = deploy_handler
        self.needs_deployment_handler = needs_deployment_handler

    def _prime_runtime_context(self) -> None:
        required_actions = {"query_all", "create", "update", "delete"}
        if not required_actions.issubset(set(self.actions)):
            raise ValueError(
                "Invalid vPC action map. Required keys: query_all, create, update, delete"
            )
        # Store runtime objects on module attributes (not params) to avoid
        # JSON-serialization issues in httpapi connection parameter handling.
        self.module._vpc_pair_model_class = self.model_class
        self.module._vpc_pair_actions = self.actions

    def execute(self, fabric_name: str) -> Dict[str, Any]:
        self._prime_runtime_context()
        nd_manage_vpc_pair = VpcPairStateMachine(module=self.module)
        result = self.run_state_handler(nd_manage_vpc_pair)

        if "_ip_to_sn_mapping" in self.module.params:
            result["ip_to_sn_mapping"] = self.module.params["_ip_to_sn_mapping"]

        deploy = self.module.params.get("deploy", False)
        if deploy and not self.module.check_mode:
            deploy_result = self.deploy_handler(nd_manage_vpc_pair, fabric_name, result)
            result["deployment"] = deploy_result
            result["deployment_needed"] = deploy_result.get(
                "deployment_needed",
                self.needs_deployment_handler(result, nd_manage_vpc_pair),
            )

        return result
