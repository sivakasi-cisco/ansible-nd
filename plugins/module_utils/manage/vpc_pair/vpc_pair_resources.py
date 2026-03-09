# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import sys
import types as py_types
from typing import Any, Callable, Dict, List, Optional

from ansible.module_utils.basic import AnsibleModule
from pydantic import ValidationError


def register_nd_state_machine_import_aliases() -> None:
    """
    Register compatibility aliases required by nd_state_machine flat imports.
    """
    nd_module = importlib.import_module(
        "ansible_collections.cisco.nd.plugins.module_utils.nd"
    )
    constants_module = importlib.import_module(
        "ansible_collections.cisco.nd.plugins.module_utils.constants"
    )
    nd_config_collection_module = importlib.import_module(
        "ansible_collections.cisco.nd.plugins.module_utils.nd_config_collection"
    )
    models_base_module = importlib.import_module(
        "ansible_collections.cisco.nd.plugins.module_utils.models.base"
    )

    sys.modules.setdefault("nd", nd_module)
    sys.modules.setdefault("constants", constants_module)
    sys.modules.setdefault("nd_config_collection", nd_config_collection_module)

    # Keep compatibility scoped to vpc_pair runtime: NDStateMachine expects
    # NDConfigCollection.to_list(), while PR172 exposes to_ansible_config().
    nd_config_collection_cls = getattr(
        nd_config_collection_module, "NDConfigCollection", None
    )
    if (
        nd_config_collection_cls is not None
        and not hasattr(nd_config_collection_cls, "to_list")
    ):
        def _to_list(self, **kwargs):
            return self.to_ansible_config(**kwargs)

        setattr(nd_config_collection_cls, "to_list", _to_list)

    models_pkg = sys.modules.get("models")
    if models_pkg is None:
        models_pkg = py_types.ModuleType("models")
        models_pkg.__path__ = []
        sys.modules["models"] = models_pkg

    setattr(models_pkg, "base", models_base_module)
    sys.modules.setdefault("models.base", models_base_module)

    # nd_state_machine imports orchestrators.base for typing. Prefer the real
    # module and only install a shim if importing it fails in this environment.
    orchestrators_pkg_name = (
        "ansible_collections.cisco.nd.plugins.module_utils.orchestrators"
    )
    orchestrator_base_name = f"{orchestrators_pkg_name}.base"
    if orchestrator_base_name not in sys.modules:
        try:
            importlib.import_module(orchestrator_base_name)
        except Exception:
            orchestrators_pkg = sys.modules.get(orchestrators_pkg_name)
            if orchestrators_pkg is None:
                orchestrators_pkg = py_types.ModuleType(orchestrators_pkg_name)
                orchestrators_pkg.__path__ = []
                sys.modules[orchestrators_pkg_name] = orchestrators_pkg

            orchestrator_base_module = py_types.ModuleType(orchestrator_base_name)

            class NDBaseOrchestrator:  # pragma: no cover - import shim
                pass

            orchestrator_base_module.NDBaseOrchestrator = NDBaseOrchestrator
            setattr(orchestrators_pkg, "base", orchestrator_base_module)
            sys.modules[orchestrator_base_name] = orchestrator_base_module


register_nd_state_machine_import_aliases()

from ansible_collections.cisco.nd.plugins.module_utils.nd_state_machine import NDStateMachine


ActionHandler = Callable[[Any], Any]
RunStateHandler = Callable[[Any], Dict[str, Any]]
DeployHandler = Callable[[Any, str, Dict[str, Any]], Dict[str, Any]]
NeedsDeployHandler = Callable[[Dict[str, Any], Any], bool]


class _VpcPairQueryContext:
    """Minimal context object for query_all during NDStateMachine initialization."""

    def __init__(self, module: AnsibleModule):
        self.module = module


class VpcPairOrchestrator:
    """
    VPC orchestrator implementation for NDStateMachine.

    Delegates CRUD operations to injected vPC action handlers.
    """

    model_class = None

    def __init__(self, module: AnsibleModule):
        self.module = module
        self.state_machine = None

        self.model_class = getattr(self.module, "_vpc_pair_model_class", None)
        self.actions = getattr(self.module, "_vpc_pair_actions", {})

        if self.model_class is None:
            raise ValueError("Missing _vpc_pair_model_class in module params")
        required_actions = {"query_all", "create", "update", "delete"}
        if not required_actions.issubset(set(self.actions)):
            raise ValueError(
                "Missing required _vpc_pair_actions. Required keys: "
                "query_all, create, update, delete"
            )

    def bind_state_machine(self, state_machine: "VpcPairStateMachine") -> None:
        self.state_machine = state_machine

    def query_all(self):
        context = self.state_machine if self.state_machine is not None else _VpcPairQueryContext(self.module)
        return self.actions["query_all"](context)

    def create(self, model_instance, **kwargs):
        _ = (model_instance, kwargs)
        if self.state_machine is None:
            raise RuntimeError("VpcPairOrchestrator is not bound to a state machine")
        return self.actions["create"](self.state_machine)

    def update(self, model_instance, **kwargs):
        _ = (model_instance, kwargs)
        if self.state_machine is None:
            raise RuntimeError("VpcPairOrchestrator is not bound to a state machine")
        return self.actions["update"](self.state_machine)

    def delete(self, model_instance, **kwargs):
        _ = (model_instance, kwargs)
        if self.state_machine is None:
            raise RuntimeError("VpcPairOrchestrator is not bound to a state machine")
        return self.actions["delete"](self.state_machine)


class VpcPairStateMachine(NDStateMachine):
    """NDStateMachine adapter with state handling compatible with nd_vpc_pair."""

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
        self.params["state"] = state
        self.ansible_config = new_configs or []

        try:
            parsed_items = []
            for config in self.ansible_config:
                try:
                    parsed_items.append(self.model_class.model_validate(config))
                except ValidationError as e:
                    self.fail_json(
                        msg=f"Invalid configuration: {e}",
                        config=config,
                        validation_errors=e.errors(),
                    )
                    return

            self.proposed = self.nd_config_collection(model_class=self.model_class, items=parsed_items)
            self.previous = self.existing.copy()
        except Exception as e:
            self.fail_json(msg=f"Failed to prepare configurations: {e}", error=str(e))
            return

        if state in ["merged", "replaced", "overridden"]:
            self._manage_create_update_state(state, unwanted_keys)
            if state == "overridden":
                self._manage_override_deletions(override_exceptions)
        elif state == "deleted":
            self._manage_delete_state()
        else:
            self.fail_json(msg=f"Invalid state: {state}")

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
                    self.fail_json(msg=error_msg, identifier=str(identifier), error=str(e))
                    return

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
                    self.fail_json(msg=error_msg, identifier=str(identifier), error=str(e))
                    return

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
                    self.fail_json(msg=error_msg, identifier=str(identifier), error=str(e))
                    return


class VpcPairResourceService:
    """
    Runtime service for nd_vpc_pair execution flow.

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
        nd_vpc_pair = VpcPairStateMachine(module=self.module)
        result = self.run_state_handler(nd_vpc_pair)

        if "_ip_to_sn_mapping" in self.module.params:
            result["ip_to_sn_mapping"] = self.module.params["_ip_to_sn_mapping"]

        deploy = self.module.params.get("deploy", False)
        if deploy and not self.module.check_mode:
            deploy_result = self.deploy_handler(nd_vpc_pair, fabric_name, result)
            result["deployment"] = deploy_result
            result["deployment_needed"] = deploy_result.get(
                "deployment_needed",
                self.needs_deployment_handler(result, nd_vpc_pair),
            )

        return result
