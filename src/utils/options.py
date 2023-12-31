#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Python version: 3.7
import os
import argparse
import pathlib
import torch
from datetime import datetime


def args_parser(method):
    ''' 
        Get the input of system config parameters.
    '''
    parser = argparse.ArgumentParser()

    ## utils arguments
    parser.add_argument('--save', action = 'store_true',
                        help = "save training loss and test accuracy to files")

    parser.add_argument('--gpu', action = 'store_true',
                        help = "whether to use GPU to speedup training")
    
    parser.add_argument('-seed', type = int, default = 20,
                        help = "the seed of training task")
    
    parser.add_argument('-batch_round', type = int, default = 1,
                        help = "the number of mini-batch to transmit the smashed data to the server")

    ## global arguments
    parser.add_argument('--dt', action = 'store_true',
                        help = "use differential transmission to upload.")

    parser.add_argument('-K', '--client', type = int, default = 100,
                        help = "the amount of clients")
    

    iid = parser.add_mutually_exclusive_group()
    iid.add_argument('--iid', action = 'store_true',
                    help = "depart dataset in iid way")

    iid.add_argument('--noniid', action = 'store_true',
                    help = "depart dataset in non-iid way")


    ## server arguments
    parser.add_argument('--dataset', type = str, choices = ['cifar', 'femnist'],
                        help = "dataset name")

    parser.add_argument('--round', type = int, default = 10,
                        help = "global training round")

    parser.add_argument('--test_round', type = int, default = 4,
                        help = "test every ____ rounds")

    parser.add_argument('--batch_size', type = int, default = 128,
                        help = "batch size for server training or testing")


    activated = parser.add_mutually_exclusive_group()
    activated.add_argument('-U', '--user', type = int,
                        help = "the number of activated clients per round")

    ## client arguments
    parser.add_argument('--lr', type = float, required = True,
                        help = "learning rate (LR)")

    parser.add_argument('--gamma', type = float,
                        help = "decay rate of LR")

    parser.add_argument('--decay_epoch', type = int, default = 1,
                        help = "epoch number to decay the LR")

    parser.add_argument('-B', '--localBS', type = int,
                        help = "local batch size for clients")

    parser.add_argument('-E', '--localEP', type = int,
                        help = "local epoch number for clients")

    parser.add_argument('--shard', type = int, 
                        help = "setup the shard number per client for noniid")


    args = parser.parse_args(); args.method = method

    return args

def group_args(args):
    '''
        Grounp arguments as utils/server/client.
    '''

    u_args, s_args, c_args = {}, {}, {}

    ''' utils arguements '''
    u_args['save']= args.save
    u_args['seed']= args.seed
    u_args['batch_round']= args.batch_round
    

#     device = torch.device("cuda:0" if args.gpu and torch.cuda.is_available() else "cpu")
    device = torch.device("cuda") if args.gpu else 'cpu'
    u_args['device']= device

    u_args['dataset']= args.dataset
    u_args['method']= args.method
    u_args['dt']= args.dt
    u_args['sample']= 'iid' if args.iid else 'noniid'
    u_args['batch_size']= args.batch_size
    
    u_args['client']= args.client

    # if args.noniid: u_args['shard_num'] = 2
    if args.noniid: u_args['shard_num'] = args.shard



    ''' server arguments '''
    s_args['dataset']= args.dataset
    s_args['device']= device
       
    s_args['client']= u_args['client']

    s_args['round']= max(1, args.round)
    s_args['t_round']= max(1, args.test_round)

    s_args['batch_size']= args.batch_size
    s_args['activated'] = max(1, args.user)

    ''' client arguments '''
    c_args['device']= device
    c_args['dataset']= args.dataset

    c_args['lr']= args.lr
    c_args['batch_size']= args.localBS
    c_args['epoch']= args.localEP

    if args.gamma:
        c_args['lr_decay'] = True
        c_args['decay_gamma'] = args.gamma
        c_args['decay_epoch'] = args.decay_epoch
    else:
        c_args['lr_decay'] = False


    ''' other system parameters '''
    ## setup saving paths
    client_info	 = f"{c_args['dataset']}-{u_args['sample']}"
    train_info	 = f"K{s_args['client']}U{s_args['activated']}E{c_args['epoch']}BR{u_args['batch_round']}-{u_args['seed']}"

    timestamp = datetime.now().strftime('%H%M%S')
    dir_name = client_info + '-' + train_info + '-' + timestamp
    if u_args['save']:
        p = os.path.join('../saves', dir_name)
        u_args['save_path'] = p

        pathlib.Path(p).mkdir(exist_ok=False)
        print(f"\033[1;36m[NOTICE] Directory '{p}' build.\033[0m")

    return u_args, s_args, c_args