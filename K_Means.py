import random
import numpy as np

def compute_distance(vec1, vec2):
    return np.sqrt(np.sum(np.square(vec1 - vec2)))
    
def compute_distances(A, B):
    m = np.shape(A)[0]
    n = np.shape(B)[0]
    M = np.dot(A, B.T)
    H = np.tile(np.matrix(np.square(A).sum(axis=1)).T,(1,n))
    K = np.tile(np.matrix(np.square(B).sum(axis=1)),(m,1))
    return np.sqrt(-2 * M + H + K + 1e-12)

class K_Means(object):
    def __init__(self, k, tolerance, max_iter):
        self.k = k
        self.max_iter  = max_iter
        self.tolerance = tolerance
        
        self.centers = []

    def fit(self, data):
        sample_centers = random.sample(data.tolist(), self.k)
        self.centers   = np.array(sample_centers)

        for i in range(self.max_iter):
            dists = compute_distances(data, self.centers)
            min_indexs = np.argmin(dists, axis=1)

            tmp_cls = [[] for i in range(self.k)]
            for idx, index in enumerate(min_indexs.tolist()):
                tmp_cls[index[0]].append(data[idx])
            
            optimized = True
            tmp_cls = np.array(tmp_cls)
            for idx in range(self.k):
                tmp_cls[idx] = np.average(tmp_cls[idx], axis=0)
                if(compute_distance(tmp_cls[idx], self.centers[idx]) > self.tolerance):
                    optimized = False
                self.centers[idx] = tmp_cls[idx]
            
            if(optimized):
                break
    
    def predict(self, vec):
        dists = compute_distances(vec, self.centers)
        min_indexs = np.argmin(dists, axis=1).tolist()
        return min_indexs

if __name__ == "__main__":
    K_means = K_Means(5, 0.1, 100)
    
    data = np.random.rand(100, 16) 

    K_means.fit(data)
    
    pre_data = np.random.rand(1, 16)

    print(K_means.predict(pre_data))
