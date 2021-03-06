from collections import namedtuple
import pickle
import re
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import sys
import os
import glob

MyStruct = namedtuple("MyStruct", "roc auc threshold_plot filtered_mass epoch_losses name")
table_printed = np.zeros((15,10))

def plot_graph(data_sample, num_layers, lr_model):

	if data_sample!="all" and data_sample!="high_level" and data_sample!="low_level" and data_sample!="no_D2" and data_sample!="no_jet_mass":
		raise Exception('Illegal data_sample input!')

	with open ('./input data/%s_test_x' % data_sample, 'rb') as fp:
		test_x = pickle.load(fp)

	with open('./output_data/%d-layer %s data %s_lr' % (num_layers,data_sample, lr_model), 'rb') as fp:
		all_nodes = pickle.load(fp)

	with open('./input data/max_min_features', 'rb') as fp:
		temp = pickle.load(fp)
		min_features = temp[0]
		max_features = temp[1]

	divisions = 20

	n = len(all_nodes)

	highest_AUC = 0

	# bubble sort all nodes
	for i in range(n):
		for j in range(0,n-i-1):
			if all_nodes[j].auc > all_nodes[j+1].auc:
				all_nodes[j], all_nodes[j+1] = all_nodes[j+1], all_nodes[j]

	plt.figure(1)
	for i in range(n-1,0,-int(n/5)):
		roc = all_nodes[i].roc
		auc = all_nodes[i].auc
		if i == n-1:
			highest_AUC = auc
		roc_name = all_nodes[i].name
		plt.plot(roc[0],roc[1],label="%s, AUC = %f" % (roc_name,auc))
	plt.xlabel("Signal Efficiency")
	plt.ylabel("Background Rejection")
	plt.legend()
	plt.title("%d-layer ROC %s data %s_lr" % (num_layers,data_sample,lr_model))
	plt.savefig("./NN_results_visualizations/%s_data/%d-layer_ROC_%s_lr" % (data_sample,num_layers,lr_model))
	plt.close(1)

	plt.figure(2)
	for i in range(n-1,0,-int(n/5)):
		threshold_plot = all_nodes[i].threshold_plot
		roc_name = all_nodes[i].name
		plt.plot(threshold_plot[0],threshold_plot[1],label="%s" % (roc_name))
	plt.xlabel("Probability Threshold")
	plt.ylabel(r'$\frac{signal}{\sqrt{background+1}}$')
	plt.legend()
	plt.title("%d-layer Probability Threshold %s data %s_lr" % (num_layers,data_sample,lr_model))
	plt.savefig("./NN_results_visualizations/%s_data/%d-layer_Probability_Threshold_%s_lr" % (data_sample,num_layers,lr_model))
	plt.close(2)

	masses = []
	mass_index = -1
	if data_sample == "all":
		mass_index = 3
	if data_sample == "high_level":
		mass_index = 0
	if data_sample == "no_D2":
		mass_index = 3

	num_bins = 100
	for i in range (len(test_x)):
		masses.append((test_x[i][mass_index]*(max_features[3]-min_features[3])+min_features[3])/1000)

	plt.figure(3)
	max_ratio = -1
	max_index = -1
	for i in range (len(all_nodes[n-1].threshold_plot[1])):
		if all_nodes[n-1].threshold_plot[1][i] > max_ratio:
			max_ratio = all_nodes[n-1].threshold_plot[1][i]
			max_index = i
	roc_name = all_nodes[n-1].name
	plt.hist(masses, num_bins, histtype='step', label = "Unfiltered", stacked = True, density = 1)
	plt.hist(all_nodes[n-1].filtered_mass[max_index], num_bins, histtype='step', label="%s Filtered" % roc_name, stacked = True, density = 1)
	plt.xlabel("Mass of Highest Pt Jet [GeV]")
	plt.legend(loc = "upper right")
	plt.title("Filtered Jet Mass %s data, Threshold = %f, %s_lr" % (data_sample, max_index/divisions,lr_model))
	plt.savefig("./NN_results_visualizations/%s_data/%d-layer_Filtered_Jet_Mass_%s_lr" % (data_sample,num_layers,lr_model))
	plt.close(3)

	plt.figure(4)
	plt.hist(masses, num_bins, facecolor='blue', alpha=0.5, density = 1)
	plt.xlabel("Mass of Highest Pt Jet [GeV]")
	plt.title("Unfiltered Jet Mass %s data" % data_sample)
	plt.savefig("./NN_results_visualizations/Unfiltered_Jet_Mass_%s" % data_sample)
	plt.close(4)

	plt.figure(5)
	plt.plot(all_nodes[n-1].epoch_losses,label="%s" % roc_name)
	plt.xlabel("Epochs")
	plt.ylabel("Loss")
	plt.legend()
	plt.title("%d-layer Loss %s data %s_lr" % (num_layers,data_sample,lr_model))
	plt.savefig("./NN_results_visualizations/%s_data/%d-layer_Loss_%s_lr" % (data_sample,num_layers,lr_model))
	plt.close(5)

	f = open("./NN_results_visualizations/%d-layer_%s_data_summary" %(num_layers, data_sample),"a")
	# f.write("%d-layer %s data %s_lr\n" % (num_layers, data_sample, lr_model))
	# f.write("Highest AUC, Highest signal over background ratio and Number of Epochs till Convergence\n")
	length = len(all_nodes[n-1].epoch_losses)
	f.write("%s & %.3f & %3.1f & %3.1f & %d" % (lr_model, auc, max_ratio, all_nodes[n-1].epoch_losses[length-1],length))
	f.write(r'\\')
	f.write("\n \hline\n")
	f.close()
	table_printed[int(num_layers)][data_sample_index]+=1

