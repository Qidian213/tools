import os
import multiprocessing as mp
import threading

def sub_processor(lock, pid, video_list):
    result_dict[key] = val

if __name__ == '__main__':
    thread_num = 6
    
    global result_dict
    result_dict = mp.Manager().dict()
    
    processes = []
    lock = threading.Lock()
    
    for i in range(thread_num):
        if i == thread_num - 1:
            sub_video_list = video_list[i * per_thread_video_num:]
        else:
            sub_video_list = video_list[i * per_thread_video_num: (i + 1) * per_thread_video_num]
        p = mp.Process(target=sub_processor, args=(lock, i, sub_video_list))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
