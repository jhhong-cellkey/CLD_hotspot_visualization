# CHO Hotspot Genome Browser

This directory contains a local IGV.js-based genome browser for visualizing CHO
PICRH hotspot regions together with gene annotation, RNA expression, and ChIP-seq
signal tracks.

The main page is `index.html`. It loads local reference and track files from
`data/`, so it should be opened through the included Python server rather than
directly as a `file://` page.

## Quick Start

From this directory:

```bash
python serve_igv.py
```

Then open:

```text
http://127.0.0.1:8020/
```

Use Chrome or Firefox and hard-refresh with `Ctrl+Shift+R` after editing
`index.html`. The server disables HTML caching, but the browser can still keep an
old copy in some cases.

If port `8020` is already in use:

```bash
kill $(lsof -t -i :8020)
python serve_igv.py
```

## Directory Overview

```text
CLD_hotspot_visualization/
├── index.html
├── serve_igv.py
├── extract_hotspot_sequences.py
├── vendor/
│   └── igv.esm.min.js
└── data/
    ├── README.md
    ├── genome/
    │   ├── PICRH.fa -> reference FASTA symlink
    │   └── PICRH.fa.fai -> FASTA index symlink
    ├── tracks/
    │   ├── genomic.no_region.gff -> gene annotation symlink
    │   ├── hotspots.bed
    │   ├── hotspots.marker.bed
    │   ├── hotspots.viz.bed
    │   ├── Visualization_GSE19750_gene_tpm.bedGraph -> RNA TPM track symlink
    │   ├── RNAseq_mean_CPM.bw -> RNA coverage bigWig symlink
    │   ├── Tp5_H3K4me3.bw -> ChIP bigWig symlink
    │   ├── Tp5_H3K9me3.bw -> ChIP bigWig symlink
    │   └── Tp5_H3K27ac.bw -> ChIP bigWig symlink
    └── sequences/
```

Most large data files are not committed. They are local symlinks; see
`data/README.md` for example `ln -sfn` commands.

## Main Files

### `index.html`

The browser UI and most application logic live here.

It does four main things:

1. Creates an IGV.js browser using `vendor/igv.esm.min.js`.
2. Loads the CHO PICRH reference genome from `data/genome/PICRH.fa`.
3. Defines the visible tracks: gene annotation, hotspots, RNA, and ChIP-seq.
4. Adds custom popovers and a hotspot sequence panel below the browser.

Important settings:

- `fastaURL`: reference FASTA path, currently `data/genome/PICRH.fa`
- `faiURL`: FASTA index path, currently `data/genome/PICRH.fa.fai`
- `initialLocus`: initial visible locus,
  `NW_023276806.1:81476323-82076323`
- `hotspotFlankBp`: default flank size for hotspot sequence download,
  currently `300_000`
- `trackBackground`: shared light-gray track background color

### `serve_igv.py`

A small static file server for local IGV use.

IGV and browser-side sequence extraction need HTTP byte-range requests. A normal
direct file open does not support that, so this server:

- serves files from this directory
- supports `Range: bytes=...` requests for FASTA, bigWig, and other indexed files
- returns `206 Partial Content` when IGV requests only part of a large file
- disables caching for HTML pages so UI edits show up more reliably

Default address:

```text
http://127.0.0.1:8020/
```

Optional arguments:

```bash
python serve_igv.py --host 0.0.0.0 --port 8020 --directory .
```

### `extract_hotspot_sequences.py`

A command-line helper for extracting FASTA sequences around hotspots.

By default it reads:

- reference FASTA: `data/genome/PICRH.fa`
- FASTA index: `data/genome/PICRH.fa.fai`
- hotspot BED: `data/tracks/hotspots.bed`

It extracts `±300 kb` around each hotspot start coordinate and writes:

- one FASTA per hotspot under `data/sequences/hotspots/`
- one combined FASTA at `data/sequences/hotspots_all.fa`

Run:

```bash
python extract_hotspot_sequences.py
```

Example with a different flank size:

```bash
python extract_hotspot_sequences.py --flank-bp 100000
```

### `vendor/igv.esm.min.js`

The local IGV.js bundle imported by `index.html`.

Keeping it in `vendor/` means the browser can run without loading IGV from a CDN.

## Tracks Shown In The Browser

`index.html` defines seven explicit tracks. IGV also adds a reference sequence
track automatically from the FASTA reference, so the page can show eight visible
rows.

### 1. Reference Sequence

Automatically created by IGV from:

```text
data/genome/PICRH.fa
data/genome/PICRH.fa.fai
```

This is the coordinate and sequence reference used by every other track. When
zoomed in far enough, IGV can display the actual reference bases.

### 2. Gene Annotation

```text
data/tracks/genomic.no_region.gff
```

Type: `annotation`  
Format: `gff3`

This displays NCBI gene annotation. The gene popover is customized in
`buildGenePopover()` and currently shows selected fields such as:

- `Gene`
- `Genome location`
- `Feature type`
- `Gene biotype`
- `GenBank feature type`
- `Annotation provider`
- `GeneID`
- `Transcript ID`

GFF attribute names are normalized before display because IGV passes many GFF
attributes as names like `gene:` or `Dbxref:`.

