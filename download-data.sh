mkdir -p /workspace/datasets/esci
cd /workspace/datasets/esci

echo "Cloning https://github.com/shuttie/esci-s.git to /workspace/datasets/esci"
# Git the original files for ESCI
git clone https://github.com/amazon-science/esci-data.git
# Git the ESCI data with metadata, as it is much more interesting
echo "Cloning the extended data for ESCI"
git clone https://github.com/shuttie/esci-s.git
echo "Downloading and unpacking the actual ESCI data.  This may take some time, but you should only have to do it once."
wget https://esci-s.s3.amazonaws.com/esci.json.zst
echo "Decompressing esci.json.zst"
zstd -d esci.json.zst
echo "Splitting esci.json"
split -l 100000  esci.json esci.json.split.

echo "Cleaning up"
rm esci.json.zst