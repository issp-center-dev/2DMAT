はじめに
================================

2DMATとは
--------------------------------

2DMATは、順問題ソルバーに対して探索アルゴリズムを適用して最適解を探すためのフレームワークです。
順問題ソルバーはユーザー自身で定義できるほか、標準的な順問題ソルバーとして2次元物質構造解析向け実験データ解析ソフトウェアが用意されています。
順問題ソルバーでは、原子位置などをパラメータとし得られたデータと実験データとのずれを損失関数として与えます。
探索アルゴリズムによりこの損失関数を最小化する最適なパラメータを推定します。
現バージョンでは、順問題ソルバーとして量子ビーム回折実験の全反射高速陽電子回折実験(Total-Reflection High-Energy Positron Diffraction: TRHEPD), 表面X線回折法(Surface X-ray Diffraction: SXRD), 低速電子線回折法(Low Energy Electron Diffraction: LEED)に対応しており、
探索アルゴリズムはNelder-Mead法, グリッド型探索法, ベイズ最適化, レプリカ交換モンテカルロ法, ポピュレーションアニーリングモンテカルロ法が実装されています。

2DMAT-LEEDとは
--------------------------------

``SATLEED`` は M.A. Van Hove氏により作成された LEED の解析を行うプログラムで、原子位置などから Rocking curve を計算し、実験で得られた Rocking curve からの誤差を求めます。2DMAT-LEED は、この SATLEED を 2DMAT の順問題ソルバーとして利用するためのアダプタライブラリです。2DMAT v2.x の順問題ソルバーの一つとして開発されたコンポーネントを、独立なモジュールとして再構成したものです。2DMAT および SATLEED と組み合わせて使用します。
``SATLEED`` に関する詳細については [SATLEED]_ をご覧ください。

.. [SATLEED] M.A. Van Hove, W. Moritz, H. Over, P.J. Rous, A. Wander, A. Barbieri, N. Materer, U. Starke, G.A. Somorjai, Automated determination of complex surface structures by LEED, Surface Science Reports, Volume 19, 191-229 (1993). https://doi.org/10.1016/0167-5729(93)90011-D


ライセンス
--------------------------------
| 本ソフトウェアのプログラムパッケージおよびソースコード一式はGNU
  General Public License version 3（GPL v3）に準じて配布されています。

Copyright (c) <2020-> The University of Tokyo. All rights reserved.

本ソフトウェアは2020年度 東京大学物性研究所 ソフトウェア高度化プロジェクトの支援を受け開発されました。
2DMATを引用する際には以下の文献を引用してください。

"Data-analysis software framework 2DMAT and its application to experimental measurements for two-dimensional material structures",
Y. Motoyama, K. Yoshimi, I. Mochizuki, H. Iwamoto, H. Ichinose, and T. Hoshi, Computer Physics Communications 280, 108465 (2022).

Bibtex:

| @article{MOTOYAMA2022108465,
|   title = {Data-analysis software framework 2DMAT and its application to experimental measurements for two-dimensional material structures},
|   journal = {Computer Physics Communications},
|   volume = {280},
|   pages = {108465},
|   year = {2022},
|   issn = {0010-4655},
|   doi = {https://doi.org/10.1016/j.cpc.2022.108465},
|   url = {https://www.sciencedirect.com/science/article/pii/S0010465522001849},
|   author = {Yuichi Motoyama and Kazuyoshi Yoshimi and Izumi Mochizuki and Harumichi Iwamoto and Hayato Ichinose and Takeo Hoshi}
| }



バージョン履歴
--------------------------------

2DMAT-LEED

- v1.0.0: 2024-XX-XX

2DMAT

- v2.1.0 : 2022-04-08
- v2.0.0 : 2022-01-17
- v1.0.1 : 2021-04-15
- v1.0.0 : 2021-03-12
- v0.1.0 : 2021-02-08

主な開発者
--------------------------------
2DMATは以下のメンバーで開発しています.

- v3.0.0 -

  - 本山 裕一 (東京大学 物性研究所)
  - 吉見 一慶 (東京大学 物性研究所)
  - 青山 龍美 (東京大学 物性研究所)
  - 星 健夫　 (核融合科学研究所)

- v2.0.0 -

  - 本山 裕一 (東京大学 物性研究所)
  - 吉見 一慶 (東京大学 物性研究所)
  - 岩本 晴道 (鳥取大学 大学院工学研究科)
  - 星 健夫 (鳥取大学 大学院工学研究科)

- v0.1.0 -

  - 本山 裕一 (東京大学 物性研究所)
  - 吉見 一慶 (東京大学 物性研究所)
  - 星 健夫 (鳥取大学 大学院工学研究科)