if __name__ == '__main__':

	path = './output_data'

	for filename in glob.glob(os.path.join(path, '*lr')):
		# do your stuff
		# print("filename = ", filename)
		filename = re.split("/",filename)[2]
		num_layers = re.split("-",filename)[0]
		# print("num_layers = ", num_layers)
		data_sample = re.split(" ",filename)[1]
		# print("data_sample = ", data_sample)
		lr_model = re.split("_",re.split(" ",filename)[3])[0]
		# print("lr_model = ", lr_model)
		data_sample_index = np.where(data_sample == "all", 0, np.where(data_sample == "no_D2", 1, 2))

		if table_printed[int(num_layers)][data_sample_index] == 0:
			f = open("./NN_results_visualizations/%d-layer_%s_data_summary" %(int(num_layers), data_sample),"a")
			f.write(r'\begin{table}[H]')
			f.write("\n")
			f.write("\centering")
			f.write("\n")
			f.write(r'\begin{tabular}{|p{1.4cm}|p{1.2cm}|p{2.2cm}|p{1.5cm}|p{1.2cm}|}')
			f.write("\n")
			f.write("\hline")
			f.write("\n")
			f.write(r'Learning Rate& Highest AUC & $\frac{Signal}{\sqrt{Background+1}}$ & Converged Loss & Number of Epochs\\ [0.5ex]')
			f.write("\n")
			f.write(r'\hline\hline')
			f.write("\n")
			f.close()
		plot_graph(data_sample, int(num_layers),lr_model)
		if table_printed[int(num_layers)][data_sample_index] == 5:
			f = open("./NN_results_visualizations/%d-layer_%s_data_summary" %(int(num_layers), data_sample),"a")
			f.write(r'\end{tabular}')
			f.write("\n")
			f.write("\caption{%d-layer Neural Net, %s features}\n"%(int(num_layers), data_sample))
			f.write("\label{%d-layer_%s_features_table}\n"%(int(num_layers), data_sample))
			f.write(r"\end{table}")
			f.close()



