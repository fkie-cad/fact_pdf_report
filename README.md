# FACT PDF report

[![Build Status](https://travis-ci.org/fkie-cad/fact_pdf_report.svg?branch=master)](https://travis-ci.org/fkie-cad/fact_pdf_report)

This repository is the home of the PDF report feature of [FACT](https://github.com/fkie-cad/FACT_core). It is integrated in FACT as a docker container. The report generation follows a simple calling convention based on a folder containing the input data - two json files - and a folder containing the output file - the finished pdf. All temporary data is stored inside the container and removed on the containers removal.

Though this tool can be used standalone, it is highly encouraged to use it from FACT, since the tool is completely integrated in FACT and standalone use would need a manual recreation of the input data. There is no documentation on how to do this.

We haven't yet come around on writing documentation for this tool. So if you have questions just open an issue or connect via the FACT [gitter channel](https://gitter.im/FACT_core/community).
