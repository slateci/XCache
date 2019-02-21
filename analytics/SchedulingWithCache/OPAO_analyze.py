# Analyze OPAO emulation results

from os import makedirs

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import OPAO_utils as ou

matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('ytick', labelsize=14)

# TITLE = 'All_2_2L_Cache'
TITLE = 'All_99_2L_Cache'
TITLE = 'Prod_99_2L_Cache'
TITLE = 'Prod_fill_99_2L_Cache'
TITLE = 'All_fill_99_2L_Cache'
TITLE = 'All_fill_2_2L_Cache'

BASE_DIR = 'analytics/SchedulingWithCache/'
SAVE_FIGURES = True

INPUT_FILE = BASE_DIR + 'results/' + TITLE + '.h5'
OUTPUT_DIR = BASE_DIR + 'plots/' + TITLE + '/'

try:
    makedirs(BASE_DIR + 'plots/' + TITLE + '/sites')
except:
    pass

KEYS = pd.HDFStore(INPUT_FILE, 'r').keys()
# print('all keys in input h5:\n',KEYS)

# original task data
data = ou.load_data()
print('********** TASKS *******\n', data.shape[0])
# print(data.describe())


# load computing statistics
COMPUTE = pd.read_hdf(INPUT_FILE, key='compute', mode='r')
print('********** COMPUTE *******\n')
print(COMPUTE.head())
# print(COMPUTE.describe())

# load summary numbers
SUMMARY = pd.read_hdf(INPUT_FILE, key='summary', mode='r')
print('********** SUMMARY *******\n', SUMMARY)
# print(SUMMARY.describe())

# load emulated task finish times
tft = pd.read_hdf(INPUT_FILE, key='tft', mode='r')
print('********** EMULATED TASKS *******\n', data.shape[0])
# print(tft.describe())

complete = data.join(tft, on='taskid', how='inner')
complete['TTC'] = complete.finished_at - complete.created_at
complete['model_TTC'] = complete.model_finish - complete.created_at
complete['improvement'] = complete.model_TTC / complete.TTC


complete.drop(['dataset'], inplace=True, axis=1)
# print(complete.head())


def tasks_stats():
    fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(10, 9))
    fig.suptitle('Tasks stats\n' + TITLE.replace('_', ' '), fontsize=18)

    complete['acores'] = complete.Scores / complete.jobs

    ax1.hist(complete.acores, bins=range(0, 65, 1), log=True)
    ax1.set_ylabel('jobs')
    ax1.set_xlabel('actual cores')
    if SAVE_FIGURES:
        fig.savefig(OUTPUT_DIR + 'tasks_stats.png')
    plt.close(fig)


def plot_compute():
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(10, 9))
    fig.suptitle('Grid\n' + TITLE.replace('_', ' '), fontsize=18)

    ax1.plot(COMPUTE.index, COMPUTE.running, 'b')
    ax1.set_ylabel('jobs running', color='b')
    ax1.set_xlabel('time')
    # ax1.legend()

    ax11 = ax1.twinx()
    ax11.plot(COMPUTE.index, COMPUTE.queued, 'r')
    ax11.set_ylabel('jobs queued', color='r')

    # textstr = "core hours used:" + str(self.core_seconds // 3600)
    # textstr += "\njob queue hours:" + str(self.queue_seconds // 3600)
    # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    # ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=props)

    ax2.plot(COMPUTE.index, COMPUTE.finished, 'b')
    ax2.plot(COMPUTE.index, COMPUTE['cores used'], 'r')

    ax2.set_ylabel('[%]')
    ax2.set_xlabel('time')
    ax2.legend()

    fig.autofmt_xdate()
    fig.subplots_adjust(hspace=0)

    # plt.tight_layout()
    if SAVE_FIGURES:
        fig.savefig(OUTPUT_DIR + 'compute.png')
    plt.close(fig)


