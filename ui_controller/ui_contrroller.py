from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

import os
from copy_controller.copy_controller import CopyController

class CopyThread(QThread):
    update_progress = pyqtSignal(int, str) 
    finished = pyqtSignal() 

    def __init__(self, target_list, destination, parent=None):
        super(CopyThread, self).__init__(parent)
        self.target_list = target_list
        self.destination = destination
        self.copy_controller = CopyController('test_bkp')

    def run(self):
        portion = 1 / len(self.target_list)
        portion = int(portion * 1000)
        currentval = 0
        for index, item_path in enumerate(self.target_list):
            self.update_progress.emit(currentval, f"Copying: {item_path}")
            if os.path.isfile(item_path):
                self.copy_controller.file_copy(item_path, self.destination)
            elif os.path.isdir(item_path):
                self.copy_controller.folder_copy(item_path, self.destination)
            currentval += portion
            self.update_progress.emit(currentval, f"Copying: {item_path}")
        self.update_progress.emit(currentval, f"Copying: {item_path}")
        self.finished.emit()

class UiController:
    def __init__(self):
        Form, Window = uic.loadUiType("ui/file_backup.ui")
        self.app = QApplication([])
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)

        self.form.BrowseDestButton.clicked.connect(self.on_browse_dest_click)
        self.form.AddPathButton.clicked.connect(self.on_browse_add_click)
        self.form.AddPathButton.setEnabled(False)
        self.form.AddFileButton.clicked.connect(self.on_add_file_click)
        self.form.AddFileButton.setEnabled(False)
        self.form.TargetList.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.form.StartCopyButton.clicked.connect(self.on_start_click)
        self.form.StartCopyButton.setEnabled(False)
        self.form.DestinatioEdit.setText("")
        self.form.DestinatioEdit.setReadOnly(True)
        self.form.CancelButton.hide()
    
    def start(self) :
        self.window.show()
        self.app.exec_()

    def on_browse_dest_click(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_path:
            self.form.DestinatioEdit.setText(folder_path)
            self.form.AddPathButton.setEnabled(True)
            self.form.AddFileButton.setEnabled(True)
            self.form.StatusLabel.setText("waiting for sources")

    def on_browse_add_click(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_path:
            self.form.TargetList.addItem(folder_path)
            self.form.StartCopyButton.setEnabled(True)
            self.form.StatusLabel.setText("ready")
            

    def on_add_file_click(self):
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Files", "", "All Files (*)")
        if file_paths:
           for file_path in file_paths:
                self.form.TargetList.addItem(file_path)
                self.form.StartCopyButton.setEnabled(True)
                self.form.StatusLabel.setText("ready")
    
    def on_item_double_clicked(self, item):
        row = self.form.TargetList.row(item)
        self.form.TargetList.takeItem(row)
        if self.form.TargetList.count() == 0:
            self.form.StartCopyButton.setEnabled(False)
            self.form.StatusLabel.setText("waiting for sources")
    
    def on_start_click(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Once the copy process Starts, the UI will be frozen until the process is finished, and IT CANNOT BE STOPPED, it is recommended to ovid copying files bigger than 500Mb. Do you still want to continue?")
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msgBox.exec_() 
        if result == QMessageBox.Ok:
            self.on_start_accept_click()

    def on_start_accept_click(self):
        try:
            self.disable_ui_elements() 
            self.form.progressBar.setValue(0)
            self.form.progressBar.setMinimum(0)
            

            target_list = [self.form.TargetList.item(index).text() for index in range(self.form.TargetList.count())]
            destination = self.form.DestinatioEdit.text()
            portion = 1 / len(target_list)
            portion = int(portion * 1000)
            self.form.progressBar.setMaximum(portion * len(target_list))
            self.copy_thread = CopyThread(target_list, destination)
            self.copy_thread.update_progress.connect(self.update_progress_ui)
            self.copy_thread.finished.connect(self.copy_finished)
            self.copy_thread.start()
        except Exception as e:
            self.enable_ui_elements() 
            self.form.StatusLabel.setText("Error!")
            self.show_error_message(str(e))

    def disable_ui_elements(self):
        self.form.BrowseDestButton.setEnabled(False)
        self.form.AddPathButton.setEnabled(False)
        self.form.AddFileButton.setEnabled(False)
        self.form.StartCopyButton.setEnabled(False)
        self.form.TargetList.setEnabled(False)

    def enable_ui_elements(self):
        self.form.BrowseDestButton.setEnabled(True)
        self.form.AddPathButton.setEnabled(True)
        self.form.AddFileButton.setEnabled(True)
        self.form.StartCopyButton.setEnabled(True)
        self.form.TargetList.setEnabled(True)

    def update_progress_ui(self, value, status):
        self.form.progressBar.setValue(value)
        self.form.StatusLabel.setText(status)

    def copy_finished(self):
        self.enable_ui_elements()
        self.form.StatusLabel.setText("Done!")

    def show_error_message(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(message)
        msgBox.setWindowTitle("Error while copying")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
