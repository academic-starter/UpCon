proxy=$1
left=$2
right=$3


ROOT_DIR=$(git rev-parse --show-toplevel)
rm -rf $ROOT_DIR/usccheck/gumtree/left
rm -rf $ROOT_DIR/usccheck/gumtree/right


cp -rf $ROOT_DIR/usccheck/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/$proxy/implementation/$left $ROOT_DIR/usccheck/gumtree/left
for file in $(ls $ROOT_DIR/usccheck/gumtree/left);
do
    f="$(basename -- $file)"
    id=$(cut -d- -f2 <<< ${f})
    echo $id
    cp $ROOT_DIR/usccheck/gumtree/left/$file  $ROOT_DIR/usccheck/gumtree/left/$id 
done 

cp -rf $ROOT_DIR/usccheck/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/$proxy/implementation/$right $ROOT_DIR/usccheck/gumtree/right

for file in $(ls $ROOT_DIR/usccheck/gumtree/right);
do
    f="$(basename -- $file)"
    id=$(cut -d- -f2 <<< ${f})
    echo $id
    cp $ROOT_DIR/usccheck/gumtree/right/$file  $ROOT_DIR/usccheck/gumtree/right/$id 
done 
sudo docker pull gumtreediff/gumtree
sudo docker run --rm -v $ROOT_DIR/usccheck/gumtree/left:/diff/left -v $ROOT_DIR/usccheck/gumtree/right:/diff/right -p 4567:4567 gumtreediff/gumtree webdiff left/ right/