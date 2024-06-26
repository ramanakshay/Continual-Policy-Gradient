from agent.networks import MLP, LargeMLP
from agent.optimizers import Adam, SGD

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import MultivariateNormal, Categorical


class ModelType(object):
    def __init__(self):
        # networks, optimizers, encoders, decoders
        pass
    
    def __repr__(self):
        return "Model Type Class"


class ContinuousActor(object):
    def __init__(self, config):
        self.config = config
        self.obs_dim = self.config.obs_dim
        self.act_dim = self.config.act_dim

        self.actor = MLP(self.obs_dim, self.act_dim, self.config.hidden_dim)
        self.optim = Adam(self.actor.parameters(), lr = self.config.lr)

        self.cov_var = torch.full(size=(self.act_dim,), fill_value=0.5)
        self.cov_mat = torch.diag(self.cov_var)

    def __repr__(self):
        return f"Continuous Actor Model: \n\
    Network = {type(self.actor).__name__} \n\
    Optimizer = {type(self.optim).__name__}"

    def reset(self):
        self.optim.zero_grad()

    def update(self):
        self.optim.step()

    def get_action(self, obs, grad=True):
        with torch.set_grad_enabled(grad):
            mean = self.actor(obs)
            dist = MultivariateNormal(mean, self.cov_mat)
            action = dist.sample()
        return action, dist


class DiscreteActor(object):
    def __init__(self, config):
        self.config = config
        self.obs_dim = self.config.obs_dim
        self.act_dim = self.config.act_dim

        self.actor = MLP(self.obs_dim, self.act_dim, self.config.hidden_dim)
        self.optim = Adam(self.actor.parameters(), lr = self.config.lr)


    def __repr__(self):
        return f"Discrete Actor Model: \n\
    Network = {type(self.actor).__name__} \n\
    Optimizer = {type(self.optim).__name__}"

    def reset(self):
        self.optim.zero_grad()

    def update(self):
        self.optim.step()

    def get_action(self, obs, grad=True):
        with torch.set_grad_enabled(grad):
            output = self.actor(obs)
            probs = F.softmax(output, dim=1)
            dist = Categorical(probs)
            action = dist.sample()
            return action, dist


class ContinuousActorCritic(object):
    def __init__(self, config):
        self.config = config
        self.obs_dim = self.config.obs_dim
        self.act_dim = self.config.act_dim

        self.actor = LargeMLP(self.obs_dim, self.act_dim, self.config.hidden_dim)
        self.critic = LargeMLP(self.obs_dim, 1, self.config.hidden_dim)

        self.actor_optim = Adam(self.actor.parameters(), lr = self.config.lr)
        self.critic_optim = Adam(self.critic.parameters(), lr = self.config.lr)

        self.cov_var = torch.full(size=(self.act_dim,), fill_value=0.5)
        self.cov_mat = torch.diag(self.cov_var)

    def reset_critic(self):
        self.critic = LargeMLP(self.obs_dim, 1, self.config.hidden_dim)
        self.critic_optim = Adam(self.critic.parameters(), lr = self.config.lr)
        self.adam_optim = Adam(self.actor.parameters(), lr = self.config.lr)

    def __repr__(self):
        return f"Continuous Actor Critic Model: \n\
            Actor Network = {type(self.actor).__name__} \n\
            Actor Optimizer = {type(self.actor_optim).__name__} \n\
            Critic Network = {type(self.critic).__name__} \n\
            Critic Optimizer = {type(self.critic_optim).__name__}"

    def reset(self):
        self.actor_optim.zero_grad()
        self.critic_optim.zero_grad()

    def update(self):
        self.actor_optim.step()
        self.critic_optim.step()

    def get_action(self, obs, grad=True):
        with torch.set_grad_enabled(grad):
            mean = self.actor(obs)
            dist = MultivariateNormal(mean, self.cov_mat)
            action = dist.sample()
        return action, dist

    def get_value(self, obs, grad=True):
        with torch.set_grad_enabled(grad):
            value = self.critic(obs)
        return value


class DiscreteActorCritic(object):
    def __init__(self, config):
        self.config = config
        self.obs_dim = self.config.obs_dim
        self.act_dim = self.config.act_dim

        self.actor = MLP(self.obs_dim, self.act_dim, self.config.hidden_dim)
        self.critic = MLP(self.obs_dim, 1, self.config.hidden_dim)

        self.actor_optim = Adam(self.actor.parameters(), lr = self.config.lr)
        self.critic_optim = Adam(self.critic.parameters(), lr = self.config.lr)


    def __repr__(self):
        return f"Discrete Actor Critic Model: \n\
    Actor Network = {type(self.actor).__name__} \n\
    Actor Optimizer = {type(self.actor_optim).__name__} \n\
    Critic Network = {type(self.critic).__name__} \n\
    Critic Optimizer = {type(self.critic_optim).__name__}"

    def reset(self):
        self.actor_optim.zero_grad()
        self.critic_optim.zero_grad()

    def update(self):
        self.actor_optim.step()
        self.critic_optim.step()

    def get_action(self, obs, grad=True):
        with torch.set_grad_enabled(grad):
            output = self.actor(obs)
            probs = F.softmax(output, dim=1)
            dist = Categorical(probs)
            action = dist.sample()
            return action, dist

    def get_value(self, obs, grad=True):
        with torch.set_grad_enabled(grad):
            value = self.critic(obs)
        return value