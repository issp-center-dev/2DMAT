はじめに
=====================

2DMATとは
----------------------

2DMATは，与えられた順問題ソルバーに対して探索アルゴリズムを適用して最適解を探すためのフレームワークです.
標準的な順問題ソルバーとしては2次元物質構造解析向け実験データ解析ソフトウェアを用い,
原子位置やシミュレーションのパラメータとした場合の実験データとのずれを損失関数として定義します.
この損失関数を最小化するアルゴリズムを適用することで, 原子位置やシミュレーションのパラメータを推定します.
現バージョンでは、量子ビーム回折実験の全反射高速陽電子回折実験（Total-reflection high-energy positron diffraction ,TRHEPD，トレプト）[1]に対応しています[2].
また, 探索アルゴリズムとして, Nelder-Mead法[3], グリッド型探索法[4], ベイズ最適化[5], レプリカ交換モンテカルロ法[6]を実装しています. 
なお, ユーザが損失関数を適切に定義することで任意のソルバーに適用可能です.  

[1] レビューとして， Y．Fukaya, et al., J. Phys. D: Appl. Phys. 52, 013002 (2019); 
兵頭俊夫，「全反射高速陽電子回折　(TRHEPD)による表面構造解析」，固体物理 53, 705 (2018).
[2] 順問題ルーチンは, 東北大学 花田貴によって開発されたコードに基づき作成しています. `T. Hanada, H. Daimon, and S. Ino, Phys. Rev. B 51, 13320 (1995). <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.51.13320>`_
[3] `K. Tanaka, T. Hoshi, I. Mochizuki, T. Hanada, A. Ichimiya, and T. Hyodo, Acta. Phys. Pol. A 137, 188 (2020). <http://przyrbwn.icm.edu.pl/APP/PDF/137/app137z2p25.pdf>`_
[4] `K. Tanaka, I. Mochizuki, T. Hanada, A. Ichimiya, T. Hyodo, and T. Hoshi, JJAP Conf. Series, in press, arXiv:2002.12165. <https://arxiv.org/abs/2002.12165>`_
[5] ベイズ最適化には, `PHYSBO <https://www.pasums.issp.u-tokyo.ac.jp/physbo>`_ を用いてます.
[6] `K. Hukushima and K. Nemoto, J. Phys. Soc. Japan, 65, 1604 (1996). <https://journals.jps.jp/doi/10.1143/JPSJ.65.1604>`_  `R. Swendsen and J. Wang, Phys. Rev. Lett. 57, 2607 (1986). <https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.57.2607>`_ .


ライセンス
----------------------
| 本ソフトウェアのプログラムパッケージおよびソースコード一式はGNU
  General Public License version 3（GPL v3）に準じて配布されています。

Copyright (c) <2020-> The University of Tokyo. All rights reserved.

本ソフトウェアは2020年度 東京大学物性研究所 ソフトウェア高度化プロジェクトの支援を受け開発されました。

バージョン履歴
----------------------

- ver.0.1 : 2021/01/27.


主な開発者
----------------------
2DMATは以下のメンバーで開発しています.

- ver. 0.1

  - 本山 裕一 (東京大学 物性研究所)
  - 吉見 一慶 (東京大学 物性研究所)
  - 星 健夫 (鳥取大学 大学院工学研究科)
