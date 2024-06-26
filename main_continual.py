import gymnasium as gym

from agent.gae_models import DiscreteActorCritic, ContinuousActorCritic
from algorithms.gae import GAE

from evaluate import Evaluator
from dotmap import DotMap
from utils.logger import Logger
import torch

import argparse

# CONTINUAL POLICY GRADIENTS

def set_seed(seed, logger):
    if seed != None:
        assert(type(seed) == int)
        torch.manual_seed(seed)
        print(f"Successfully set seed to {seed}")
        logger.update_info(f"Seed = {seed}")

def choose_environment(env_name, logger):
    env = gym.make(env_name)
    logger.update_info(f"Environment = {env_name}\n")
    print('Environment', env_name)
    print()
    info = {}
    if env_name == 'Pendulum-v1':
        info = {
            'obs_dim': env.observation_space.shape[0],
            'act_dim': env.action_space.shape[0],
            'timesteps_per_update': 2048,
            'max_episode_length': 200,
            'total_timesteps': 2005000,
            'gamma': 0.99,
            'lr': 1e-3
        }
    elif env_name == 'Acrobot-v1':
        info  = {
            'obs_dim': env.observation_space.shape[0],
            'act_dim': env.action_space.n,
            'max_episode_length': 500,
            'timesteps_per_update': 5000,
            'total_timesteps': 150000,
            'gamma': 0.999,
            'lr': 3e-3
        }
    elif env_name == 'particle-v0':
        info  = {
            'obs_dim': env.observation_space.shape[0],
            'act_dim': env.action_space.shape[0],
            'max_episode_length': 200,
            'timesteps_per_update': 1000,
            'total_timesteps': 50000,
            'gamma': 0.999,
            'lr': 5e-4
        }
    else:
        raise InvalidArgumentError('Unknown environment.')

    return env, info

def choose_model(model_name, info, logger):
    model_config = DotMap({
        'obs_dim': info['obs_dim'],
        'act_dim': info['act_dim'],
        'lr': info['lr'],
        'hidden_dim': 128,
        'gam': info['gamma'],
        'lam': 1.0,
        'clip': 1.0,
        'replacing': False
    })
    if model_name == 'discrete-actor-critic':
        model = DiscreteActorCritic(model_config)
    elif model_name == 'continuous-actor-critic':
        model = ContinuousActorCritic(model_config)
    else:
        raise InvalidArgumentError('Unknown model.')

    logger.update_info(str(model))
    logger.update_info(str(model_config)+"\n")
    print(model)
    print(model_config)

    return model


def choose_algorithm(alg_name, info, logger):
    alg_config = DotMap({
        'max_episode_length': info['max_episode_length'],
        'timesteps_per_update': info['timesteps_per_update'],
        'gamma': info['gamma'],
        'lam': 0.9
    })
    total_timesteps = info['total_timesteps']
    if alg_name == 'gae':
        alg = GAE
    else:
        raise InvalidArgumentError('Unknown algorithm.')
    logger.update_info("Algorithm: ")
    logger.update_info(alg_name)
    logger.update_info(str(alg_config))
    logger.update_info(f"Total Timesteps={total_timesteps}")

    return alg, alg_config ,total_timesteps


def train(args):
    # logger
    logger = Logger()

    # dot map
    set_seed(args.seed, logger)
    env, info = choose_environment(args.env, logger)
    model = choose_model(args.model, info, logger)
    alg_class, alg_config, total_timesteps = choose_algorithm(args.alg, info, logger)
    alg = alg_class(env, model, alg_config, logger)
    alg.learn(total_timesteps)

    # save history
    log_name = str(args.seed) + "_" + args.env + "_Cont" + args.alg
    logger.save(log_name)

    return env, model


def eval(env, model):
    evaluator = Evaluator(env, model)
    
    # statistics
    evaluator.results()
        
    # render
    evaluator.render()


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', dest='seed', type=int, default=None)
    parser.add_argument('--env', dest='env', type=str, default='Acrobot-v1')
    parser.add_argument('--model', dest='model', type=str, default='discrete-actor-critic')
    parser.add_argument('--alg', dest='alg', type=str, default='gae')
    args = parser.parse_args()


    env, model = train(args)
    eval(env, model)