def plot_ttc():

    # print(complete.describe())

    fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(10, 9))
    fig.suptitle('Jobs stats\n' + TITLE.replace('_', ' '), fontsize=18)

    bs = []
    for b in range(20):
        bs.append(60 * pow(2, b))
    ax1.hist([complete.TTC, complete.model_TTC], bins=bs, label=['orig.', 'emulation'], histtype='step')
    ax1.set_ylabel('tasks')
    ax1.set_xlabel('TTC [s]')

    ax1.set_yscale("log", nonposy='clip')
    ax1.set_xscale("log", nonposy='clip')
    ax1.legend()

    orig = complete.TTC.mean()
    emul = complete.model_TTC.mean()
    print('orig:', orig)
    print('emulation:', emul)
    print('orig/emulation', orig / emul)
    textstr = "Avg. TTC [h]\nOriginal:" + str(orig // 3600)
    textstr += "\nEmulation:" + str(emul // 3600)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=12, verticalalignment='top', bbox=props)

    # plt.tight_layout()

    if SAVE_FIGURES:
        fig.savefig(OUTPUT_DIR + 'TTC_1.png')
    plt.close(fig)
    bs = []
    for b in range(29):
        bs.append(0.0001 * pow(2, b))
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 9))
    fig.suptitle('TTC\n' + TITLE.replace('_', ' '), fontsize=18)
    ax.set_yscale("log", nonposy='clip')
    ax.set_xscale("log", nonposy='clip')
    complete.hist('improvement', bins=bs, ax=ax)
    if SAVE_FIGURES:
        fig.savefig(OUTPUT_DIR + 'TTC.png')
    plt.close(fig)


def plot_ce_stats():
    for key in KEYS:
        if not key.startswith('/compute-'):
            continue
        ce_name = key.replace('/compute-', '')
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=False, figsize=(8, 9))
        fig.suptitle(ce_name + '\n' + TITLE.replace('_', ' '), fontsize=18)

        stats = pd.read_hdf(INPUT_FILE, key=key, mode='r')

        ax1.plot(stats.index, stats.running)
        ax1.plot(stats.index, stats.queued)
        ax1.set_ylabel('jobs')
        ax1.legend()

        ax2.plot(stats.index, stats.finished)
        ax2.set_ylabel('finished')
        ax2.set_xlabel('time')
        # ax2.legend()

        ax3.plot(stats.index, stats.cores_used)
        ax3.set_ylabel('cores used')
        ax3.set_xlabel('time')
        # ax3.legend()

        fig.autofmt_xdate()
        fig.subplots_adjust(hspace=0)

        if SAVE_FIGURES:
            fig.savefig(OUTPUT_DIR + 'sites/' + ce_name + '.png')
        plt.close(fig)


def plot_storage():

    accdf = pd.read_hdf(INPUT_FILE, key='file_accesses', mode='r')
    dacdf = pd.read_hdf(INPUT_FILE, key='data_accessed', mode='r')

    if not CLOUD_LEVEL_CACHE:
        accdf.drop('Cloud caches', axis=1, inplace=True)
        dacdf.drop('Cloud caches', axis=1, inplace=True)

    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 10), sharex=True,)
    fig.suptitle('Cache levels\n' + TITLE.replace("_", " "), fontsize=18)

    accdf.plot(ax=axs[0][0])
    axs[0][0].set_ylabel('hits')
    axs[0][0].set_xlabel('time')
    axs[0][0].legend()

    dacdf.plot(ax=axs[1][0])
    axs[1][0].set_ylabel('data delivered [TB]')
    axs[1][0].set_xlabel('time')
    axs[1][0].legend()

    accdf = accdf.div(accdf.sum(axis=1), axis=0)
    dacdf = dacdf.div(dacdf.sum(axis=1), axis=0)

    accdf.plot(ax=axs[0][1])
    axs[0][1].set_ylabel('hits [%]')
    axs[0][1].set_xlabel('time')
    axs[0][1].grid(axis='y')
    axs[0][1].legend()

    dacdf.plot(ax=axs[1][1])
    axs[1][1].set_ylabel('data delivered [%]')
    axs[1][1].set_xlabel('time')
    axs[1][1].grid(axis='y')
    axs[1][1].legend()

    # plt.show()

    fig.autofmt_xdate()
    fig.subplots_adjust(hspace=0)
    if SAVE_FIGURES:
        fig.savefig(OUTPUT_DIR + 'storage.png')
    plt.close(fig)


def plot_storage_throughput():
    for key in KEYS:
        if not key.startswith('/cache-'):
            continue
        cache_name = key.replace('/cache-', '')

        df = pd.read_hdf(INPUT_FILE, key=key, mode='r')

        fig, ax = plt.subplots(figsize=(18, 6))
        fig.suptitle(cache_name + '\n' + TITLE.replace("_", " "), fontsize=18)
        fig.autofmt_xdate()
        ax.set_ylabel('throughput [Gbps]')
        df.plot(kind='line', ax=ax)
        if SAVE_FIGURES:
            fig.savefig(OUTPUT_DIR + 'sites/' + cache_name + '-thr.png')
        plt.close(fig)


if __name__ == "__main__":
    plot_compute()
    plot_ttc()
    # plot_storage()

    # plot_storage_throughput()
    plot_ce_stats()
