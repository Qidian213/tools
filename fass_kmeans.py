###
### conda install -c pytorch faiss-gpu
###

import os
import faiss
import numpy as np
import shutil

ncentroids = 500   ## 聚类类别
feat_dim   = 1024  ## 特证维度
niter      = 2432  ## 迭代次数
dist_th    = 0.5   ## 最近邻阈值
topk       = 200   ## 最近邻个数
min_topk   = 30    ## 最少最近邻数

### data
src_dir = '/data/Dataset/LargeFineFoodAI/Retrieval/'
dst_dir = '/data/Dataset/LargeFineFoodAI/Retrieval/culster/'

query_feats = np.load('/data/zzg/Classificaction/Image_Classification/features/qf.npy')
query_names = np.load('/data/zzg/Classificaction/Image_Classification/features/query_path_1.npy')

gallery_feats = np.load('/data/zzg/Classificaction/Image_Classification/features/gf.npy')
gallery_names = np.load('/data/zzg/Classificaction/Image_Classification/features/gallery_path_1.npy')

query_names   = ['query_private/'+name.replace('.jpg', '') for name in query_names]
gallery_names = ['gallery/'+name.replace('.jpg', '') for name in gallery_names]

xb_names = query_names + gallery_names
xb_feats = np.vstack((query_feats, gallery_feats))

### K-means
kmeans = faiss.Kmeans(feat_dim, ncentroids, niter=niter, verbose=True, gpu=True)
kmeans.train(xb_feats)

### Index
index = faiss.IndexFlatL2(feat_dim)   # build the index
index.add(xb_feats) 

### Search
D_Res, I_Res = index.search(kmeans.centroids, topk)

cls_num = [0]*ncentroids
for idx, (c_res, d_res) in enumerate(zip(I_Res, D_Res)):
    print(f"{idx}/{ncentroids}")
    
    idx_dir = dst_dir + str(idx+1000) + '/'

    if not os.path.exists(idx_dir):
        os.makedirs(idx_dir)

    for cl, cd in zip(c_res, d_res):
        if(cd < dist_th):
            cls_num[idx] += 1
            src_path = src_dir + xb_names[cl] + '.jpg'
            dst_path = idx_dir + xb_names[cl].split('/')[-1] + '.jpg'
            shutil.copyfile(src_path, dst_path)
            
    if(cls_num[idx] <min_topk):
        for cl, cd in zip(c_res, d_res):
            cls_num[idx] += 1
            src_path = src_dir + xb_names[cl] + '.jpg'
            dst_path = idx_dir + xb_names[cl].split('/')[-1] + '.jpg'
            shutil.copyfile(src_path, dst_path)
print(cls_num)

