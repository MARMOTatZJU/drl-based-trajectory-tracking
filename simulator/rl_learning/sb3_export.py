"""
Official guid for exporting SB3 model:
    https://stable-baselines3.readthedocs.io/en/master/guide/export.html

TODO: unit test
"""

from typing import Union
import logging

import numpy as np
import torch as th
from torch import nn
import gym
import gym.spaces
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.policies import BasePolicy
from stable_baselines3 import TD3, SAC, DDPG

from drltt_proto.sdk.exported_policy_test_case_pb2 import ExportedPolicyTestCases
from common.io import convert_numpy_to_TensorFP, convert_TensorFP_to_numpy

ACTOR_CRITIC_ALGORITHMS = (TD3, SAC, DDPG)


class OnnxableActorCriticPolicy(th.nn.Module):
    """
    TODO: docstring

    Reference:
        https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/td3/policies.py
        https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/sac/policies.py
    """

    actor: nn.Module
    action_space_lb: th.Tensor
    action_space_ub: th.Tensor
    box_action_space: bool
    squash_output: bool

    def __init__(self, actor_critic_algorithm: BasePolicy):
        """
        TODO: docstring
        """
        super().__init__()
        policy: BasePolicy = actor_critic_algorithm.policy
        self.actor: nn.Module = policy.actor
        self.actor.eval()

        self.action_space_lb = th.from_numpy(policy.action_space.low)
        self.action_space_ub = th.from_numpy(policy.action_space.high)

        self.box_action_space = isinstance(policy.action_space, gym.spaces.Box)
        self.squash_output = policy.squash_output

        self.eval()

    def forward(self, observation: th.Tensor) -> th.Tensor:
        """
        Reference: https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/common/policies.py#L329

        TODO: docstring
        """
        # https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/common/policies.py#L366
        scaled_action: th.Tensor = self.actor(observation)

        # https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/common/policies.py#L370
        if self.box_action_space:
            if self.squash_output:
                action = self.unscale_action(scaled_action)
            else:
                action = th.clamp(scaled_action, self.action_space_lb, self.action_space_ub)

        # TODO: support vectorized inference
        # https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/common/policies.py#L380

        return action

    def unscale_action(self, scaled_action: th.Tensor) -> th.Tensor:
        """Rescale the action from [-1, 1] to [low, high].

        Reference: https://github.com/DLR-RM/stable-baselines3/tree/v2.2.1/stable_baselines3/common/policies.py#L400

        Args:
            scaled_action: Action scaled within [-1, 1]

        Return:
            th.Tensor: unscaled action
        """
        lb = self.action_space_lb
        ub = self.action_space_ub

        return lb + (0.5 * (scaled_action + 1.0) * (ub - lb))


def export_sb3_jit_module(
    algorithm: BasePolicy,
    environment: gym.Env,
    export_dir: str,
    test_case_save_format: str = 'protobuf',
    device: Union[th.device, str] = 'cpu',
    n_test_cases: int = 1,
) -> th.jit.ScriptModule:
    """Export jit module for stable-baselines3.

    Reference: https://stable-baselines3.readthedocs.io/en/master/guide/export.html#trace-export-to-c

    TODO: docstring

    Args:
        algorithm: SB3 algorithm to be traced.
        input_size: Input tensor size.
        device: Desired device where the tranced module is to be inferenced.
        export_dir: Directory to export traced module.
        test_case_save_format: ('protobuf'|'numpy')
        n_test_cases:
    """
    is_actor_critic_algorithm = any([isinstance(algorithm, ac_algo) for ac_algo in ACTOR_CRITIC_ALGORITHMS])
    assert (
        is_actor_critic_algorithm
    ), f'Algorithm {type(algorithm)} does not belong to actor critic algorithm: {ACTOR_CRITIC_ALGORITHMS}'

    # prepare test cases
    gt_observations = list()
    gt_actions = list()
    for _ in range(n_test_cases):
        observation = environment.reset()
        action, _states = algorithm.predict(observation)
        gt_observations.append(observation)
        gt_actions.append(action)
    gt_observations = np.stack(gt_observations, axis=0)
    gt_actions = np.stack(gt_actions, axis=0)

    # trace module
    onnxable_model = OnnxableActorCriticPolicy(algorithm)
    onnxable_model.to(device)
    dummy_input = th.from_numpy(gt_observations[0:1, ...])
    traced_module: th.jit.ScriptModule = th.jit.trace(onnxable_model.eval(), dummy_input)
    frozen_module = th.jit.freeze(traced_module)
    frozen_module = th.jit.optimize_for_inference(frozen_module)

    export_jit_path = f'{export_dir}/traced_policy.pt'
    th.jit.save(frozen_module, export_jit_path)
    logging.info(f'Traced JIT module saved at: {export_jit_path}')

    logging.info(f'Generated {gt_observations.shape[0]} test cases for Traced JIT module.')

    test_cases_prefix = f'{export_dir}/traced_policy_test_cases'
    if test_case_save_format == 'protobuf':
        test_cases = ExportedPolicyTestCases()
        test_cases.observations.CopyFrom(convert_numpy_to_TensorFP(gt_observations))
        test_cases.actions.CopyFrom(convert_numpy_to_TensorFP(gt_actions))
        test_cases_path = f'{test_cases_prefix}.bin'
        with open(test_cases_path, 'wb') as f:
            f.write(test_cases.SerializeToString())
    elif test_case_save_format == 'numpy':
        test_cases = dict(
            observations=gt_observations,
            actions=gt_actions,
        )
        test_cases_path = f'{test_cases_prefix}.npy'
        np.save(test_cases_path, test_cases, allow_pickle=True)
    else:
        raise ValueError(f'Invalid `test_case_save_format`: {test_case_save_format}')
    logging.info(f'Traced JIT module test cases saved at: {test_cases_path}')

    test_sb3_jit_module(export_jit_path, test_cases_path, test_case_save_format=test_case_save_format, device=device)

    return frozen_module


def test_sb3_jit_module(
    jit_module_path: str,
    test_cases_path: str,
    test_case_save_format: str = 'protobuf',
    device: Union[th.device, str] = 'cpu',
    rtol=1e-4,
    atol=1e-5,
) -> float:
    """
    TODO: docstring
    """
    logging.info(f'Testing jit module...')
    loaded_module = th.jit.load(jit_module_path)
    logging.info(f'Loaded jit module from: {jit_module_path}')

    if test_case_save_format == 'protobuf':
        test_cases = ExportedPolicyTestCases()
        with open(test_cases_path, 'rb') as f:
            test_cases.ParseFromString(f.read())
        gt_observations = convert_TensorFP_to_numpy(test_cases.observations)
        gt_actions = convert_TensorFP_to_numpy(test_cases.actions)
    elif test_case_save_format == 'numpy':
        test_cases = np.load(test_cases_path, allow_pickle=True)
        gt_observations = test_cases.item()['observations']
        gt_actions = test_cases.item()['actions']
    else:
        raise ValueError(f'Invalid `test_case_save_format`: {test_case_save_format}')
    logging.info(f'Loaded jit module test cases from: {test_cases_path}')

    jit_actions = loaded_module(th.from_numpy(gt_observations).to(device)).numpy()
    isclose = np.isclose(gt_actions, jit_actions, rtol=rtol, atol=atol)
    isclose_ratio = isclose.sum() / isclose.size
    logging.info(f'np.isclose(gt_actions, jit_actions) ratio={isclose_ratio}, rtol={rtol}, atol={atol}')

    return isclose_ratio
