
ratios=($(find ./data -name "*.bam_ratio.txt" -type f))
cnvs=($(find ./data -name "*.bam_CNVs_corrected.txt" -type f))
echo ${#ratios[@]}
echo ${#cnvs[@]}

for index in $(seq 0 $((${#ratios[@]}-1)))
do  
    echo "cat ./FREEC-11.6b/scripts/assess_significance.R | R --slave --args ${cnvs[$index]} ${ratios[$index]})"
    cat ./FREEC-11.6b/scripts/assess_significance.R | R --slave --args ${cnvs[$index]} ${ratios[$index]}
done