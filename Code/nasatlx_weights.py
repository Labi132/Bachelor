import sys
import csv
import os
from PyQt5 import QtWidgets, uic

UI_FILE = '/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/questionnaires/nasa-tlx_weighted.ui'
LOG_DIRECTORY = '/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/log/'

class WeightedTLX(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()
        self.pid = 00# sys.argv[1]
        self.task_type = 00# sys.argv[2]
        self.time_demand = 0
        self.mental_demand = 0
        self.physical_demand = 0
        self.performance = 0
        self.effort = 0
        self.frustration = 0
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi(UI_FILE, self)
        # self.showFullScreen()
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.on_finished)
        self.show()


    def on_finished(self):
        self.read_sliders()
        self.write_to_csv()

    def write_to_csv(self):
        if not os.path.exists(LOG_DIRECTORY):
            os.makedirs(LOG_DIRECTORY)

        file_exists = os.path.exists(LOG_DIRECTORY + 'tlx_participant_' + str(self.pid) + '_weights.csv')

        with open(LOG_DIRECTORY + 'tlx_participant_' + str(self.pid) + '_weights.csv', mode='a+') as file:
            writer = csv.writer(file, delimiter=',')

            if not file_exists:
                print("writi")
                writer.writerow(['participant_id',
                                 'trial',
                                 'mental_demand_weight',
                                 'physical_demand_weight',
                                 'temporal_demand_weight'
                                 'performance_weight',
                                 'effort_weight',
                                 'frustration_weight'])

            writer.writerow([self.pid,
                             self.task_type,
                             self.mental_demand,
                             self.physical_demand,
                             self.time_demand,
                             self.performance,
                             self.effort,
                             self.frustration])

    def read_sliders(self):
        if self.ui.effort_performance.value() == 0:
            self.effort += 1
        else:
            self.performance += 1

        if self.ui.effort_physical.value() == 0:
            self.effort += 1
        else:
            self.physical_demand += 1

        if self.ui.frustration_effort.value() == 0:
            self.frustration += 1
        else:
            self.effort += 1

        if self.ui.frustration_mental.value() == 0:
            self.frustration += 1
        else:
            self.mental_demand += 1

        if self.ui.mental_effort.value() == 0:
            self.mental_demand += 1
        else:
            self.effort += 1

        if self.ui.mental_physical.value() == 0:
            self.mental_demand += 1
        else:
            self.physical_demand += 1

        if self.ui.performance_frustration.value() == 0:
            self.performance += 1
        else:
            self.frustration += 1

        if self.ui.performance_mental.value() == 0:
            self.performance += 1
        else:
            self.mental_demand += 1

        if self.ui.performance_time.value() == 0:
            self.performance += 1
        else:
            self.time_demand += 1

        if self.ui.physical_frustration.value() == 0:
            self.physical_demand += 1
        else:
            self.frustration += 1

        if self.ui.physical_performance.value() == 0:
            self.physical_demand += 1
        else:
            self.performance += 1

        if self.ui.physical_time.value() == 0:
            self.physical_demand += 1
        else:
            self.time_demand += 1

        if self.ui.time_effort.value() == 0:
            self.time_demand += 1
        else:
            self.effort += 1

        if self.ui.time_frustration.value() == 0:
            self.time_demand += 1
        else:
            self.frustration += 1

        if self.ui.time_mental.value() == 0:
            self.time_demand += 1
        else:
            self.mental_demand += 1


def main():
    app = QtWidgets.QApplication(sys.argv)
    weights = WeightedTLX()
    sys.exit(app.exec_())



