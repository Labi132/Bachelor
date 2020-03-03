#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
from PyQt5 import QtWidgets, uic
import os

UI_FILE = '/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/questionnaires/nasa-tlx.ui'
LOG_DIRECTORY = '/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/log/'


class NasaTLX(QtWidgets.QWizard):

    #id_prob = -1
    #id_trial = -1


    def __init__(self):
        super().__init__()

        # Collect and storeArguments passed to the script
        self.id_prob = sys.argv[1]
        self.id_trial = sys.argv[2]

        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi(UI_FILE, self)

        # Stylesheet for custom slider design
        self.ui.setStyleSheet("""
                .QSlider {
                    min-height: 68px;
                    max-height: 68px;
                    padding-left: 10px;
                    padding-right: 10px;
                }

                .QSlider::groove:horizontal {
                    height: 0px;
                    background: #000000;
                }

                .QSlider::handle:horizontal {
                    background: #22B14C;
                    border: 5px solid #B5E61D;
                    width: 10px;
                    height: 50px;
                    margin: -10px -10px;
                }
                """)

        self.showFullScreen()

        # Only show an back button on page 2 (ID 1)
        if QtWidgets.QWizard.currentId(self) is not 1:
            self.button(QtWidgets.QWizard.BackButton).hide()
        else:
            self.button(QtWidgets.QWizard.BackButton).show()

        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.on_finished)

        self.show()

    def on_finished(self):
        #print(self.ui.slider_mental.value())
        #print(self.ui.slider_physical.value())
        #print(self.ui.slider_temporal.value())
        #print(self.ui.slider_performance.value())
        #print(self.ui.slider_effort.value())
        #print(self.ui.slider_frustration.value())

        self.write_to_csv()

    def write_to_csv(self):
        if not os.path.exists(LOG_DIRECTORY):
            os.makedirs(LOG_DIRECTORY)

        file_exists = os.path.exists(LOG_DIRECTORY + 'tlx_participant_' + str(self.id_prob) + '.csv')

        with open(LOG_DIRECTORY + 'tlx_participant_' + str(self.id_prob) + '.csv', mode='a+') as file:
            writer = csv.writer(file, delimiter=',')

            if not file_exists:
                print("writi")
                writer.writerow(['participant_id',
                                 'trial',
                                 'mental_demand',
                                 'physical_demand',
                                 'temporal_demand',
                                 'performance',
                                 'effort',
                                 'frustration'])

            writer.writerow([self.id_prob,
                             self.id_trial,
                             round(self.ui.slider_mental.value() / 5),  # Divide by 5 to get from 0-100 to 0-20
                             round(self.ui.slider_physical.value() / 5),
                             round(self.ui.slider_temporal.value() / 5),
                             round(self.ui.slider_performance.value() / 5),
                             round(self.ui.slider_effort.value() / 5),
                             round(self.ui.slider_frustration.value() / 5)])


def main():
    app = QtWidgets.QApplication(sys.argv)
    nasaTLX = NasaTLX()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
