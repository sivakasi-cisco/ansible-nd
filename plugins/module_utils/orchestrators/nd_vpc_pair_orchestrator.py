# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Sivakami S <sivakasi@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Any, Optional

from ansible.module_utils.basic import AnsibleModule


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

    def __init__(
        self,
        module: Optional[AnsibleModule] = None,
        sender: Optional[Any] = None,
        **kwargs,
    ):
        _ = kwargs
        # Compatibility with both NDStateMachine variants:
        # - legacy: model_orchestrator(module=...)
        # - Current: model_orchestrator(sender=nd_module)
        if module is None and sender is not None:
            module = getattr(sender, "module", None)
        if module is None:
            raise ValueError(
                "VpcPairOrchestrator requires either module=AnsibleModule "
                "or sender=<NDModule with .module>."
            )

        self.module = module
        self.sender = sender
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

    def bind_state_machine(self, state_machine: Any) -> None:
        self.state_machine = state_machine

    def query_all(self):
        context = (
            self.state_machine
            if self.state_machine is not None
            else _VpcPairQueryContext(self.module)
        )
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
