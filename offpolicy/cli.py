from offpolicy import train as _train, DEFAULT_KWARGS
import tensorflow as tf
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import click
import json
import copy
import gym
import os


def parse_args(args):
    """Parse arbitrary command line arguments into a dictionary of
    parameters for specifying hyper-parameters
    https://stackoverflow.com/a/34097314

    Args:

    args: list of str
        a list of strings that specify command line args and values

    Returns:

    dict: dict of str: value
        a dictionary mapping names to their corresponding values
    """

    ret_args = dict()
    for index, k in enumerate(args):

        # check if there are additional args left
        if index < len(args) - 1:
            a, b = k, args[index+1]
        else:
            a, b = k, None

        new_key = None

        # double hyphen, equals
        if a.startswith('--') and '=' in a:
            new_key, val = a.split('=')

        # double hyphen, no arg
        elif a.startswith('--') and (not b or b.startswith('--')):
            val = True

        # double hypen, arg
        elif a.startswith('--') and b and not b.startswith('--'):
            val = b

        # there are no args left
        else:
            continue

        # parse int
        if isinstance(val, str):
            try:
                val = int(val)
            except ValueError:
                pass

        # parse float
        if isinstance(val, str):
            try:
                val = float(val)
            except ValueError:
                pass

        # santize the key
        ret_args[(new_key or a).strip(' -')] = val

    return ret_args


@click.group()
def cli():
    """A group of potential sub methods that are available for use through
    a command line interface
    """


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument('argv', nargs=-1, type=click.UNPROCESSED)
def train(argv):
    """Entry point for training an algorithm, the argv contain keyword
    hyper parameters parsed using a custom arg parser

    Args:

    argv: list
        a list of arbitrary named hyper parameters
    """

    kwargs = copy.copy(DEFAULT_KWARGS)
    kwargs.update(parse_args(argv))
    logdir = kwargs.pop('logdir', './ant')

    # load existing hyper params
    path = os.path.join(logdir, "kwargs.json")
    os.makedirs(logdir, exist_ok=True)
    if os.path.isfile(path):
        with open(path, "r") as f:
            existing_kwargs = json.load(f)
            existing_kwargs.update(kwargs)
            kwargs = existing_kwargs

    # save hyper params
    with open(path, "w") as f:
        json.dump(kwargs, f)

    # train a policy using soft actor critic
    np.random.seed(kwargs.pop('seed', 0))
    env = kwargs.pop('env', 'Ant-v2')
    _train(logdir,
           gym.make(env),
           gym.make(env),
           **kwargs)


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('--files', '-f', type=str, multiple=True)
@click.option('--names', '-n', type=str, multiple=True)
@click.option('--out',   '-o', type=str, default='plot.png')
@click.option('--tag',   '-t', type=str, default='return/max')
@click.option('--limit', '-l', type=int, default=2500000)
def plot(files, names, out, tag, limit):
    """A utility for plotting data in a tensorboard format into a
    visually aesthetic seaborn plot

    Args:

    files: list
        a list of file names pointing to tensorboard experimental runs
    names: list
        a list of algorithm names corresponding to tensorboard files
    out: str
        the name of the plot file to be generated by this utility
    tag: str
        the tag from the tensorboard file to read values from
    limit: int
        the max event step to be included in the plot
    """

    sns.set(style='darkgrid')

    # append the data into a pandas data frame
    df = pd.DataFrame(columns=[
        'Name', 'Environment Step', 'Average Return'])
    for f, name in zip(files, names):
        for e in tf.compat.v1.train.summary_iterator(f):
            for v in e.summary.value:
                if v.tag == tag and e.step <= limit:
                    v = tf.make_ndarray(v.tensor).tolist()
                    df = df.append(
                        {'Average Return': v,
                         'Environment Step': e.step,
                         'Name': name}, ignore_index=True)

    # generate a plot using matplotlib
    plt.clf()
    sns.lineplot(x='Environment Step',
                 y='Average Return',
                 hue='Name',
                 data=df)
    plt.savefig(out)
