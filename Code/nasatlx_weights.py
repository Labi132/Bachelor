import sys
import csv
import os
# from PyQt5 import QtWidgets, uic

LOG_DIRECTORY = '/home/lab/Desktop/Eder-Bachelor/Bachelor/Code/log/'

class WeightedTLX():
    def __init__(self):
        self.pid = sys.argv[1]
        self.task_type = sys.argv[2]
        self.time_demand = 0
        self.mental_demand = 0
        self.physical_demand = 0
        self.performance = 0
        self.effort = 0
        self.frustration = 0


    def on_click(self):
        # get button type/name
        self.increment_counter() # übergib button/buttonname
        # next

    def increment_counter(self, type):
        if type == "time":
            self.time_demand += 1
        if type == "mental":
            self.mental_demand += 1
        if type == "physical":
            self.physical_demand += 1
        if type == "performance":
            self.performance += 1
        if type == "effort":
            self.effort += 1
        if type == "frustration":
            self.frustration += 1

    def on_finish(self):
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

    def selection(self, item1, item2):
        msg = "Bitte wählen Sie aus welcher Aspekt für die Duchrführung der Aufgabe am bedeutsamsten war. "
        msg += item1 + "(1) oder "
        msg += item2 + "(2)."
        s = input(msg)
        if s == "1":
            return item1
        if s == "2":
            return item2
        else:
            return self.selection(item1, item2)


def main():
    weights = WeightedTLX()
    weights.increment_counter(weights.selection("effort", "performance"))
    weights.increment_counter(weights.selection("time", "effort"))
    weights.increment_counter(weights.selection("performance", "frustration"))
    weights.increment_counter(weights.selection("physical", "performance"))
    weights.increment_counter(weights.selection("time", "frustration"))
    weights.increment_counter(weights.selection("physical", "frustration"))
    weights.increment_counter(weights.selection("physical", "time"))
    weights.increment_counter(weights.selection("time", "mental"))
    weights.increment_counter(weights.selection("frustration", "effort"))
    weights.increment_counter(weights.selection("performance", "mental"))
    weights.increment_counter(weights.selection("performance", "time"))
    weights.increment_counter(weights.selection("mental", "effort"))
    weights.increment_counter(weights.selection("mental", "physical"))
    weights.increment_counter(weights.selection("effort", "physical"))
    weights.increment_counter(weights.selection("frustration", "mental"))
    weights.on_finish()




main()
