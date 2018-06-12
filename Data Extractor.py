import json
import urllib3
from os import system, makedirs
from os.path import exists
from chardet import detect
from multiprocessing import Pool, Manager

path = "C:/Users/t-vimeh/Pictures/GSoC/top500domains.csv"
dir_path = "C:/Users/t-vimeh/Pictures/GSoC/SnapShots/"

http = urllib3.PoolManager()

def auto_decode(data):
    if type(data) == str:
        return data
    print(detect(data))
    return data.decode(detect(data)['encoding'])


def read_file(path):
    with open(path) as f:
        read_data = f.read()
    return auto_decode(read_data)


def write_to_file(path, data):
    with open(path, 'w', encoding = 'utf-8') as f:
        return f.write(data)


def get_snapshot_timestamps(url, date_range = ['2008', '2018'], num_snapshots = 20):
    url_of_snapshots = 'http://web.archive.org/cdx/search/cdx?url=' + url + \
                       '&from=' + date_range[0] + '&to=' + date_range[1]
    r = http.request('GET', url_of_snapshots)
    lst_snapshots_temp = auto_decode(r.data).strip().split('\n')
    num_snapshots = min([num_snapshots, len(lst_snapshots_temp)])
    increment = len(lst_snapshots_temp)//num_snapshots
    lst_timestamps = []
    for i in range(0, len(lst_snapshots_temp), increment):
        lst_timestamps.append(lst_snapshots_temp[i].split()[1][:8])
    return lst_timestamps


def get_snapshots(url, lst_timestamps = None):
    if not lst_timestamps:
        lst_timestamps = [str(i) for i in range(2018, 1998, -1)]
    lst_snapshots = []
    set_of_timestamps = set([])
    for timestamp in lst_timestamps:
        url_of_snapshot_meta_data = 'http://archive.org/wayback/available?url=' + \
                          url + '&timestamp=' + timestamp
        r = http.request('GET', url_of_snapshot_meta_data)
        dic = json.loads(r.data.strip())
        if dic['archived_snapshots'] == {}:
            continue
        url_of_snapshot = dic['archived_snapshots']['closest']['url']
        if dic['archived_snapshots']['closest']['timestamp'] in set_of_timestamps:
            continue
        set_of_timestamps.add(dic['archived_snapshots']['closest']['timestamp'])
        r = http.request('GET', url_of_snapshot)
        lst_snapshots.append((timestamp, auto_decode(r.data).strip()))
    return lst_snapshots


def save_snapshots(lst_snapshots, url):
    if not exists(dir_path + url):
        makedirs(dir_path + url)
    for snapshot in lst_snapshots:
        path = dir_path + url + '/' + snapshot[0] + '.html'
        write_to_file(path, snapshot[1])


lst_urls = read_file(path).split('\n')
cnt = 1
for url in lst_urls:
    try:
        #lst_timestamps = get_snapshot_timestamps(url)
        lst_snapshots = get_snapshots(url, lst_timestamps = None)
        print('URL number: ' + str(cnt) + ', URL: ' + url)
        print("...Saving " + str(len(lst_snapshots)) + " snapshots of " + url + "...")
        save_snapshots(lst_snapshots, url)
        print("...Finished saving snapshots of " + url + "!")
        cnt += 1
    except Exception as e:
        print("Some error occured...: " + str(e))
        continue
    

