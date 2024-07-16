.. 2dmat documentation master file, created by
   sphinx-quickstart on Tue May 26 18:44:52 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

チュートリアル
==================================

2DMAT-SXRD は ``sxrdcalc`` を用いる順問題ソルバーで、原子位置 :math:`x` や原子の占有率、デバイワラー因子から Rocking curve を計算し、実験で得られた Rocking curve からの誤差を :math:`f(x)` として返します。

このチュートリアルでは、Nelder-Mead法を用いて SXRD データ解析を行う例を示します。
以下では、2DMAT-SXRD に付属の ``py2dmat-sxrd`` プログラムを利用し、TOML形式のパラメータファイルを入力として解析を行います。
次に、ユーザープログラムの項では、メインプログラムを自分で作成して使う方法を説明します。

.. toctree::
   :maxdepth: 1

   minsearch
   user_program