### 3. Hotspots

```text
data/tracks/hotspots.marker.bed
```

Type: `annotation`  
Format: `bed`

This is the visual hotspot marker track. The current file uses center-based
markers that are `1000 bp` wide (`center ±500 bp`) so hotspots look like visible
vertical blocks rather than 1-bp points.

Clicking a hotspot also opens the custom hotspot sequence panel below the
browser.

### 4. RNA Expr (TPM, n=15)

```text
data/tracks/Visualization_GSE19750_gene_tpm.bedGraph
```

Type: `wig`  
Format: `bedgraph`

This is a gene-level RNA expression summary track. It is displayed as a bar graph
using mean TPM information generated from 15 RNA-seq samples.

### 5. RNA Coverage

```text
data/tracks/RNAseq_mean_CPM.bw
```

Type: `wig`  
Format: `bigwig`

This shows mean RNA-seq coverage/signal as a bigWig track.

### 6. H3K4me3

```text
data/tracks/Tp5_H3K4me3.bw
```

Type: `wig`  
Format: `bigwig`

ChIP-seq signal for H3K4me3.

### 7. H3K9me3

```text
data/tracks/Tp5_H3K9me3.bw
```

Type: `wig`  
Format: `bigwig`

ChIP-seq signal for H3K9me3.

### 8. H3K27ac

```text
data/tracks/Tp5_H3K27ac.bw
```

Type: `wig`  
Format: `bigwig`

ChIP-seq signal for H3K27ac.

## Hotspot Data Files

### `data/tracks/hotspots.bed`

The source hotspot intervals. These are the real hotspot regions used for:

- hotspot sequence preview
- hotspot TXT download region calculation
- resolving hotspot names to original coordinates

BED columns:

```text
chrom  start0  end0  name
```

`start0` is 0-based and `end0` is BED-style exclusive.

### `data/tracks/hotspots.marker.bed`

The display-only hotspot marker file used by the IGV Hotspots track.

It is intentionally wider than 1 bp so each hotspot is easy to see in the
browser. Changing the start/end columns here changes the visual width of the red
hotspot marker, but does not change the real hotspot coordinates used for
sequence preview or downloads.

### `data/tracks/hotspots.viz.bed`

An alternative widened visualization BED. It is not currently used by
`index.html`, but can be used if you want much wider visual hotspot regions.

## Hotspot Sequence Panel

When the user clicks a feature in the `Hotspots` track:

1. `showHotspotSequencePanel()` resolves the clicked hotspot name.
2. The real hotspot coordinates are loaded from `data/tracks/hotspots.bed`.
3. The panel below IGV displays the hotspot sequence.
4. The TXT download options panel can be opened.

The TXT download supports two scopes:

- `Hotspot only`: the real BED interval from `hotspots.bed`
- `Hotspot ± flank`: a user-selected kb flank around the hotspot start coordinate

Sequence loading is done in the browser through byte-range requests against
`PICRH.fa`, using `PICRH.fa.fai` to convert genomic coordinates into byte
offsets.

## Gene Information Popover

Gene popover content comes from the clicked GFF feature.

The GFF 9th column contains semicolon-separated attributes such as:

```text
ID=...;Dbxref=GeneID:...;Name=...;gbkey=...;gene=...;gene_biotype=...
```

IGV parses these attributes and passes them to `buildGenePopover()`. The current
code only displays selected fields and maps some labels:

- `Dbxref` is shown as `GeneID`
- values like `GeneID:103158549` are displayed as `103158549`
- `Source` is shown as `Annotation provider`
- `gbkey` is shown as `GenBank feature type`

If a field is missing from the clicked feature, it is skipped.

## Data Setup

Large data files are expected as local symlinks. The important ones are:

```text
data/genome/PICRH.fa
data/genome/PICRH.fa.fai
data/tracks/genomic.no_region.gff
data/tracks/Visualization_GSE19750_gene_tpm.bedGraph
data/tracks/RNAseq_mean_CPM.bw
data/tracks/Tp5_H3K4me3.bw
data/tracks/Tp5_H3K9me3.bw
data/tracks/Tp5_H3K27ac.bw
```

See `data/README.md` for example symlink commands.

## Common Edits

### Change The Initial Region

Edit:

```javascript
const initialLocus = "NW_023276806.1:81476323-82076323";
```

### Change Hotspot Download Flank

Edit:

```javascript
const hotspotFlankBp = 300_000;
```

### Change Hotspot Marker Width

Edit the start/end columns in:

```text
data/tracks/hotspots.marker.bed
```

The current marker width is `1000 bp`.

### Change Track Colors Or Heights

Edit the corresponding object in the `tracks` array inside `index.html`.

Examples:

- `color`
- `height`
- `featureHeight`
- `displayMode`

### Change Gene Popover Fields

Edit `geneVisibleFields` and `fieldLabelMap` in `index.html`.

## Notes

- Do not open `index.html` directly from the filesystem; use `serve_igv.py`.
- Use hard refresh after edits.
- The large reference, GFF, bigWig, and RNA expression files are local symlinks
  and are ignored by git.
- The `data/genome/cho_demo.fa` and small demo bedGraph files are older demo
  files kept in the folder but are not the current main data sources.
