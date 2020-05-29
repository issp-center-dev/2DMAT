# TRHEPD_to_DFT

## Installation

You need **Atomic Simulation Environment (ASE)** package (https://wiki.fysik.dtu.dk/ase). Please install it first according to the description in the ASE web site.

## Usage
Edit the top part of **trhepd_to_dft.py**:
```
calculation='relax' # 'scf','realx','bands',...
ecutwfc=20.0        # Cut-off energy in Ry
kpts=(3,3,1)        # sampling k points (Monkhorst-Pack grid)
nbands=33           # # of bands (only used in band structure calc
pseudo_dir='./'     # Pseudopotential directory
pseudopotentials={ 'Si': 'Si.pbe-mt_fhi.UPF',
                   'H' : 'H.pbe-mt_fhi.UPF' }
```
where you see the parameters for Quantum Espresso calculations.  
Then run the script with a xyz file which includes the 2D-periodic cell information at the last two lines.
```
$ python3 trhepd_to_dft.py abc.xyz
```

## Input file
```
abc.xyz       (XYZ file including the 2D-periodic cell information)
```

## Outpuf files
```
abc_ext.xyz   (Extended-XYZ file format)
abc.cif       (Crystallographic Information File format)
espresso.pwi  (Input file for Qunatunm Espresso calculation)
```

## 説明書：

アドバンスソフト社(担当：岩田様)による報告書「第一原理計算による実験解析の高精度化支援作業報告書」(2020年1月31日)

```
doc/Report_by_AdvanceSoft_20200131.pdf (PDFファイル)
doc/Report_by_AdvanceSoft_20200131.docx (Wordファイル．内容はPDFファイルと同じ）
```

## データファイル：

アドバンスソフト社(担当：岩田様)提供のデータファイルを, sample/ディレクトリに保管した．

QuantumEspressoの出力ファイルまで含めたデータ(2020年2月13日, 300MB)は，　下記にアップロードした．
```
TRHEPDtoDFT_data_20200128.tgz
https://drive.google.com/file/d/1OpsqAVlOcMlDw9SZjPl8MEpkVC1jFxaA/view?usp=sharing
```
