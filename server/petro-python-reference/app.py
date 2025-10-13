import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
    
    # #well  = found_well[0]
    #     #for dtst in found_well.datasets[:]:  # Iterate over a copy of the list
    #         if dtst.name == dtst_name:
    #             for wl in dtst.well_logs[:]:
    #                 if wl.name==log_name:
    #                     dtst.well_logs.remove(wl)
