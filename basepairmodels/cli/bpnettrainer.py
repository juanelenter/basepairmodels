"""
    Python script for network training via the CLI

    License:
    
    MIT License

    Copyright (c) 2020 Kundaje Lab

    Permission is hereby granted, free of charge, to any person 
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without 
    restriction, including without limitation the rights to use, copy,
    modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be 
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""


import json
import logging
import os
import sys

from basepairmodels.cli import argparsers
from basepairmodels.cli.exceptionhandler import NoTracebackException
from basepairmodels.common import model_archs, training


def main():
    # parse the command line arguments
    parser = argparsers.training_argsparser()
    args = parser.parse_args()

    # input params
    input_params = {}
    input_params['data'] = args.input_data
    input_params['stranded'] = args.stranded
    input_params['has_control'] = args.has_control

    # output params 
    output_params = {}
    output_params['automate_filenames'] = args.automate_filenames
    output_params['time_zone'] = args.time_zone
    output_params['tag_length'] = args.tag_length
    output_params['output_dir'] = args.output_dir
    output_params['model_output_filename']= args.model_output_filename
    
    # genome params
    genome_params = {}
    genome_params['reference_genome'] = args.reference_genome
    genome_params['chrom_sizes'] = args.chrom_sizes
    genome_params['chroms'] = args.chroms
    genome_params['exclude_chroms'] = args.exclude_chroms

    # batch generation parameters
    batch_gen_params = {}    
    batch_gen_params['sequence_generator_name'] = args.sequence_generator_name
    batch_gen_params['input_seq_len'] = args.input_seq_len
    batch_gen_params['output_len'] = args.output_len
    batch_gen_params['sampling_mode'] = args.sampling_mode
    batch_gen_params['rev_comp_aug'] = args.reverse_complement_augmentation
    batch_gen_params['negative_sampling_rate'] = args.negative_sampling_rate
    batch_gen_params['max_jitter'] = args.max_jitter
    batch_gen_params['shuffle'] = args.shuffle
    
    # hyper parameters
    hyper_params = {}
    hyper_params['epochs'] = args.epochs
    hyper_params['batch_size'] = args.batch_size
    hyper_params['learning_rate'] = args.learning_rate
    hyper_params['min_learning_rate'] = args.min_learning_rate
    hyper_params['early_stopping_patience'] = args.early_stopping_patience
    hyper_params['early_stopping_min_delta'] = args.early_stopping_min_delta
    hyper_params['reduce_lr_on_plateau_patience'] = \
        args.reduce_lr_on_plateau_patience
    hyper_params['lr_reduction_factor'] = \
        args.lr_reduction_factor
    
    # parallelization parms
    parallelization_params = {}
    parallelization_params['threads'] = args.threads
    parallelization_params['gpus'] = args.gpus
    
    # network params
    network_params = {}
    network_params['name'] = args.model_arch_name
    network_params['filters'] = args.filters
    network_params['counts_loss_weight'] = args.counts_loss_weight
    network_params['control_smoothing'] = args.control_smoothing
    network_params['pearson_count_loss'] = args.pearson_count_loss
    
    # attribution prior params
    attribution_prior_params = {}
    attribution_prior_params['frquency_limit'] = \
        args.attribution_prior_frequency_limit
    attribution_prior_params['limit_softness'] = \
        args.attribution_prior_limit_softness
    attribution_prior_params['grad_smooth_sigma'] = \
        args.attribution_prior_grad_smooth_sigma
    attribution_prior_params['profile_grad_loss_weight'] = \
        args.attribution_prior_profile_grad_loss_weight
    attribution_prior_params['counts_grad_loss_weight'] = \
        args.attribution_prior_counts_grad_loss_weight
    
    if not os.path.exists(output_params['output_dir']):
        raise NoTracebackException(
            "Directory {} does not exist".format(output_params['output_dir']))

    if not output_params['automate_filenames'] and \
        output_params['automate_filenames'] is None:
        raise NoTracebackException(
            "Model output filename not specified")

    if not os.path.exists(genome_params['reference_genome']):
        raise NoTracebackException(
            "Reference genome file {} does not exist".format(
                genome_params['reference_genome'] ))
    
    if not os.path.exists(genome_params['chrom_sizes']):
        raise NoTracebackException(
            "Chromosome sizes file {} does not exist".format(
            genome_params['chrom_sizes']))
        
    try:
        get_model = getattr(model_archs, network_params['name'])
    except AttributeError:
        raise NoTracebackException(
            "Network {} not found in model definitions".format(
                network_params['name']))
    
    if not os.path.isfile(args.splits):
        raise NoTracebackException("File not found: {}", args.splits)
                
    # load splits from json file
    with open(args.splits, "r") as splits_json:
        splits = json.loads(splits_json.read())
    
    # training and validation
    training.train_and_validate_ksplits(
        input_params, output_params, genome_params, batch_gen_params, 
        hyper_params, parallelization_params, network_params, 
        args.use_attribution_prior, attribution_prior_params, splits)

if __name__ == '__main__':
    main()


