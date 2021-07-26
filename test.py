from IPython import embed

from rlxnix.dataset import Dataset

if __name__ == "__main__":
    test_file = "data/2018-09-06-ai-invivo-1.nix"
    test_file2 = "data/2021-07-08-ad-invivo-1.nix"
    
    d = Dataset(test_file2)
    embed()
    d.close()
    