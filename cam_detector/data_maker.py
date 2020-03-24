
"""
DeWiCam explores four ﬁelds (length, duration, FC and Address)

Problems
- How should I get FC from Ethernet packets?
- Duration values are too big. Did I parse it correctly?

Process
1. Sort SRC, DST addresses
2. Get 4 vectors
"""

import pickle
from scipy.stats import norm, ks_2samp

from pkl_maker import read_pkl
from scipy.stats import ks_2samp
from utils import get_pld_stability


MIN_DATA_SIZE = 300


def get_cdf1(data):
    hist, bin_edges = np.histogram(data, bins=len(data), density=True)
    cdf = np.cumsum(hist*np.diff(bin_edges))
    return cdf


def get_cdf2(data):
    sorted_data = np.sort(data)
    cdf = np.arange(len(sorted_data))/float(len(sorted_data)-1)
    return cdf


def get_cdf3(data):
    data_size=len(data)

    # Set bins edges
    data_set=sorted(set(data))
    bins=np.append(data_set, data_set[-1]+1)

    # Use the histogram function to bin the data
    counts, bin_edges = np.histogram(data, bins=bins, density=False)
    counts=counts.astype(float)/data_size

    # Find the cdf
    cdf = np.cumsum(counts)
    return cdf


def get_pld(data, split_num=50):
    block_num = (len(data)+(split_num//2)) // split_num
    if block_num <= 1:
        raise ValueError('The number of blocks must be greater than 1')

    for i in range(block_num):
        data_clip = data[i*split_num:(i+1)*split_num]

        print(get_cdf1(data_clip))
        print(get_cdf2(data_clip))
        print(get_cdf3(data_clip))
        input()


def get_bandwidth_std(data):
    bandwidth_list = []
    for time_delta, length in data[1:]:
        bps = (1./time_delta)*(length/1024*8)
        bandwidth_list.append(bps)

    return np.std(bandwidth_list)


def get_duration_std(data):
    return np.std(data)


def get_duration_avg(data):
    return np.mean(data)


def get_length_sum(data):
    return sum(data)


def get_pld_stb(data, split_num=50):
    block_num = (len(data)+(split_num//2)) // split_num
    if block_num <= 1:
        raise ValueError('The number of block must be over 1')

    cum_s = 0
    l1 = data[:split_num]
    for j in range(1, block_num):
        lj = data[j*split_num:(j+1)*split_num]
        cum_s += ks_2samp(l1, lj).statistic

    stb = cum_s/(block_num-1)
    return stb


    print('packet num:', len(data))

    length_list = [d['length'] for d in data]
    # pld = get_pld(length_list, split_num=50)
    pld_stb = get_pld_stb(length_list, split_num=50)
    length_sum = get_length_sum(length_list)

    print()
    input()
    duration_list = [d['duration'] for d in data]
    duration_std = get_duration_std(duration_list)
    duration_avg = get_duration_avg(duration_list)

    bandwidth_list = [(d['time_delta'], d['length']) for d in data]
    bandwidth_std = get_bandwidth_std(bandwidth_list)


def make_data_list(path_list) -> list:
    data_list = []
    for path in path_list:
        with open(path, 'rb') as fp:
            flows = pickle.load(fp)

        for src, src_value in flows.items():
            for dst, dst_value in src_value.items():
                for fc, data in dst_value.items():
                    if len(data) < MIN_DATA_SIZE:
                        continue

                    for i in range(0, len(data), MIN_DATA_SIZE//2):
                        vector = get_vector(data[i:i+MIN_DATA_SIZE])
                        data_list.append(vector)

    return data_list

if __name__ == '__main__':
    with open('pos_paths.txt', 'r') as f:
        pos_path_list = f.read().splitlines()
    pos_data_list = make_data_list(pos_path_list)

    # with open('neg_paths.txt', 'r') as f:
    #     neg_path_list = f.read().splitlines()
    # neg_data_list = make_data_list(neg_path_list)