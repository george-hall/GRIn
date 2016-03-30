#! /usr/bin/env python

################################################################################
# Copyright (c) 2016 Genome Research Ltd. 
# 
# Author: George Hall <gh10@sanger.ac.uk> 
# 
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 3 of the License, or (at your option) any later 
# version. 
# 
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details. 
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <http://www.gnu.org/licenses/>. 
################################################################################


import sys

import scipy.signal
import numpy as np

import custom_argument_parser


def find_start_repeat_kmers(hist_dict):

	order_num = 1

	min_list = scipy.signal.argrelextrema(np.array(hist_dict.values()), np.less_equal, 
		order = order_num)[0].tolist()
	max_list = scipy.signal.argrelextrema(np.array(hist_dict.values()), np.greater_equal, 
		order = order_num)[0].tolist()

	min_list_minimum = min(min_list)

	for maximum in sorted(max_list):
		if (maximum > min_list_minimum) and (maximum > 10):
			first_peak = maximum
			break

	# Return the point 'x' such that the first peak is equidistant 
	# between the first minimum and x
	return ((2 * first_peak) - min_list_minimum)


def create_hist_dict(in_file):
	hist_dict = {}
	for line in in_file.readlines():
		splat = [int(x) for x in line.strip().split()]
		hist_dict[splat[0]] = splat[1]

	return hist_dict


def calculate_gri(hist_dict, verbose, start_repetitive_kmers = 0):
	if not start_repetitive_kmers:
		if verbose:
			print "Estimating start of repetitive k-mers"
		start_repetitive_kmers = find_start_repeat_kmers(hist_dict)
	else:
		if verbose:
			print "User specified start of reptitive k-mers =" , start_repetitive_kmers

	if verbose:
		print "Start of repetitive k-mers" , start_repetitive_kmers

	total_number_kmers = sum((a * b) for (a, b) in hist_dict.items())
	if verbose:
		print "Total number of k-mers" , total_number_kmers

	number_repetitive_kmers = 0
	for (a, b) in hist_dict.items():
		if (a >= start_repetitive_kmers):
			number_repetitive_kmers += (a * b)

	if verbose:
		print "Number of repetitive k-mers" , number_repetitive_kmers

	return ((1.0 * number_repetitive_kmers) / total_number_kmers)


def create_parser():
	parser = custom_argument_parser.CustomParser()
	parser.add_argument("-v", "--verbose", action = "store_true")
	parser.add_argument("-c", "--cutoffs", type = int, nargs = '+')
	parser.add_argument("-f", "--file", type = str, nargs = '+', required = True)

	return parser


def parser_main():
	parser = create_parser()
	args = parser.parse_args()

	if args.cutoffs:
		if len(args.file) != len(args.cutoffs):
			print "ERROR: Need to have the same number of manual cutoffs as files"
			sys.exit(1)
	else:
		args.cutoffs = [0 for x in args.file]

	return args


if __name__ == "__main__":

	args = parser_main()

	manual_cutoffs = args.cutoffs
	file_paths = args.file
	verbose = args.verbose

	for (file_name, cutoff) in zip(file_paths, manual_cutoffs):
		with open(file_name, 'r') as f:
			print "Started processing" , file_name
			hist_dict = create_hist_dict(f)
			gri = calculate_gri(hist_dict, verbose, cutoff)
			print "GRI =" , gri
			print "Finished processing" , file_name

