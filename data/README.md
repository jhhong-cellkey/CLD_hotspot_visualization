# Data setup

Track and genome files are not stored in git. Create symlinks locally, for example:

```bash
# genome
ln -sfn /nvme2/hotspot/reference/GCF_003668045.3/GCF_003668045.3_CriGri-PICRH-1.0_genomic.fna data/genome/PICRH.fa
ln -sfn /nvme2/hotspot/reference/GCF_003668045.3/GCF_003668045.3_CriGri-PICRH-1.0_genomic.fna.fai data/genome/PICRH.fa.fai

# annotation
ln -sfn /nvme2/hotspot/reference/GCF_003668045.3/genomic.gff data/tracks/genomic.gff

# RNA / ChIP tracks
ln -sfn /nvme1/hotspot/RNA_expr/GSE19750_all_samples.bed data/tracks/GSE19750_all_samples.bed
ln -sfn /nvme1/hotspot/ChIP_seq/final_chipseq2/macs3_peaks/Tp5/H3K4me3/Tp5_H3K4me3_BSF_0128_C5HP5ACXX_7_Library_E_1_5_H3K4me3_Tp5.PICRH.sorted_FE.bw data/tracks/Tp5_H3K4me3.bw
ln -sfn /nvme1/hotspot/ChIP_seq/final_chipseq2/macs3_peaks/Tp5/H3K9me3/Tp5_H3K9me3_BSF_0128_C5HP5ACXX_7_Library_E_1_2_H3K9me3_Tp5.PICRH.sorted_FE.bw data/tracks/Tp5_H3K9me3.bw
ln -sfn /nvme1/hotspot/ChIP_seq/final_chipseq2/macs3_peaks/Tp5/H3K27ac/Tp5_H3K27ac_BSF_0116_C55NLACXX_2_Library_E_1_6_H3K27ac_Tp5.PICRH.sorted_FE.bw data/tracks/Tp5_H3K27ac.bw
```

## Hotspot sequence extraction (±300 kb)

```bash
python extract_hotspot_sequences.py
```

Reads `data/tracks/hotspots.bed`, extracts ±300 kb around each hotspot start from `data/genome/PICRH.fa`, and writes:

- `data/sequences/hotspots/Hotspot_1.fa` (per hotspot)
- `data/sequences/hotspots_all.fa` (combined)
